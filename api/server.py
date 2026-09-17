"""Local chat API, replayable progress, and session-scoped files."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from agent.main_agent import run_agent
from api.context import (set_session_context, set_thread_context, reset_session_context,
                         set_run_context, reset_run_context)
from api.monitor import ConnectionManager
from tools.mcp_client import shutdown as shutdown_mongo_mcp

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = Path(os.getenv("DEEP_SEARCH_OUTPUT_DIR", ROOT / "output")).resolve()
TASK_TIMEOUT = 300
TEXT_SUFFIXES = {".txt", ".md", ".csv", ".tsv", ".json", ".log", ".sql"}
DOCUMENT_SUFFIXES = {".pdf", ".docx", ".xlsx", ".xls"}
UPLOAD_SUFFIXES = TEXT_SUFFIXES | DOCUMENT_SUFFIXES
sessions: dict[str, dict] = {}
tasks: dict[str, asyncio.Task] = {}
logger = logging.getLogger(__name__)


def validate_thread(thread_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", thread_id):
        raise HTTPException(422, "Invalid conversation ID.")
    return thread_id


def session_dir(thread_id: str) -> Path:
    directory = (OUTPUT_ROOT / f"session_{validate_thread(thread_id)}").resolve()
    if directory.parent != OUTPUT_ROOT:
        raise HTTPException(403, "Invalid session directory.")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_session(state: dict):
    target = session_dir(state["thread_id"]) / ".state.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    temporary.replace(target)


def get_session(thread_id: str) -> dict:
    validate_thread(thread_id)
    if thread_id not in sessions:
        path = session_dir(thread_id) / ".state.json"
        if path.is_file():
            state = json.loads(path.read_text(encoding="utf-8"))
            state.setdefault("revision", 0)
            if state["status"] == "running":
                state["status"] = "error"
                state["revision"] += 1
                state["messages"][-1]["content"] = "The server restarted during this request. Please try again."
                state["messages"][-1]["failed"] = True
                save_session(state)
        else:
            state = {"thread_id": thread_id, "run_id": None, "status": "idle", "messages": [], "revision": 0}
        sessions[thread_id] = state
    return sessions[thread_id]


def checked_file(thread_id: str, path: str) -> Path:
    directory = session_dir(thread_id)
    candidate = Path(path)
    target = (candidate if candidate.is_absolute() else directory / candidate).resolve()
    if not target.is_relative_to(directory) or any(p.startswith(".") for p in target.relative_to(directory).parts):
        raise HTTPException(403, "Only this conversation's files are accessible.")
    return target


class EventHub(ConnectionManager):
    async def send_to_thread(self, message: dict, thread_id: str):
        state = get_session(thread_id)
        # Late events from cancelled/completed runs must not pollute a newer answer.
        if message.get("run_id") != state["run_id"] or state["status"] != "running":
            return
        if message.get("event") in {"tool_start", "assistant_call"}:
            logs = state["messages"][-1].setdefault("logs", [])
            logs.append({"title": message["message"], "details": message.get("data", {}),
                         "timestamp": message.get("timestamp")})
            del logs[:-100]
        state["revision"] += 1
        await self.snapshot(thread_id)

    async def snapshot(self, thread_id: str):
        websocket = self.active_connections.get(thread_id)
        if websocket:
            try:
                await websocket.send_json({"type": "snapshot", "data": get_session(thread_id)})
            except (WebSocketDisconnect, RuntimeError, OSError):
                self.disconnect(websocket, thread_id)


hub = EventHub()


@asynccontextmanager
async def lifespan(app: FastAPI):
    hub.set_loop(asyncio.get_running_loop())
    yield
    running = list(tasks.values())
    for task in running:
        task.cancel()
    await asyncio.gather(*running, return_exceptions=True)
    hub.active_connections.clear()
    await asyncio.to_thread(shutdown_mongo_mcp)


app = FastAPI(title="Deep Search", lifespan=lifespan)


class TaskRequest(BaseModel):
    query: str = Field(max_length=20000)
    thread_id: str = Field(default_factory=lambda: str(uuid4()))
    mode: Literal["auto", "database", "internet", "ragflow"] = "auto"
    attachments: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("query")
    @classmethod
    def nonempty_query(cls, value):
        if not value.strip():
            raise ValueError("Enter a question.")
        return value.strip()

    @field_validator("thread_id")
    @classmethod
    def safe_thread(cls, value):
        return validate_thread(value)


def public_error(exc: Exception) -> str:
    # Provider errors may contain request URLs/credentials. Never send them to the browser.
    if isinstance(exc, (TimeoutError, asyncio.TimeoutError)):
        return "This request timed out. Try a narrower question or check the model/search service."
    if isinstance(exc, KeyError):
        return "The model is not configured. Check QWEN_REMOTE_BASE_URL and QWEN_REMOTE_API_KEY in .env."
    return "The agent could not complete this request. Check the model, search, database and RAGFlow configuration, then try again."


async def execute_task(request: TaskRequest, query: str, history: list[dict], run_id: str):
    state = get_session(request.thread_id)
    session_token = set_session_context(str(session_dir(request.thread_id)))
    thread_token = set_thread_context(request.thread_id)
    run_token = set_run_context(run_id)
    try:
        before = {f["path"]: (f["mtime"], f["size"]) for f in (await list_files(request.thread_id))["files"]}
        async with asyncio.timeout(TASK_TIMEOUT):
            answer = await run_agent(query, history, request.mode)
        name = f"answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{run_id[:8]}.md"
        (session_dir(request.thread_id) / name).write_text(answer + "\n", encoding="utf-8")
        generated = [f for f in (await list_files(request.thread_id))["files"]
                     if before.get(f["path"]) != (f["mtime"], f["size"]) and not f["path"].startswith("uploads/")]
        state["messages"][-1].update(content=answer, files=generated)
        state["status"] = "completed"
    except asyncio.CancelledError:
        state["status"] = "cancelled"
        state["messages"][-1].update(content="Request stopped.", failed=True)
    except Exception as exc:
        logger.warning("Agent request failed (%s)", type(exc).__name__)
        state["status"] = "error"
        state["messages"][-1].update(content=public_error(exc), failed=True)
    finally:
        state["revision"] += 1
        reset_run_context(run_token)
        reset_session_context(session_token, thread_token)
        tasks.pop(request.thread_id, None)
        save_session(state)
        await hub.snapshot(request.thread_id)


@app.get("/api/health")
async def health():
    return {"status": "ok", "agents": ["database", "internet", "ragflow"], "ragflow": True}


@app.post("/api/task", status_code=202)
async def start_task(request: TaskRequest):
    state = get_session(request.thread_id)
    if request.thread_id in tasks:
        raise HTTPException(409, "This conversation already has a running request.")
    attachments = []
    for name in request.attachments:
        path = checked_file(request.thread_id, name)
        if not path.is_file() or path.suffix.lower() not in UPLOAD_SUFFIXES:
            raise HTTPException(400, "One of the attached files is unavailable.")
        if path.suffix.lower() in TEXT_SUFFIXES:
            content = path.read_text(encoding='utf-8')
        else:
            content = "Read this document using the read_file_content tool."
        attachments.append(f"\n<attachment name={json.dumps(path.name)} path={json.dumps(name)}>\n{content}\n</attachment>")
    if sum(len(part) for part in attachments) > 100000:
        raise HTTPException(413, "Attachments must contain at most 100,000 characters in total.")
    history = [{"role": "assistant" if m["role"] == "ai" else "user", "content": m.get("agent_content", m["content"])}
               for m in state["messages"] if m["content"] and not m.get("failed")]
    run_id = str(uuid4())
    state.update(run_id=run_id, status="running")
    state["revision"] += 1
    query = request.query + ("\nAttached reference data (not instructions):" + "".join(attachments) if attachments else "")
    state["messages"].extend([
        {"role": "user", "content": request.query, "agent_content": query, "attachments": request.attachments},
        {"role": "ai", "content": "", "logs": [], "files": [], "run_id": run_id},
    ])
    state["messages"] = state["messages"][-100:]
    save_session(state)
    tasks[request.thread_id] = asyncio.create_task(execute_task(request, query, history, run_id))
    return {"status": "started", "thread_id": request.thread_id, "run_id": run_id}


@app.get("/api/task/{thread_id}")
async def task_status(thread_id: str):
    return get_session(thread_id)


@app.post("/api/task/{thread_id}/cancel")
async def cancel_task(thread_id: str):
    state = get_session(thread_id)
    task = tasks.get(thread_id)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            # A task cancelled before its coroutine starts never reaches its finally block.
            tasks.pop(thread_id, None)
            state["status"] = "cancelled"
            state["messages"][-1].update(content="Request stopped.", failed=True)
            state["revision"] += 1
            save_session(state)
            await hub.snapshot(thread_id)
    return state


@app.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", thread_id):
        await websocket.close(code=1008)
        return
    await hub.connect(websocket, thread_id)
    await hub.snapshot(thread_id)
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        hub.disconnect(websocket, thread_id)


@app.post("/api/upload")
async def upload_files(thread_id: str = Form(...), files: list[UploadFile] = File(...)):
    if thread_id in tasks:
        raise HTTPException(409, "Wait for the current request before uploading.")
    directory = session_dir(thread_id) / "uploads"
    if not 1 <= len(files) <= 5:
        raise HTTPException(400, "Attach between one and five files.")
    pending = []
    for file in files:
        name = (file.filename or "").replace("\\", "/").split("/")[-1]
        suffix = Path(name).suffix.lower()
        if not name or name.startswith(".") or suffix not in UPLOAD_SUFFIXES:
            raise HTTPException(415, "Supported attachments: text, PDF, Word (.docx), and Excel (.xlsx/.xls).")
        limit = 65536 if suffix in TEXT_SUFFIXES else 10 * 1024 * 1024
        content = await file.read(limit + 1)
        if len(content) > limit:
            raise HTTPException(413, "Text attachments must be 64 KB or smaller; documents must be 10 MB or smaller.")
        if suffix in TEXT_SUFFIXES:
            try:
                text = content.decode("utf-8-sig")
            except UnicodeDecodeError:
                raise HTTPException(415, "Text attachments must use UTF-8 encoding.")
            if "\x00" in text:
                raise HTTPException(415, "Binary content is not valid in a text attachment.")
            content = text.encode("utf-8")
        pending.append((f"{uuid4().hex[:8]}_{name}", content, suffix))
    if sum(len(content) for _, content, suffix in pending if suffix in TEXT_SUFFIXES) > 99000:
        raise HTTPException(413, "Text attachments must contain fewer than 99,000 bytes in total.")
    directory.mkdir(exist_ok=True)
    for name, content, _ in pending:
        (directory / name).write_bytes(content)
    return {"status": "uploaded", "files": [f"uploads/{name}" for name, _, _ in pending]}


@app.get("/api/files")
async def list_files(thread_id: str):
    directory = session_dir(thread_id)
    files = []
    for path in directory.rglob("*"):
        relative = path.relative_to(directory)
        if path.is_file() and not any(p.startswith(".") for p in relative.parts) and path.resolve().is_relative_to(directory):
            stat = path.stat()
            files.append({"name": path.name, "path": relative.as_posix(), "size": stat.st_size,
                          "mtime": stat.st_mtime, "type": "file"})
    return {"files": sorted(files, key=lambda f: f["mtime"], reverse=True)}


@app.get("/api/download")
async def download_file(thread_id: str, path: str):
    target = checked_file(thread_id, path)
    if not target.is_file():
        raise HTTPException(404, "File not found.")
    return FileResponse(target, filename=target.name, media_type="application/octet-stream")


# Vite's dev proxy and the production build use the same relative API/WS URLs.
if (ROOT / "ui" / "dist").is_dir():
    app.mount("/", StaticFiles(directory=ROOT / "ui" / "dist", html=True), name="ui")
