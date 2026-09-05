<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import axios from 'axios'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

interface LogItem { title: string; details: unknown; timestamp?: string }
interface FileItem { name: string; path: string; size?: number }
interface Message {
  role: 'user' | 'ai'; content: string; logs?: LogItem[]; files?: FileItem[];
  attachments?: string[]; failed?: boolean
}
interface Snapshot {
  thread_id: string; status: 'idle' | 'running' | 'completed' | 'error' | 'cancelled';
  messages: Message[]; run_id: string | null; revision: number
}
const api = axios.create({ timeout: 15000 })
const inputQuery = ref('')
const messages = ref<Message[]>([])
const status = ref<Snapshot['status']>('idle')
const submitting = ref(false)
const cancelling = ref(false)
const busy = computed(() => submitting.value || status.value === 'running')
const agentMode = ref<'auto' | 'database' | 'internet'>('auto')
const connected = ref(false)
const errorMessage = ref('')
const connectionError = ref('')
const fileError = ref('')
const messagesEndRef = ref<HTMLElement | null>(null)
const isWelcomeScreen = computed(() => messages.value.length === 0)
const isSidebarOpen = ref(false)
const fileList = ref<FileItem[]>([])
const loadingFiles = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])
const currentThreadId = ref(readThreadId())
let socket: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | undefined
let pollTimer: ReturnType<typeof setInterval> | undefined
let heartbeatTimer: ReturnType<typeof setInterval> | undefined
let disposed = false
let revision = -1
let polling = false

function readThreadId(): string {
  try {
    const saved = localStorage.getItem('deep-search-thread')
    if (saved && /^[A-Za-z0-9_-]{1,80}$/.test(saved)) return saved
  } catch { /* Storage may be disabled in private browser contexts. */ }
  return crypto.randomUUID()
}
function saveThreadId() {
  try { localStorage.setItem('deep-search-thread', currentThreadId.value) } catch { /* optional */ }
}
const scrollToBottom = async () => {
  await nextTick()
  messagesEndRef.value?.scrollIntoView({ behavior: 'smooth', block: 'end' })
}
function downloadUrl(file: FileItem) {
  return `/api/download?${new URLSearchParams({ thread_id: currentThreadId.value, path: file.path })}`
}
function describeError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map(item => item.msg).join(' ')
    if (!error.response) return 'Cannot reach the backend. Check that it is running, then retry.'
  }
  return 'The request failed. Please try again.'
}
const fetchFiles = async () => {
  const thread = currentThreadId.value
  loadingFiles.value = true
  try {
    const { data } = await api.get('/api/files', { params: { thread_id: thread } })
    if (thread === currentThreadId.value) { fileList.value = data.files; fileError.value = '' }
  } catch (error) {
    if (thread === currentThreadId.value) fileError.value = describeError(error)
  } finally { if (thread === currentThreadId.value) loadingFiles.value = false }
}
function applySnapshot(data: Snapshot) {
  if (data.thread_id !== currentThreadId.value || submitting.value || data.revision < revision) return
  const changed = data.revision > revision
  const finished = status.value === 'running' && data.status !== 'running'
  revision = data.revision
  messages.value = data.messages
  status.value = data.status
  if (finished) void fetchFiles()
  if (changed) void scrollToBottom()
}
async function syncState() {
  if (polling || disposed) return
  polling = true
  const thread = currentThreadId.value
  try {
    const { data } = await api.get<Snapshot>(`/api/task/${thread}`)
    if (thread === currentThreadId.value) { applySnapshot(data); connectionError.value = '' }
  } catch (error) {
    if (thread === currentThreadId.value) connectionError.value = describeError(error)
  } finally { polling = false }
}
function connectWebSocket() {
  if (disposed) return
  const thread = currentThreadId.value
  const url = new URL(`/ws/${thread}`, location.href)
  url.protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const ws = new WebSocket(url)
  socket = ws
  ws.onopen = () => { if (socket === ws) { connected.value = true; void syncState() } }
  ws.onmessage = ({ data }) => {
    if (socket !== ws) return
    try {
      const payload = JSON.parse(data)
      if (payload.type === 'snapshot') applySnapshot(payload.data)
    } catch { /* The polling endpoint remains authoritative if an event is malformed. */ }
  }
  ws.onerror = () => ws.close()
  ws.onclose = () => {
    if (socket !== ws || disposed) return
    connected.value = false
    reconnectTimer = setTimeout(connectWebSocket, 3000)
  }
}
function closeSocket() {
  clearTimeout(reconnectTimer)
  const previous = socket
  socket = null
  previous?.close()
  connected.value = false
}
async function newChat() {
  if (busy.value) return
  closeSocket()
  currentThreadId.value = crypto.randomUUID()
  saveThreadId()
  revision = -1
  messages.value = []; fileList.value = []; selectedFiles.value = []
  status.value = 'idle'; inputQuery.value = ''; errorMessage.value = ''; fileError.value = ''
  connectionError.value = ''
  isSidebarOpen.value = false
  connectWebSocket()
  await syncState()
}
async function sendMessage() {
  const query = inputQuery.value.trim()
  if (!query || busy.value) return
  errorMessage.value = ''
  submitting.value = true
  try {
    let attachments: string[] = []
    if (selectedFiles.value.length) {
      const form = new FormData()
      form.append('thread_id', currentThreadId.value)
      selectedFiles.value.forEach(file => form.append('files', file))
      const { data } = await api.post('/api/upload', form)
      attachments = data.files
    }
    await api.post('/api/task', { query, thread_id: currentThreadId.value, mode: agentMode.value, attachments })
    inputQuery.value = ''
    selectedFiles.value = []
    status.value = 'running'
    submitting.value = false
    await syncState()
    void fetchFiles()
  } catch (error) {
    errorMessage.value = describeError(error)
    // A timed-out POST may still have started a task. Reconcile before enabling another submission.
    submitting.value = false
    try {
      const { data } = await api.get<Snapshot>(`/api/task/${currentThreadId.value}`)
      applySnapshot(data)
    } catch { /* Keep the draft and explain the connection failure. */ }
  } finally { submitting.value = false }
}
async function stopTask() {
  if (submitting.value || cancelling.value) return
  cancelling.value = true
  try {
    const { data } = await api.post<Snapshot>(`/api/task/${currentThreadId.value}/cancel`)
    applySnapshot(data)
  } catch (error) { errorMessage.value = describeError(error) }
  finally { cancelling.value = false }
}
function handleEnter(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    void sendMessage()
  }
}
const triggerFileUpload = () => fileInputRef.value?.click()
function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const files = [...selectedFiles.value, ...Array.from(target.files ?? [])]
  target.value = ''
  if (files.length > 5 || files.some(file => file.size > 65536 || !/\.(txt|md|csv|tsv|json|log|sql)$/i.test(file.name))) {
    errorMessage.value = 'Attach up to five UTF-8 text files, each 64 KB or smaller (TXT, MD, CSV, TSV, JSON, LOG, SQL).'
    return
  }
  selectedFiles.value = files
  errorMessage.value = ''
}
const removeFile = (index: number) => selectedFiles.value.splice(index, 1)
const renderMarkdown = (text: string) => DOMPurify.sanitize(marked.parse(text, { async: false }))
onMounted(() => {
  saveThreadId()
  connectWebSocket()
  void syncState()
  void fetchFiles()
  pollTimer = setInterval(() => void syncState(), 3000)
  heartbeatTimer = setInterval(() => { if (socket?.readyState === WebSocket.OPEN) socket.send('ping') }, 20000)
})
onUnmounted(() => {
  disposed = true
  closeSocket()
  clearInterval(pollTimer)
  clearInterval(heartbeatTimer)
})
</script>

<template>
  <div class="app-container">
    <!-- Main Content -->
    <main class="main-content" :class="{ 'centered-layout': isWelcomeScreen }">

      <header class="app-toolbar">
        <strong>Deep Search</strong>
        <span class="connection-status" :class="{ online: connected }">{{ connected ? 'Live updates connected' : 'Reconnecting · polling for updates' }}</span>
        <button class="folder-btn" @click="newChat" :disabled="busy">New chat</button>
      </header>
      <!-- Sidebar Toggle Button -->
      <button
        v-if="!isWelcomeScreen && !isSidebarOpen"
        class="sidebar-toggle-btn"
        @click="isSidebarOpen = true"
        title="Open File Sidebar"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- Welcome Screen -->
      <div v-if="isWelcomeScreen" class="welcome-screen">
        <div class="welcome-text">
          <h1>Deep Search</h1>
          <h2>What would you like to explore?</h2><p class="welcome-description">Query company data, search the internet, or combine both.</p>
        </div>
      </div>

      <!-- Chat Area -->
      <div v-else class="chat-scroll-area">
        <div class="chat-container">
          <div v-for="(msg, index) in messages" :key="index" class="message-wrapper" :class="msg.role">

            <!-- User Message -->
            <div v-if="msg.role === 'user'" class="message-user">
              <div class="msg-content">{{ msg.content }}<div v-if="msg.attachments?.length" class="attachment-names">{{ msg.attachments.map(path => path.split('/').pop()?.replace(/^[a-f0-9]{8}_/, '')).join(', ') }}</div></div>
            </div>

            <!-- AI Message -->
            <div v-else-if="msg.role === 'ai'" class="message-ai">
              <div class="ai-avatar">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="url(#grad1)"/>
                  <defs>
                    <linearGradient id="grad1" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#4E75F6"/>
                      <stop offset="1" stop-color="#E3557A"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>

              <div class="ai-content-wrapper">
                <!-- Logs / Thinking Process -->
                <div v-if="msg.logs && msg.logs.length > 0" class="process-section">
                  <details>
                    <summary>
                      <span class="spinner" v-if="busy && index === messages.length - 1"></span>
                      View agent activity
                    </summary>
                    <div class="process-steps">
                      <div v-for="(log, idx) in msg.logs" :key="idx" class="step-item">
                        <div class="step-header">
                          <span class="step-icon">🔧</span>
                          <span class="step-title">{{ log.title }}</span>
                        </div>
                        <div class="step-details" v-if="log.details">
                           <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
                        </div>
                      </div>
                    </div>
                  </details>
                </div>

                <!-- Text Content -->
                <div v-if="!msg.content && busy && index === messages.length - 1" class="typing-indicator" role="status">Working on your request…</div>
                <div class="markdown-body" :class="{ 'failed-answer': msg.failed }" v-html="renderMarkdown(msg.content)"></div>

                <!-- Files -->
                <div v-if="msg.files && msg.files.length > 0" class="files-grid">
                  <a v-for="file in msg.files" :key="file.name" :href="downloadUrl(file)" class="file-card" :download="file.name">
                    <div class="file-icon">📄</div>
                    <div class="file-info">
                      <div class="file-name">{{ file.name }}</div>
                      <div class="file-type">Document</div>
                    </div>
                  </a>
                </div>
              </div>
            </div>

            <!-- System Message -->
             <div v-else class="message-system">
              {{ msg.content }}
            </div>

          </div>
          <div ref="messagesEndRef" class="spacer-bottom"></div>
        </div>
      </div>

      <!-- Input Area -->
      <footer class="input-footer">
        <div v-if="errorMessage || connectionError" class="error-banner" role="alert">{{ errorMessage || connectionError }} <button v-if="connectionError" class="folder-btn" @click="syncState">Retry connection</button></div>
        <div class="composer-options">
          <label for="agent-mode">Agent</label>
          <select id="agent-mode" v-model="agentMode" :disabled="busy">
            <option value="auto">Auto · both agents</option>
            <option value="database">Database query</option>
            <option value="internet">Internet search</option>
          </select>
          <span>Read-only database · public web search</span>
        </div>
        <!-- File Preview Tab -->
        <div v-if="selectedFiles.length > 0" class="file-preview-container">
          <div v-for="(file, index) in selectedFiles" :key="index" class="file-preview-chip">
            <span class="file-preview-icon">📎</span>
            <span class="file-preview-name">{{ file.name }}</span>
            <button class="file-remove-btn" @click="removeFile(index)" :disabled="busy" title="Remove file" aria-label="Remove file">×</button>
          </div>
        </div>

        <div class="input-container" :class="{ focused: busy }">
          <input
            type="file"
            ref="fileInputRef"
            multiple
            accept=".txt,.md,.csv,.tsv,.json,.log,.sql"
            style="display: none"
            @change="handleFileChange"
          />
          <button class="upload-btn" @click="triggerFileUpload" :disabled="busy" title="Attach UTF-8 text (up to 64 KB per file)" aria-label="Attach text files">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <textarea
            v-model="inputQuery"
            @keydown="handleEnter"
            placeholder="Ask about company data or the web…" aria-label="Your question"
            :disabled="busy"
          ></textarea>
          <button class="send-btn" @click="busy ? stopTask() : sendMessage()" :disabled="submitting || cancelling || (!busy && !inputQuery.trim())" :aria-label="busy ? 'Stop request' : 'Send message'" :title="busy ? 'Stop request' : 'Send message'">
            <span v-if="busy" class="stop-icon">■</span>
            <svg v-if="!busy" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
            </svg>
          </button>
        </div>
        <div class="footer-text">
          Shift + Enter for a new line · Attach UTF-8 text files, up to 64 KB each · Answers save as Markdown
        </div>
      </footer>
    </main>

    <!-- Right Sidebar (File Explorer) -->
    <aside v-if="isSidebarOpen" class="file-sidebar">
      <div class="sidebar-header">
        <h3>Session Files</h3>
        <div style="display: flex; gap: 8px; align-items: center;">
            <button class="folder-btn" @click="fetchFiles" title="Refresh Files" style="padding: 4px 8px;">
                ↻
            </button>
            <button class="close-btn" aria-label="Close files" @click="isSidebarOpen = false">×</button>
        </div>
      </div>
      <div class="file-list">
        <div v-if="fileError" class="error-banner" role="alert">{{ fileError }}</div>
        <div v-if="loadingFiles" class="empty-files" role="status">Loading files…</div>
        <div v-else-if="fileList.length === 0" class="empty-files">
          No files generated yet.
        </div>
        <div v-for="file in fileList" :key="file.path" class="file-item">
          <a :href="downloadUrl(file)" class="file-link" :download="file.name">
            <span class="file-icon">📄</span>
            <span class="file-name-text">{{ file.name }}</span>
          </a>
        </div>
      </div>
    </aside>
  </div>
</template>

<style>
/* Global Resets & Variables */
:root {
  --bg-dark: #131314;
  --surface-dark: #1E1F20;
  --surface-light: #2D2E2F;
  --text-primary: #E3E3E3;
  --text-secondary: #C4C7C5;
  --accent-blue: #A8C7FA;
  --user-msg-bg: #2D2E30; /* Darker gray for user */
  --border-color: #444746;
}

body {
  margin: 0;
  background-color: var(--bg-dark);
  color: var(--text-primary);
  font-family: 'Google Sans', 'Roboto', Helvetica, Arial, sans-serif;
  overflow: hidden; /* App handles scroll */
}

/* Layout */
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  /* justify-content: center; Removed to allow sidebar layout */
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background-color: var(--bg-dark);
  min-width: 0; /* Prevent flex overflow */
}

.sidebar-toggle-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  z-index: 10;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.sidebar-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

/* File Sidebar */
.file-sidebar {
  width: 300px;
  background-color: var(--surface-dark);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: var(--text-primary);
}

.file-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.empty-files {
  color: var(--text-secondary);
  text-align: center;
  font-size: 0.9rem;
  margin-top: 2rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.file-link {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  color: var(--text-primary);
  text-decoration: none;
  transition: background 0.2s;
  border: 1px solid transparent;
}

.file-link:hover {
  background: #2D2E30;
  border-color: #444;
}

.folder-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.folder-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  border-color: var(--text-secondary);
}

.file-name-text {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Welcome Screen */
.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

/* Centered Layout Mode (Initial State) */
.main-content.centered-layout {
  justify-content: center;
  align-items: center;
  overflow-y: auto;
}

.main-content.centered-layout .welcome-screen {
  flex: 0 0 auto;
  padding-bottom: 2rem;
}

.main-content.centered-layout .input-footer {
  width: 100%;
  max-width: 100%;
  padding: 0;
  background: transparent;
  justify-content: center;
}

.welcome-text {
  text-align: center;
  margin-bottom: 2rem;
}

.welcome-text h1 {
  font-size: 3.5rem;
  background: linear-gradient(90deg, #4E75F6, #E3557A);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  line-height: 1.2;
}

.welcome-text h2 {
  font-size: 3.5rem;
  color: #444746;
  margin: 0;
  line-height: 1.2;
}

/* Chat Area */
.chat-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.chat-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* User Message */
.message-user {
  align-self: flex-end;
  max-width: 70%;
}

.msg-content {
  background-color: var(--user-msg-bg);
  padding: 12px 18px;
  border-radius: 18px;
  border-bottom-right-radius: 4px;
  line-height: 1.6;
}

/* AI Message */
.message-ai {
  align-self: flex-start;
  width: 100%;
  display: flex;
  gap: 1rem;
}

.ai-avatar {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  margin-top: 4px;
}

.ai-content-wrapper {
  flex: 1;
  min-width: 0; /* Text wrap fix */
}

.markdown-body {
  line-height: 1.6;
  font-size: 1rem;
}

.markdown-body pre {
  background: #2D2E30;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
}

.typing-indicator {
  color: var(--text-secondary);
  font-style: italic;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

/* Process / Logs */
.process-section {
  margin-bottom: 1rem;
}

.process-section summary {
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 0.85rem;
  list-style: none; /* Hide default arrow */
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
}

.process-section summary:hover {
  background: #2D2E30;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid var(--text-secondary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.process-steps {
  background: #1E1F20;
  border-radius: 8px;
  padding: 0.5rem;
  margin-top: 0.5rem;
  border: 1px solid #333;
}

.step-item {
  padding: 0.5rem;
  border-left: 2px solid #333;
  margin-left: 0.5rem;
  margin-bottom: 0.5rem;
}

.step-header {
  font-size: 0.85rem;
  font-weight: 500;
  color: #E3E3E3;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.step-details pre {
  margin: 0.5rem 0 0 0;
  font-size: 0.75rem;
  color: #999;
  background: #111;
  padding: 0.5rem;
  border-radius: 4px;
  overflow-x: auto;
}

/* Files Grid */
.files-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.file-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #2D2E30;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-primary);
  border: 1px solid #444;
  transition: all 0.2s;
  min-width: 150px;
}

.file-card:hover {
  background: #333537;
  border-color: #666;
}

.file-info {
  display: flex;
  flex-direction: column;
}

.file-name {
  font-weight: 500;
  font-size: 0.9rem;
}

.file-type {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* System Message */
.message-system {
  text-align: center;
  font-size: 0.8rem;
  color: #666;
  margin: 1rem 0;
}

.spacer-bottom { height: 100px; }

/* Input Footer */
.input-footer {
  background: var(--bg-dark); /* Ensure it covers scrolling content */
  padding: 1rem 2rem 2rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.input-container {
  width: 100%;
  max-width: 800px;
  background: #1E1F20;
  border-radius: 32px;
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  transition: background 0.2s;
}

.input-container.focused {
  background: #2D2E30;
}

textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 1rem;
  padding: 10px;
  resize: none;
  height: 24px;
  max-height: 200px;
  font-family: inherit;
  outline: none;
}

.send-btn {
  background: none;
  border: none;
  color: var(--text-primary); /* White when active */
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:disabled {
  color: #444746;
  cursor: default;
}

.send-btn:not(:disabled):hover {
  background: #3c4043;
}

.upload-btn {
  background: none;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 4px;
}

.upload-btn:hover {
  background: #3c4043;
}

.upload-btn:disabled {
  color: #444746;
  cursor: default;
}

.footer-text {
  font-size: 0.75rem;
  color: #444746;
  text-align: center;
}

/* File Preview Styles */
.file-preview-container {
  width: 100%;
  max-width: 800px;
  display: flex;
  justify-content: flex-start;
  padding-left: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.file-preview-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #2D2E30;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #444;
  font-size: 0.9rem;
  color: var(--text-primary);
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.file-preview-icon {
  font-size: 1rem;
}

.file-preview-name {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-remove-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.1rem;
  padding: 0 4px;
  line-height: 1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-remove-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ff6b6b;
}

/* Scrollbar Styles */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #555;
}

* { box-sizing: border-box; }
.app-container { height: 100dvh; }
.app-toolbar { display: flex; gap: 1rem; align-items: center; padding: 1rem 4rem 1rem 1.25rem; width: 100%; }
.centered-layout .app-toolbar { position: absolute; top: 0; }
.connection-status { color: #d8b775; font-size: .75rem; flex: 1; }
.connection-status.online { color: #9bc9a4; }
.welcome-description { color: var(--text-secondary); line-height: 1.6; }
.welcome-text h2 { font-size: clamp(1.5rem, 4vw, 3rem); color: #9aa0a6; }
.welcome-text h1 { font-size: clamp(2.5rem, 5vw, 3.5rem); }
.composer-options { width: 100%; max-width: 800px; display: flex; align-items: center; gap: .75rem; color: var(--text-secondary); font-size: .8rem; flex-wrap: wrap; }
select { background: var(--surface-dark); color: var(--text-primary); border: 1px solid var(--border-color); border-radius: 8px; padding: .5rem; font: inherit; }
.error-banner { width: 100%; max-width: 800px; padding: .7rem; border: 1px solid #b66d6d; color: #ffc3c3; border-radius: 8px; font-size: .85rem; display: flex; gap: .5rem; align-items: center; }
.error-banner .folder-btn { margin-left: auto; white-space: nowrap; }
.main-content.centered-layout .input-footer { padding: 0 1.25rem 1.25rem; }
.chat-scroll-area { min-height: 0; }
.input-footer { flex-shrink: 0; }
textarea { min-width: 0; height: 64px; max-height: 140px; }
.msg-content { white-space: pre-wrap; overflow-wrap: anywhere; }
.attachment-names { font-size: .75rem; opacity: .7; margin-top: .5rem; }
.file-info { min-width: 0; }
.file-name { overflow-wrap: anywhere; }
.file-card { max-width: 100%; }
.markdown-body { overflow-wrap: anywhere; overflow-x: auto; }
.markdown-body table { border-collapse: collapse; display: block; overflow-x: auto; margin: 1rem 0; }
.markdown-body th, .markdown-body td { border: 1px solid var(--border-color); padding: .6rem .8rem; text-align: left; }
.markdown-body th { background: var(--surface-dark); }
.markdown-body a { color: var(--accent-blue); }
.markdown-body code { background: var(--surface-light); padding: .1rem .25rem; border-radius: 4px; }
.failed-answer { color: #ffc3c3; }
.spacer-bottom { height: 16px; }
.footer-text { color: #9aa0a6; }
button:disabled, select:disabled { opacity: .5; cursor: default; }
button:focus-visible, select:focus-visible, textarea:focus-visible { outline: 2px solid var(--accent-blue); outline-offset: 3px; }
@media (max-width: 700px) {
  .app-toolbar { gap: .5rem; padding-left: .75rem; }
  .connection-status { font-size: .65rem; }
  .welcome-screen { padding: 5rem 1rem 1rem; }
  .input-footer { padding: .75rem; }
  .composer-options > span { display: none; }
  .file-sidebar { position: absolute; right: 0; top: 0; bottom: 0; width: min(320px, 90vw); z-index: 20; box-shadow: -12px 0 30px #0008; }
  .message-user { max-width: 90%; }
  .ai-content-wrapper { max-width: 100%; }
}
</style>
