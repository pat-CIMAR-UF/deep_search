# Deep Search API（已实现）

服务地址：`http://localhost:8000`。`uv run main.py` 同时提供前端、HTTP API 和 WebSocket。
开发模式由 Vite 代理 `/api` 和 `/ws`，前端不使用硬编码主机地址。

这是本机单用户应用，运行一个服务进程。`thread_id` 隔离会话，不代表账户认证。
允许字母、数字、下划线和连字符，长度 1–80。默认生成 UUID。
主智能体使用 DeepAgents 流式执行，协调数据库查询（MongoDB，经 mongodb-mcp-server 只读访问）、互联网搜索和 RAGFlow 知识库三个子智能体。

## 启动任务

`POST /api/task`，JSON：

```json
{
  "query": "按地区统计销售额",
  "thread_id": "your-session-id",
  "mode": "database",
  "attachments": []
}
```

- `query`：必填，非空，最多 20,000 字符。
- `thread_id`：可选。同一 ID 保留对话上下文。
- `mode`：`auto`（默认，三个智能体协调）、`database`、`internet` 或 `ragflow`。
- `attachments`：上传接口返回的会话内相对路径，最多 5 个。文本作为参考数据传入模型；PDF、Word、Excel 通过文件读取工具解析。

成功返回 HTTP 202：`{"status":"started","thread_id":"...","run_id":"..."}`。
同一会话已有任务时返回 409。任务最多运行 5 分钟。

## 状态、历史与取消

- `GET /api/task/{thread_id}`：获取最新会话快照，支持断线恢复和轮询。
- `POST /api/task/{thread_id}/cancel`：取消当前任务，返回更新后的快照。
- `GET /api/health`：返回 `{"status":"ok","agents":["database","internet","ragflow"],"ragflow":true}`。
  此接口表示应用就绪；实际服务连通性在请求时验证。

快照包含 `thread_id`、`run_id`、单调递增 `revision`、`status`、`messages`。
状态为 `idle`、`running`、`completed`、`error`、`cancelled`。
消息包含 `role`（`user`/`ai`）、`content`、可选 `logs`、`files`、`attachments`、`failed`。
失败和取消也有终态消息，不会让 UI 一直等待。
取消后的底层只读请求可能继续完成，但迟到事件不会污染新任务。

## WebSocket

`/ws/{thread_id}`。连接成功和每次工具/智能体活动、任务终止时推送完整快照：

```json
{"type":"snapshot","data":{"thread_id":"...","run_id":"...","revision":3,"status":"running","messages":[]}}
```

前端只采用当前会话、最新版本的快照。工具原有 `tool_start`、`assistant_call` 事件
由服务端汇入当前 AI 消息的 `logs`。客户端发送任意文本，收到 `{"type":"pong"}`。
前端每 3 秒轮询一次状态，断线后每 3 秒重连；刷新页面恢复当前会话。

## 文件上传

`POST /api/upload`，`multipart/form-data` 字段：`thread_id`、`files`（1–5 个）。
浏览器自动设置 multipart boundary，不要手动设置 Content-Type。

支持 UTF-8 TXT、MD、CSV、TSV、JSON、LOG、SQL。每个文件不超过 64 KB，
文本总内容小于 99,000 字节。另支持 PDF、Word (.docx)、Excel (.xlsx/.xls)，每个不超过 10 MB。
不进行知识库入库。

成功响应：`{"status":"uploaded","files":["uploads/unique_notes.txt"]}`。
文件类型或编码不支持返回 415；超过大小限制返回 413。上传失败不提交聊天任务。

## 文件列表与下载

- `GET /api/files?thread_id=...` 返回 `{"files":[{"name":"...","path":"...","size":123,"mtime":0,"type":"file"}]}`。
  按修改时间倒序排列，`path` 为会话内相对路径。
- `GET /api/download?thread_id=...&path=...` 下载指定文件。
  路径必须属于当前会话，越界路径、指向会话外的符号链接和隐藏状态文件返回 403。

每次成功回答自动保存为 `answer_<timestamp>_<id>.md`。本次生成的 Markdown/PDF 报告也会包含在消息的 `files` 中。
会话历史、上传文本和报告保存在忽略版本控制的 `output/session_<thread_id>/`。
服务器重启后恢复历史；重启时尚未结束的请求标记为失败，可重新提问。

## 错误格式

HTTP 错误使用 FastAPI 的 `{"detail":"说明"}`（字段校验错误为数组）。
智能体执行错误写入会话快照。原始供应商错误和密钥不会返回浏览器。
