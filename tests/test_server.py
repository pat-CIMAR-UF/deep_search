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
        monitor._emit("tool_start", "Querying sales", {"tool_name": "aggregate_documents"})
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
    assert client.post("/api/upload", data={"thread_id": "upload-session"}, files={"files": ("program.exe", b"MZ")} ).status_code == 415
    assert client.post("/api/upload", data={"thread_id": "upload-session"}, files={"files": ("big.txt", b"a" * 65537)}).status_code == 413
    assert client.post("/api/upload", data={"thread_id": "upload-session"}, files={"files": ("bad.txt", b"\xff")}).status_code == 415


@pytest.mark.parametrize("payload", [
    {"query": " "}, {"query": "hello", "mode": "unknown"},
    {"query": "hello", "thread_id": "../escape"},
])
def test_request_validation(client, payload):
    assert client.post("/api/task", json=payload).status_code == 422


def test_health_includes_three_agents(client):
    assert client.get("/api/health").json() == {"status": "ok", "agents": ["database", "internet", "ragflow"], "ragflow": True}


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


def test_document_upload_uses_reader_and_links_generated_pdf(client, monkeypatch):
    from io import BytesIO
    from docx import Document
    from tools.upload_file_read_tool import read_file_content
    from tools.markdown_tools import generate_markdown
    from tools.pdf_tools import convert_md_to_pdf
    document = Document()
    document.add_paragraph("Reference number: 731")
    payload = BytesIO()
    document.save(payload)
    response = client.post("/api/upload", data={"thread_id": "document-session"},
                           files={"files": ("notes.docx", payload.getvalue())})
    assert response.status_code == 200
    name = response.json()["files"][0]
    async def fake(query, history, mode):
        assert name in query
        assert "Reference number: 731" in read_file_content.invoke({"filename": name})
        generate_markdown.invoke({"content": "# Summary\nReference: 731", "filename": "summary"})
        assert "Converted successfully" in convert_md_to_pdf.invoke({"md_filename": "summary.md"})
        return "Report generated."
    monkeypatch.setattr(server, "run_agent", fake)
    with client.websocket_connect("/ws/document-session") as ws:
        ws.receive_json()
        response = client.post("/api/task", json={"thread_id": "document-session", "query": "Summarize",
                                                 "attachments": [name], "mode": "ragflow"})
        assert response.status_code == 202
        state = wait_result(ws)
    assert state["status"] == "completed"
    assert "summary.pdf" in [f['path'] for f in state['messages'][-1]['files']]
    pdf = client.get("/api/download", params={"thread_id": "document-session", "path": "summary.pdf"})
    assert pdf.content.startswith(b"%PDF-")


# ------------------------------------------------------------- error mapping --
def test_public_error_messages_never_include_exception_text():
    secret = RuntimeError("https://provider.test/v1?key=SECRET")
    assert "SECRET" not in server.public_error(secret)
    assert server.public_error(secret).startswith("The agent could not complete")
    assert "timed out" in server.public_error(TimeoutError())
    assert "timed out" in server.public_error(asyncio.TimeoutError())
    configuration = server.public_error(KeyError("QWEN_REMOTE_BASE_URL"))
    assert "not configured" in configuration and "QWEN_REMOTE_API_KEY" in configuration


# --------------------------------------------------------- request validation --
def test_request_limits_and_defaults(client, monkeypatch):
    async def fake(query, history, mode):
        return "ok"
    monkeypatch.setattr(server, "run_agent", fake)
    assert client.post("/api/task", json={"query": "x" * 20001}).status_code == 422
    assert client.post("/api/task", json={"query": "hi", "attachments": [f"uploads/{i}.txt" for i in range(6)]}).status_code == 422
    response = client.post("/api/task", json={"query": "  padded  "})
    assert response.status_code == 202
    thread_id = response.json()["thread_id"]
    assert len(thread_id) == 36 and thread_id.count("-") == 4
    with client.websocket_connect(f"/ws/{thread_id}") as ws:
        state = wait_result(ws)
    assert state["messages"][0]["content"] == "padded"
    assert state["messages"][-1]["content"] == "ok"


def test_attachment_references_are_validated(client, tmp_path):
    uploads = server.session_dir("attach-session") / "uploads"
    uploads.mkdir()
    (uploads / "program.exe").write_bytes(b"MZ")
    outside = server.session_dir("other-session") / "uploads"
    outside.mkdir()
    (outside / "notes.txt").write_text("private", encoding="utf-8")
    post = lambda names: client.post("/api/task", json={"query": "Read", "thread_id": "attach-session", "attachments": names})
    assert post(["uploads/missing.txt"]).status_code == 400
    assert post(["uploads/program.exe"]).status_code == 400
    assert post(["../session_other-session/uploads/notes.txt"]).status_code == 403
    assert post([".state.json"]).status_code == 403
    assert client.get("/api/task/attach-session").json()["status"] == "idle"


def test_attachment_context_total_size_limit(client):
    uploads = server.session_dir("large-session") / "uploads"
    uploads.mkdir()
    for name in ("a.txt", "b.txt"):
        (uploads / name).write_text("x" * 60000, encoding="utf-8")
    response = client.post("/api/task", json={"query": "Read", "thread_id": "large-session",
                                              "attachments": ["uploads/a.txt", "uploads/b.txt"]})
    assert response.status_code == 413
    assert client.get("/api/task/large-session").json()["status"] == "idle"


def test_websocket_rejects_invalid_thread_ids(client):
    from starlette.websockets import WebSocketDisconnect
    with pytest.raises(WebSocketDisconnect) as info:
        with client.websocket_connect("/ws/" + "a" * 81):
            pass
    assert info.value.code == 1008


def test_cancel_without_running_task_returns_current_state(client):
    assert client.post("/api/task/idle-session/cancel").json()["status"] == "idle"
    assert client.get("/api/task/idle-session").json()["revision"] == 0


def test_download_missing_file_is_404(client):
    assert client.get("/api/download", params={"thread_id": "empty-session", "path": "nope.md"}).status_code == 404


# ------------------------------------------------------------------- uploads --
def test_upload_is_rejected_while_a_request_is_running(client, monkeypatch):
    async def slow(*args):
        await asyncio.sleep(60)
    monkeypatch.setattr(server, "run_agent", slow)
    client.post("/api/task", json={"query": "Long", "thread_id": "busy-session"})
    response = client.post("/api/upload", data={"thread_id": "busy-session"}, files={"files": ("n.txt", b"x")})
    assert response.status_code == 409
    client.post("/api/task/busy-session/cancel")


def test_upload_validation_rules(client):
    upload = lambda files: client.post("/api/upload", data={"thread_id": "rules-session"}, files=files)
    assert upload([("files", (f"f{i}.txt", b"x")) for i in range(6)]).status_code == 400
    assert upload({"files": ("nul.txt", b"abc\x00def")}).status_code == 415
    assert upload({"files": (".hidden.txt", b"x")}).status_code == 415
    assert upload({"files": ("noext", b"x")}).status_code == 415
    assert upload([("files", ("a.txt", b"a" * 50000)), ("files", ("b.txt", b"b" * 50000))]).status_code == 413
    assert upload({"files": ("big.pdf", b"%PDF-" + b"0" * (10 * 1024 * 1024))}).status_code == 413
    assert (server.session_dir("rules-session") / "uploads").exists() is False


def test_upload_sanitizes_names_and_normalizes_text(client):
    response = client.post("/api/upload", data={"thread_id": "names-session"}, files=[
        ("files", ("dir/../evil.txt", b"\xef\xbb\xbfwith bom")),
        ("files", ("C:\\Users\\me\\notes.md", b"# notes")),
        ("files", ("report.docx", b"PK\x03\x04binary")),
    ])
    assert response.status_code == 200
    names = response.json()["files"]
    assert [n.split("/", 1)[1].split("_", 1)[1] for n in names] == ["evil.txt", "notes.md", "report.docx"]
    assert all(n.startswith("uploads/") and len(n.split("/")[1].split("_")[0]) == 8 for n in names)
    stored = server.session_dir("names-session") / names[0]
    assert stored.read_bytes() == b"with bom"
    assert (server.session_dir("names-session") / names[2]).read_bytes() == b"PK\x03\x04binary"
    listed = client.get("/api/files", params={"thread_id": "names-session"}).json()["files"]
    assert sorted(f["path"] for f in listed) == sorted(names)


# --------------------------------------------------------- state bookkeeping --
def test_history_excludes_failed_answers_and_uses_agent_content(client, monkeypatch):
    seen = []
    attempts = {"n": 0}

    async def flaky(query, history, mode):
        attempts["n"] += 1
        seen.append(list(history))
        if attempts["n"] == 1:
            raise RuntimeError("first attempt fails")
        return "Second answer"
    monkeypatch.setattr(server, "run_agent", flaky)
    uploads = server.session_dir("history-session") / "uploads"
    uploads.mkdir()
    (uploads / "ref.txt").write_text("Reference: 7", encoding="utf-8")
    with client.websocket_connect("/ws/history-session") as ws:
        ws.receive_json()
        client.post("/api/task", json={"query": "First", "thread_id": "history-session", "attachments": ["uploads/ref.txt"]})
        assert wait_result(ws)["status"] == "error"
        client.post("/api/task", json={"query": "Second", "thread_id": "history-session"})
        assert wait_result(ws)["status"] == "completed"
    assert seen[0] == []
    assert [m["role"] for m in seen[1]] == ["user"]
    assert "Reference: 7" in seen[1][0]["content"] and seen[1][0]["content"].startswith("First")
    state = client.get("/api/task/history-session").json()
    assert state["messages"][0]["content"] == "First"
    assert state["messages"][0]["attachments"] == ["uploads/ref.txt"]
    assert state["messages"][1]["failed"] is True


def test_message_history_is_capped_at_one_hundred(client, monkeypatch):
    async def fake(query, history, mode):
        return "ok"
    monkeypatch.setattr(server, "run_agent", fake)
    state = server.get_session("cap-session")
    state["messages"] = [{"role": "user", "content": f"m{i}"} for i in range(100)]
    with client.websocket_connect("/ws/cap-session") as ws:
        ws.receive_json()
        client.post("/api/task", json={"query": "New", "thread_id": "cap-session"})
        final = wait_result(ws)
    assert len(final["messages"]) == 100
    assert final["messages"][0]["content"] == "m2"
    assert final["messages"][-2]["content"] == "New"


def test_live_events_cap_logs_and_ignore_other_runs(client):
    state = server.get_session("events-session")
    state.update(run_id="run-A", status="running", messages=[{"role": "ai", "content": "", "logs": []}])

    async def exercise():
        for i in range(105):
            await server.hub.send_to_thread({"run_id": "run-A", "event": "tool_start", "message": f"step {i}",
                                             "data": {"i": i}, "timestamp": "t"}, "events-session")
        await server.hub.send_to_thread({"run_id": "run-B", "event": "tool_start", "message": "stale"}, "events-session")
        await server.hub.send_to_thread({"run_id": "run-A", "event": "task_result", "message": "done"}, "events-session")

    asyncio.run(exercise())
    logs = state["messages"][-1]["logs"]
    assert len(logs) == 100
    assert logs[0]["title"] == "step 5" and logs[-1] == {"title": "step 104", "details": {"i": 104}, "timestamp": "t"}
    assert state["revision"] == 106


def test_snapshot_drops_sockets_that_fail_to_send(client):
    class DeadSocket:
        async def send_json(self, data):
            raise RuntimeError("connection closed")

    dead = DeadSocket()
    server.hub.active_connections["dead-session"] = dead
    asyncio.run(server.hub.snapshot("dead-session"))
    assert "dead-session" not in server.hub.active_connections


def test_restored_state_gets_a_revision_and_lists_files_newest_first(client):
    directory = server.session_dir("restore-session")
    (directory / ".state.json").write_text(
        '{"thread_id": "restore-session", "run_id": null, "status": "completed", "messages": []}', encoding="utf-8")
    assert client.get("/api/task/restore-session").json()["revision"] == 0
    (directory / "old.md").write_text("old", encoding="utf-8")
    (directory / "nested").mkdir()
    (directory / "nested" / "new.md").write_text("new", encoding="utf-8")
    (directory / ".hidden.md").write_text("hidden", encoding="utf-8")
    import os
    os.utime(directory / "old.md", (1_600_000_000, 1_600_000_000))
    os.utime(directory / "nested" / "new.md", (1_700_000_000, 1_700_000_000))
    files = client.get("/api/files", params={"thread_id": "restore-session"}).json()["files"]
    assert [f["path"] for f in files] == ["nested/new.md", "old.md"]
    assert files[0] == {"name": "new.md", "path": "nested/new.md", "size": 3, "mtime": 1_700_000_000.0, "type": "file"}


def test_generated_files_exclude_uploads_written_during_the_run(client, monkeypatch):
    async def fake(query, history, mode):
        directory = Path(get_session_context())
        (directory / "uploads").mkdir(exist_ok=True)
        (directory / "uploads" / "scratch.txt").write_text("not a report", encoding="utf-8")
        (directory / "report.md").write_text("# Report", encoding="utf-8")
        return "Done"
    monkeypatch.setattr(server, "run_agent", fake)
    with client.websocket_connect("/ws/generated-session") as ws:
        ws.receive_json()
        client.post("/api/task", json={"query": "Report", "thread_id": "generated-session"})
        state = wait_result(ws)
    paths = sorted(f["path"] for f in state["messages"][-1]["files"])
    assert "report.md" in paths
    assert any(p.startswith("answer_") for p in paths)
    assert not any(p.startswith("uploads/") for p in paths)


def test_shutdown_cancels_running_requests(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "OUTPUT_ROOT", tmp_path.resolve())
    server.sessions.clear()
    server.tasks.clear()

    async def slow(*args):
        await asyncio.sleep(60)
    monkeypatch.setattr(server, "run_agent", slow)
    with TestClient(server.app) as client:
        assert client.post("/api/task", json={"query": "Long", "thread_id": "shutdown-session"}).status_code == 202
        assert "shutdown-session" in server.tasks
    assert server.tasks == {}
    state = server.sessions["shutdown-session"]
    assert state["status"] == "cancelled"
    assert state["messages"][-1] == {"role": "ai", "content": "Request stopped.", "logs": [], "files": [],
                                     "run_id": state["run_id"], "failed": True}
    server.sessions.clear()
