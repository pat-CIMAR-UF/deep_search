"""Persistent stdio session to mongodb-mcp-server, shared by the MongoDB tools.

The server is spawned once per process and kept alive on a dedicated thread with its
own event loop. anyio cancel scopes must be entered and exited in the same task, so
that thread owns the `async with Client(...)` block; synchronous tools marshal calls
into the loop with `asyncio.run_coroutine_threadsafe`.
"""
import asyncio
import atexit
import os
import shlex
import shutil
import sys
import threading
from pathlib import Path

import anyio
from dotenv import load_dotenv, find_dotenv
from mcp import Client, MCPError, StdioServerParameters
from mcp.types import CONNECTION_CLOSED, CallToolResult

_PROJECT_ROOT = str(Path(__file__).parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# 加载项目根目录的 .env 文件 / Load .env from the project root
_ = load_dotenv(find_dotenv())

PRECONFIGURED_CONNECTION = "preconfigured"
CALL_TIMEOUT = 120.0
STARTUP_TIMEOUT = 90.0
MAX_DOCUMENTS_PER_QUERY = 100
DEFAULT_DATABASE = "pharma_db"
_SERVER_BINARY = "mongodb-mcp-server"
_NPX_ARGS = "-y mongodb-mcp-server@3"
# 子进程不会继承父进程环境变量，代理等设置需要显式转发 / The child does not inherit env; forward proxies explicitly
_FORWARDED_ENV = ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy",
                  "NODE_EXTRA_CA_CERTS", "npm_config_registry")
_TRANSPORT_ERRORS = (anyio.ClosedResourceError, anyio.BrokenResourceError)


def get_mongo_config() -> dict:
    """Read the MongoDB MCP settings from the environment.

    Returns a dict with ``uri``, ``database``, ``command`` and ``args``.
    Raises ValueError when MONGODB_URI is missing.
    """
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("Missing core database configuration: MONGODB_URI")
    command = os.getenv("MONGODB_MCP_COMMAND")
    args = os.getenv("MONGODB_MCP_ARGS")
    if not command:
        # 优先使用全局安装的二进制，其次回退到 npx / Prefer the global binary, fall back to npx
        command = _SERVER_BINARY if shutil.which(_SERVER_BINARY) else "npx"
        if args is None:
            args = "" if command == _SERVER_BINARY else _NPX_ARGS
    return {
        "uri": uri,
        "database": os.getenv("MONGODB_DATABASE", DEFAULT_DATABASE),
        "command": command,
        "args": shlex.split(args or ""),
    }


def server_parameters(config: dict) -> StdioServerParameters:
    """Build the read-only spawn parameters for mongodb-mcp-server."""
    env = {
        "MDB_MCP_CONNECTION_STRING": config["uri"],
        "MDB_MCP_READ_ONLY": "true",
        "MDB_MCP_DISABLED_TOOLS": "atlas,connect,create,update,delete,export",
        "MDB_MCP_MAX_DOCUMENTS_PER_QUERY": str(MAX_DOCUMENTS_PER_QUERY),
        "MDB_MCP_MAX_TIME_MS": "60000",
        "MDB_MCP_TELEMETRY": "disabled",
        "DO_NOT_TRACK": "1",
        "MDB_MCP_LOGGERS": "mcp",
    }
    for key in _FORWARDED_ENV:
        value = os.getenv(key)
        if value:
            env[key] = value
    return StdioServerParameters(command=config["command"], args=list(config["args"]), env=env)


def _is_transport_failure(exc: BaseException) -> bool:
    if isinstance(exc, _TRANSPORT_ERRORS):
        return True
    return isinstance(exc, MCPError) and exc.code == CONNECTION_CLOSED


class MCPClient:
    """Own one mongodb-mcp-server process from a dedicated thread and event loop."""

    def __init__(self):
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._client = None
        self._stop: asyncio.Event | None = None
        self._ready = threading.Event()
        self._error: BaseException | None = None

    # ------------------------------------------------------------------ owner --
    def _serve(self, params: StdioServerParameters) -> None:
        async def main():
            self._loop = asyncio.get_running_loop()
            self._stop = asyncio.Event()
            try:
                # 进入和退出必须在同一个任务中 / Enter and exit inside the same task
                async with Client(params, read_timeout_seconds=CALL_TIMEOUT) as client:
                    self._client = client
                    self._ready.set()
                    await self._stop.wait()
            except BaseException as exc:  # noqa: BLE001 - surfaced to the caller via _error
                self._error = exc
            finally:
                self._client = None
                self._ready.set()  # unblock a waiting starter; it checks _client

        asyncio.run(main())

    def _alive(self) -> bool:
        return self._client is not None and self._thread is not None and self._thread.is_alive()

    def _ensure_started(self) -> None:
        # 只锁初始化，避免并发首次调用启动多个进程 / Lock only initialization so concurrent first calls share one process
        with self._lock:
            if self._alive():
                return
            self._stop_thread()
            params = server_parameters(get_mongo_config())
            self._ready.clear()
            self._error = None
            self._thread = threading.Thread(target=self._serve, args=(params,), name="mongodb-mcp", daemon=True)
            self._thread.start()
            if not self._ready.wait(STARTUP_TIMEOUT):
                self._stop_thread()
                raise RuntimeError("Timed out starting mongodb-mcp-server.")
            if self._client is None:
                raise RuntimeError(f"Could not start mongodb-mcp-server: {self._error}")

    def _stop_thread(self, timeout: float = 10.0) -> None:
        thread, loop, stop = self._thread, self._loop, self._stop
        if thread is not None and thread.is_alive() and loop is not None and stop is not None:
            loop.call_soon_threadsafe(stop.set)
            thread.join(timeout)
        self._thread = None
        self._client = None
        self._loop = None
        self._stop = None

    def _mark_dead(self) -> None:
        with self._lock:
            self._stop_thread()

    # ----------------------------------------------------------------- public --
    def call_tool(self, name: str, arguments: dict, timeout: float = CALL_TIMEOUT) -> CallToolResult:
        """Call one MCP tool on the preconfigured connection; respawn once if the process died."""
        for attempt in (1, 2):
            self._ensure_started()
            client, loop = self._client, self._loop
            coro = client.call_tool(name, {"connectionId": PRECONFIGURED_CONNECTION, **arguments},
                                    read_timeout_seconds=timeout)
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            try:
                return future.result(timeout + 5)
            except TimeoutError:
                future.cancel()
                raise TimeoutError(f"MCP tool '{name}' did not answer within {timeout:.0f} seconds.")
            except Exception as exc:  # noqa: BLE001 - only transport failures are retried
                if attempt == 2 or not _is_transport_failure(exc):
                    raise
                self._mark_dead()
        raise RuntimeError("unreachable")  # pragma: no cover

    def shutdown(self, timeout: float = 10.0) -> None:
        """Stop the server process; safe to call repeatedly."""
        with self._lock:
            self._stop_thread(timeout)


_client = MCPClient()


def call_mcp_tool(name: str, arguments: dict, timeout: float = CALL_TIMEOUT) -> CallToolResult:
    """Call a tool on the shared mongodb-mcp-server session."""
    return _client.call_tool(name, arguments, timeout=timeout)


def shutdown() -> None:
    """Stop the shared mongodb-mcp-server process."""
    _client.shutdown()


atexit.register(shutdown)
