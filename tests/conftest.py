"""Shared fixtures for the deep_search unit-test harness.

All external services (MySQL, Gemini, Tavily, RAGFlow, the Qwen chat model) are
mocked. Dummy credentials are injected *before* any project module is imported
so that import-time configuration (agent.llm, tools.*, ragflow.*) never touches
real secrets and does not depend on a .env file being present.
"""
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Dummy configuration. python-dotenv does not override variables that are
# already set, so these win over whatever is in .env.
_TEST_ENV = {
    "QWEN_REMOTE_BASE_URL": "http://qwen.test/v1",
    "QWEN_REMOTE_API_KEY": "test-qwen-key",
    "GEMINI_API_KEY": "test-gemini-key",
    "GEMINI_MODEL": "gemini-test-model",
    "TAVILY_API_KEY": "tvly-test-key",
    "MYSQL_HOST": "db.test",
    "MYSQL_PORT": "3307",
    "MYSQL_USER": "test_user",
    "MYSQL_PASSWORD": "test_password",
    "MYSQL_DATABASE": "test_db",
    "RAGFLOW_API_KEY": "ragflow-test-key",
    "RAGFLOW_API_URL": "http://ragflow.test:9380",
}
for _k, _v in _TEST_ENV.items():
    os.environ[_k] = _v


@pytest.fixture
def test_env():
    """The dummy environment values injected for the test session."""
    return dict(_TEST_ENV)


@pytest.fixture(autouse=True)
def monitor_calls(monkeypatch):
    """Silence api.monitor and record every report_tool call as (tool_name, args)."""
    from api.monitor import monitor

    calls: list[tuple[str, dict]] = []

    def _record(tool_name, args=None):
        calls.append((tool_name, args))

    monkeypatch.setattr(monitor, "report_tool", _record)
    return calls


# --------------------------------------------------------------------------- #
# Fake MySQL connection
# --------------------------------------------------------------------------- #
class FakeCursor:
    def __init__(self, rows=(), description=None, execute_error=None):
        self.rows = list(rows)
        self.description = description
        self.execute_error = execute_error
        self.executed: list[str] = []
        self.fetchmany_size = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self.executed.append(sql)
        if self.execute_error is not None:
            raise self.execute_error

    def fetchall(self):
        return list(self.rows)

    def fetchmany(self, size=1):
        self.fetchmany_size = size
        return self.rows[:size]


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.closed = True
        return False

    def cursor(self, *args, **kwargs):
        return self._cursor


@pytest.fixture
def fake_db(monkeypatch):
    """Install a fake ``mysql.connector.connect`` into tools.db_tools.

    Returns an ``install(...)`` callable that configures the fake and returns a
    handle exposing the cursor and the connection kwargs that were used.
    """
    import tools.db_tools as db_tools

    class Handle:
        cursor: FakeCursor
        connection: FakeConnection | None = None
        connect_kwargs: dict | None = None

    def install(rows=(), description=None, execute_error=None, connect_error=None):
        handle = Handle()
        handle.cursor = FakeCursor(rows=rows, description=description, execute_error=execute_error)

        def _connect(**kwargs):
            handle.connect_kwargs = kwargs
            if connect_error is not None:
                raise connect_error
            handle.connection = FakeConnection(handle.cursor)
            return handle.connection

        monkeypatch.setattr(db_tools, "connect", _connect)
        return handle

    return install
