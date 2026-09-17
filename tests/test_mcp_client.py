"""Tests for the persistent mongodb-mcp-server session in tools/mcp_client.py (no subprocess)."""
import asyncio
import threading
import time

import pytest
from mcp import MCPError
from mcp.types import CONNECTION_CLOSED, CallToolResult, TextContent

import tools.mcp_client as mcp_client


class FakeClient:
    """Stand-in for mcp.Client: records lifecycle and tool calls."""
    instances: list["FakeClient"] = []

    def __init__(self, params, read_timeout_seconds=None):
        self.params = params
        self.read_timeout_seconds = read_timeout_seconds
        self.entered = self.exited = False
        self.calls: list[tuple[str, dict, float | None]] = []
        self.fail_enter = False
        self.fail_next: BaseException | None = None
        FakeClient.instances.append(self)

    async def __aenter__(self):
        if self.fail_enter:
            raise OSError("spawn failed")
        self.entered = True
        return self

    async def __aexit__(self, *exc):
        self.exited = True
        return False

    async def call_tool(self, name, arguments, read_timeout_seconds=None):
        self.calls.append((name, arguments, read_timeout_seconds))
        if self.fail_next is not None:
            error, self.fail_next = self.fail_next, None
            raise error
        if name == "sleep":
            await asyncio.sleep(arguments["seconds"])
        return CallToolResult(content=[TextContent(type="text", text=f"{name} ok")], structured_content={"tool": name})


@pytest.fixture
def client(monkeypatch):
    FakeClient.instances = []
    monkeypatch.setattr(mcp_client, "Client", FakeClient)
    monkeypatch.setattr(mcp_client, "STARTUP_TIMEOUT", 5.0)
    instance = mcp_client.MCPClient()
    yield instance
    instance.shutdown()


def test_call_tool_starts_once_and_injects_connection_id(client):
    first = client.call_tool("find", {"database": "test_db", "collection": "drugs"}, timeout=7)
    second = client.call_tool("count", {"database": "test_db"})
    assert first.structured_content == {"tool": "find"} and second.structured_content == {"tool": "count"}
    assert len(FakeClient.instances) == 1
    fake = FakeClient.instances[0]
    assert fake.calls[0] == ("find", {"connectionId": "preconfigured", "database": "test_db", "collection": "drugs"}, 7)
    assert fake.calls[1][2] == mcp_client.CALL_TIMEOUT
    assert fake.params.env["MDB_MCP_READ_ONLY"] == "true"
    assert fake.read_timeout_seconds == mcp_client.CALL_TIMEOUT


def test_concurrent_first_calls_share_one_process(client):
    results, errors = [], []

    def worker():
        try:
            results.append(client.call_tool("list-collections", {"database": "test_db"}))
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(10)
    assert not errors and len(results) == 8
    assert len(FakeClient.instances) == 1
    assert len(FakeClient.instances[0].calls) == 8


def test_transport_failure_respawns_once(client):
    client.call_tool("count", {"database": "test_db"})
    first = FakeClient.instances[0]
    first.fail_next = MCPError(CONNECTION_CLOSED, "Connection closed")
    result = client.call_tool("count", {"database": "test_db"})
    assert result.structured_content == {"tool": "count"}
    assert len(FakeClient.instances) == 2
    assert first.exited is True
    assert len(FakeClient.instances[1].calls) == 1


def test_other_mcp_errors_are_not_retried(client):
    client.call_tool("count", {"database": "test_db"})
    FakeClient.instances[0].fail_next = MCPError(-32602, "Invalid arguments")
    with pytest.raises(MCPError, match="Invalid arguments"):
        client.call_tool("count", {"database": "test_db"})
    assert len(FakeClient.instances) == 1


def test_spawn_failure_is_reported(client):
    original_init = FakeClient.__init__

    def failing_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.fail_enter = True

    FakeClient.__init__ = failing_init
    try:
        with pytest.raises(RuntimeError, match="Could not start mongodb-mcp-server.*spawn failed"):
            client.call_tool("count", {"database": "test_db"})
    finally:
        FakeClient.__init__ = original_init


def test_missing_uri_fails_before_spawning(client, monkeypatch):
    monkeypatch.delenv("MONGODB_URI")
    with pytest.raises(ValueError, match="MONGODB_URI"):
        client.call_tool("count", {"database": "test_db"})
    assert FakeClient.instances == []


def test_call_timeout_raises_timeout_error(client):
    with pytest.raises(TimeoutError, match="did not answer"):
        client.call_tool("sleep", {"seconds": 5}, timeout=-4.9)


def test_shutdown_exits_context_and_allows_restart(client):
    client.call_tool("count", {"database": "test_db"})
    fake = FakeClient.instances[0]
    client.shutdown()
    deadline = time.time() + 5
    while not fake.exited and time.time() < deadline:
        time.sleep(0.01)
    assert fake.exited is True
    assert not any(t.name == "mongodb-mcp" and t.is_alive() for t in threading.enumerate())
    client.shutdown()  # idempotent
    client.call_tool("count", {"database": "test_db"})
    assert len(FakeClient.instances) == 2
