"""Shared fixtures for the deep_search unit-test harness.

All external services (MongoDB MCP, Gemini, Tavily, RAGFlow, the Qwen chat model) are
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
    "MONGODB_URI": "mongodb://mongo.test:27017",
    "MONGODB_DATABASE": "test_db",
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
# Fake MongoDB MCP session
# --------------------------------------------------------------------------- #
def make_tool_result(structured=None, text=None, is_error=False):
    """Build a CallToolResult like the one mongodb-mcp-server returns."""
    from mcp.types import CallToolResult, TextContent

    content = [TextContent(type="text", text=text)] if text is not None else []
    return CallToolResult(content=content, structured_content=structured, is_error=is_error)


@pytest.fixture
def fake_mcp(monkeypatch):
    """Replace ``tools.mongo_tools.call_mcp_tool`` with a recorder.

    Returns an ``install(...)`` callable that configures the canned result (or the
    exception to raise) and returns a handle exposing the recorded ``calls`` as
    ``(tool_name, arguments)`` tuples.
    """
    import tools.mongo_tools as mongo_tools

    class Handle:
        calls: list[tuple[str, dict]]

    def install(structured=None, text=None, is_error=False, error=None):
        handle = Handle()
        handle.calls = []
        result = make_tool_result(structured=structured, text=text, is_error=is_error)

        def _call(name, arguments, timeout=None):
            handle.calls.append((name, dict(arguments)))
            if error is not None:
                raise error
            return result

        monkeypatch.setattr(mongo_tools, "call_mcp_tool", _call)
        return handle

    return install
