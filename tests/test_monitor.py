"""Tests for api/monitor.py: event routing across loops/threads and the connection manager."""
import asyncio
import builtins
from datetime import datetime
from types import SimpleNamespace

import pytest

from api import context
from api.monitor import ConnectionManager, ToolMonitor, monitor


class FakeManager:
    def __init__(self, loop):
        self.loop = loop
        self.sent = []

    async def send_to_thread(self, payload, thread_id):
        self.sent.append((payload, thread_id))


class FakeWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent = []

    async def accept(self):
        self.accepted = True

    async def send_text(self, text):
        self.sent.append(("text", text))

    async def send_json(self, data):
        self.sent.append(("json", data))


@pytest.fixture
def run_context():
    """Set thread/run/session context for the duration of a test."""
    session_token = context.set_session_context("/tmp/session_monitor")
    thread_token = context.set_thread_context("monitor-thread")
    run_token = context.set_run_context("run-1")
    yield
    context.reset_run_context(run_token)
    context.reset_session_context(session_token, thread_token)


@pytest.fixture
def no_manager(monkeypatch):
    monkeypatch.setattr(monitor, "websocket_manager", None)


def emit(method, *args):
    """Call the real ToolMonitor method even though conftest patches report_tool on the instance."""
    return getattr(ToolMonitor, method)(monitor, *args)


# ----------------------------------------------------------------- ToolMonitor --
def test_monitor_is_a_singleton():
    assert ToolMonitor() is monitor


def test_emit_without_manager_prints_console_fallback(no_manager, run_context, capsys):
    emit("report_tool", "my_tool", {"a": 1})
    assert "[Monitor:tool_start] Tool execution started: my_tool" in capsys.readouterr().out


def test_payload_shape_and_same_loop_delivery(monkeypatch, run_context):
    async def run():
        manager = FakeManager(asyncio.get_running_loop())
        monkeypatch.setattr(monitor, "websocket_manager", manager)
        emit("report_tool", "my_tool", {"a": 1})
        emit("report_assistant", "Database Query Agent", {"description": "Look up sales"})
        emit("report_task_result", "done")
        emit("report_session_dir", "/tmp/session_monitor")
        await asyncio.sleep(0)
        return manager.sent

    sent = asyncio.run(run())
    assert [thread for _, thread in sent] == ["monitor-thread"] * 4
    events = [payload["event"] for payload, _ in sent]
    assert events == ["tool_start", "assistant_call", "task_result", "session_created"]
    first = sent[0][0]
    assert first["type"] == "monitor_event"
    assert first["run_id"] == "run-1"
    assert first["message"] == "Tool execution started: my_tool"
    assert first["data"] == {"tool_name": "my_tool", "args": {"a": 1}}
    datetime.fromisoformat(first["timestamp"])
    assert sent[1][0]["data"] == {"assistant_name": "Database Query Agent", "args": {"description": "Look up sales"}}
    assert sent[2][0]["data"] == {"result": "done"}
    assert sent[3][0]["data"] == {"path": "/tmp/session_monitor"}


def test_emit_from_worker_thread_uses_threadsafe_scheduling(monkeypatch, run_context):
    """Synchronous tools run in worker threads with no running loop of their own."""
    async def run():
        manager = FakeManager(asyncio.get_running_loop())
        monkeypatch.setattr(monitor, "websocket_manager", manager)
        await asyncio.to_thread(emit, "report_tool", "threaded_tool", {})
        for _ in range(50):
            if manager.sent:
                break
            await asyncio.sleep(0.01)
        return manager.sent

    sent = asyncio.run(run())
    assert len(sent) == 1
    assert sent[0][0]["data"]["tool_name"] == "threaded_tool"


def test_emit_without_thread_context_is_not_delivered(monkeypatch):
    thread_token = context.set_thread_context(None)
    try:
        async def run():
            manager = FakeManager(asyncio.get_running_loop())
            monkeypatch.setattr(monitor, "websocket_manager", manager)
            emit("report_tool", "orphan", {})
            await asyncio.sleep(0)
            return manager.sent
        assert asyncio.run(run()) == []
    finally:
        context.reset_session_context(context.set_session_context(None), thread_token)


def test_emit_with_unbound_manager_loop_is_skipped(monkeypatch, run_context):
    manager = FakeManager(None)
    monkeypatch.setattr(monitor, "websocket_manager", manager)
    emit("report_tool", "early", {})
    assert manager.sent == []


def test_emit_survives_a_closed_manager_loop(monkeypatch, run_context, capsys):
    """After the app shuts down the hub may keep a closed loop; reporting must not raise."""
    loop = asyncio.new_event_loop()
    loop.close()
    manager = FakeManager(loop)
    monkeypatch.setattr(monitor, "websocket_manager", manager)
    with pytest.warns(RuntimeWarning, match="never awaited"):
        emit("report_tool", "stale", {})
    out = capsys.readouterr().out
    assert "[Monitor] WebSocket send failed" in out
    assert "[Monitor:tool_start]" in out


def test_emit_forwards_to_script_runtime_stream_writer(no_manager, run_context, monkeypatch):
    received = []
    monkeypatch.setattr(builtins, "runtime", SimpleNamespace(stream_writer=received.append), raising=False)
    emit("report_task_result", "final")
    assert received[0]["event"] == "task_result"

    def broken(payload):
        raise RuntimeError("writer closed")

    monkeypatch.setattr(builtins, "runtime", SimpleNamespace(stream_writer=broken), raising=False)
    emit("report_task_result", "still fine")


# ----------------------------------------------------------- ConnectionManager --
def test_set_loop_binds_manager_to_monitor(monkeypatch):
    monkeypatch.setattr(monitor, "websocket_manager", monitor.websocket_manager)
    manager = ConnectionManager()
    loop = asyncio.new_event_loop()
    try:
        manager.set_loop(loop)
        assert manager.loop is loop
        assert monitor.websocket_manager is manager
    finally:
        loop.close()


def test_connect_send_and_disconnect_lifecycle():
    async def run():
        manager = ConnectionManager()
        first, second = FakeWebSocket(), FakeWebSocket()
        await manager.connect(first, "t1")
        assert first.accepted and manager.active_connections == {"t1": first}
        await manager.send_to_thread({"event": "x"}, "t1")
        await manager.send_to_thread({"event": "ignored"}, "unknown")
        await manager.send_personal_message("hello", first)
        assert first.sent == [("json", {"event": "x"}), ("text", "hello")]
        # A stale socket must not evict the connection that replaced it.
        await manager.connect(second, "t1")
        manager.disconnect(first, "t1")
        assert manager.active_connections == {"t1": second}
        manager.disconnect(second, "t1")
        assert manager.active_connections == {}

    asyncio.run(run())
