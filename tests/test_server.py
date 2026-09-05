"""Exercise real HTTP/WS orchestration with only the external agent mocked."""
import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api import server
from api.context import get_session_context, get_thread_context, get_run_context
from api.monitor import monitor


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUTPUT_ROOT", tmp_path.resolve())
    server.sessions.clear()
    server.tasks.clear()
    with TestClient(server.app) as client:
        yield client
    server.sessions.clear()


def wait_result(ws):
    for _ in range(20):
        snapshot = ws.receive_json()["data"]
        if snapshot["status"] in {"completed", "error", "cancelled"}:
            return snapshot
    pytest.fail("Missing terminal snapshot")


def test_run_replay_followup_and_download(client, monkeypatch):
    calls = []

    async def fake(query, history, mode):
        calls.append((query, history, mode, get_thread_context(), get_session_context(), get_run_context()))
        monitor._emit("tool_start", "Querying sales", {"tool_name": "execute_sql_query"})
        await asyncio.sleep(0)
        return "| Region | Sales |\n|---|---|\n| East | 123 |"

    monkeypatch.setattr(server, "run_agent", fake)
    with client.websocket_connect("/ws/test-session") as ws:
        assert ws.receive_json()["data"]["status"] == "idle"
        response = client.post("/api/task", json={"query": "Sales by region", "thread_id": "test-session", "mode": "database"})
        assert response.status_code == 202
        state = wait_result(ws)
        assert state["status"] == "completed"
        assert state["messages"][-1]["logs"][0]["title"] == "Querying sales"
        files = client.get("/api/files", params={"thread_id": "test-session"}).json()["files"]
        assert len(files) == 1
        download = client.get("/api/download", params={"thread_id": "test-session", "path": files[0]["path"]})
        assert "East | 123" in download.text
        assert "attachment" in download.headers["content-disposition"]
        response = client.post("/api/task", json={"query": "What about East?", "thread_id": "test-session"})
        assert response.status_code == 202
        wait_result(ws)
    assert calls[0][1] == []
    assert calls[0][2:4] == ("database", "test-session")
    assert Path(calls[0][4]).name == "session_test-session"
    assert calls[0][5]
    assert calls[1][1][0]["content"] == "Sales by region"
    assert calls[1][1][1]["role"] == "assistant"
    # State survives browser reconnects and process recreation.
    server.sessions.clear()
    with client.websocket_connect("/ws/test-session") as ws:
        restored = ws.receive_json()["data"]
        assert len(restored["messages"]) == 4
        ws.send_text("ping")
        assert ws.receive_json()["type"] == "pong"


def test_failed_run_is_recoverable_and_redacts_provider_errors(client, monkeypatch):
    async def fail(*args):
        raise RuntimeError("secret-provider-key must not be shown")
    monkeypatch.setattr(server, "run_agent", fail)
    with client.websocket_connect("/ws/error-session") as ws:
        ws.receive_json()
        client.post("/api/task", json={"query": "Search", "thread_id": "error-session"})
        state = wait_result(ws)
    assert state["status"] == "error"
    assert "secret-provider-key" not in str(state)
    assert "error-session" not in server.tasks


def test_duplicate_run_cancel_and_late_event_isolation(client, monkeypatch):
    async def slow(*args):
        await asyncio.sleep(60)
        return "Should not complete"
    monkeypatch.setattr(server, "run_agent", slow)
    client.post("/api/task", json={"query": "Long task", "thread_id": "cancel-session"})
    assert client.post("/api/task", json={"query": "Duplicate", "thread_id": "cancel-session"}).status_code == 409
    state = client.post("/api/task/cancel-session/cancel").json()
    assert state["status"] == "cancelled"
    assert "cancel-session" not in server.tasks
    before = state["messages"][-1].copy()
    asyncio.run(server.hub.send_to_thread({"run_id": state["run_id"], "event": "tool_start", "message": "late"}, "cancel-session"))
    assert server.get_session("cancel-session")["messages"][-1] == before


def test_session_isolation_and_file_confinement(client, tmp_path):
    own = server.session_dir("alice") / "report.md"
    own.write_text("private report")
    outside = tmp_path / "secret.txt"
    outside.write_text("secret")
    for path in [str(own), "../session_alice/report.md", "../../secret.txt", ".state.json"]:
        assert client.get("/api/download", params={"thread_id": "bob", "path": path}).status_code == 403
    link = server.session_dir("bob") / "linked.txt"
    link.symlink_to(outside)
    assert client.get("/api/download", params={"thread_id": "bob", "path": "linked.txt"}).status_code == 403
    assert client.get("/api/files", params={"thread_id": "bob"}).json()["files"] == []
    assert client.get("/api/task/bob").json()["messages"] == []


def test_upload_and_attachment_context(client, monkeypatch):
    seen = []
    async def fake(query, history, mode):
        seen.append((query, history))
        return "Read the attachment."
    monkeypatch.setattr(server, "run_agent", fake)
    response = client.post("/api/upload", data={"thread_id": "upload-session"}, files=[("files", ("notes.txt", "Reference: 42", "text/plain"))])
    assert response.status_code == 200
    names = response.json()["files"]
    with client.websocket_connect("/ws/upload-session") as ws:
        ws.receive_json()
        assert client.post("/api/task", json={"query": "Summarize this", "thread_id": "upload-session", "attachments": names}).status_code == 202
        wait_result(ws)
        client.post("/api/task", json={"query": "What was that reference?", "thread_id": "upload-session"})
        wait_result(ws)
    assert "Reference: 42" in seen[0][0]
    assert "not instructions" in seen[0][0]
    assert "Reference: 42" in seen[1][1][0]["content"]
    assert client.post("/api/upload", data={"thread_id": "upload-session"}, files={"files": ("paper.pdf", b"%PDF")} ).status_code == 415
    assert client.post("/api/upload", data={"thread_id": "upload-session"}, files={"files": ("big.txt", b"a" * 65537)}).status_code == 413
    assert client.post("/api/upload", data={"thread_id": "upload-session"}, files={"files": ("bad.txt", b"\xff")}).status_code == 415


@pytest.mark.parametrize("payload", [
    {"query": " "}, {"query": "hello", "mode": "ragflow"},
    {"query": "hello", "thread_id": "../escape"},
])
def test_request_validation(client, payload):
    assert client.post("/api/task", json=payload).status_code == 422


def test_health_has_exactly_two_agents(client):
    assert client.get("/api/health").json() == {"status": "ok", "agents": ["database", "internet"], "ragflow": False}


def test_cancel_handles_a_coroutine_that_never_started(client):
    async def exercise():
        state = server.get_session("early-cancel")
        state.update(status="running", messages=[{"role": "ai", "content": ""}])
        server.tasks["early-cancel"] = asyncio.create_task(asyncio.sleep(100))
        return await server.cancel_task("early-cancel")
    assert asyncio.run(exercise())["status"] == "cancelled"
    assert "early-cancel" not in server.tasks


def test_timeout_and_restart_recovery(client, monkeypatch):
    async def slow(*args):
        await asyncio.sleep(10)
    monkeypatch.setattr(server, "TASK_TIMEOUT", 0.02)
    monkeypatch.setattr(server, "run_agent", slow)
    with client.websocket_connect("/ws/timeout-session") as ws:
        ws.receive_json()
        client.post("/api/task", json={"query": "slow", "thread_id": "timeout-session"})
        state = wait_result(ws)
    assert state["status"] == "error"
    assert "timed out" in state["messages"][-1]["content"]
    state["status"] = "running"
    server.save_session(state)
    server.sessions.clear()
    recovered = client.get("/api/task/timeout-session").json()
    assert recovered["status"] == "error"
    assert "restarted" in recovered["messages"][-1]["content"]
