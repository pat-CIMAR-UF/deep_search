"""Tests for tools/tavily_tool.py with a fake Tavily client."""
import importlib
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tavily_tool():
    import tools.tavily_tool as mod

    return mod


def test_module_imports_without_api_key(monkeypatch):
    """Importing the tool module must not require TAVILY_API_KEY (same contract as gemini_tool)."""
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.setattr("dotenv.main.load_dotenv", lambda *a, **k: False)
    sys.modules.pop("tools.tavily_tool", None)
    try:
        importlib.import_module("tools.tavily_tool")
    finally:
        sys.modules.pop("tools.tavily_tool", None)


def test_tool_metadata(tavily_tool):
    t = tavily_tool.internet_search
    assert t.name == "internet_search"
    assert set(t.args) == {"query", "topic", "max_results", "include_raw_content"}
    assert t.args["topic"]["default"] == "general"
    assert set(t.args["topic"]["enum"]) == {"news", "finance", "general"}
    assert t.args["max_results"]["default"] == 5
    assert t.args["include_raw_content"]["default"] is False


def test_internet_search_forwards_arguments(tavily_tool, monkeypatch, monitor_calls):
    client = MagicMock()
    client.search.return_value = {"results": [{"title": "x"}]}
    monkeypatch.setattr(tavily_tool, "tavily_client", client, raising=False)

    out = tavily_tool.internet_search.invoke(
        {"query": "aspirin", "topic": "news", "max_results": 2, "include_raw_content": True}
    )
    assert out == {"results": [{"title": "x"}]}
    client.search.assert_called_once_with(
        query="aspirin", topic="news", max_results=2, include_raw_content=True
    )
    assert monitor_calls == [
        (
            "Internet Search Tool",
            {"query": "aspirin", "topic": "news", "max_results": 2, "include_raw_content": True},
        )
    ]


def test_internet_search_defaults(tavily_tool, monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(tavily_tool, "tavily_client", client, raising=False)
    tavily_tool.internet_search.invoke({"query": "aspirin"})
    client.search.assert_called_once_with(
        query="aspirin", topic="general", max_results=5, include_raw_content=False
    )


def test_internet_search_rejects_bad_topic(tavily_tool, monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(tavily_tool, "tavily_client", client, raising=False)
    with pytest.raises(Exception):
        tavily_tool.internet_search.invoke({"query": "aspirin", "topic": "sports"})
    client.search.assert_not_called()
