"""Run the actual coordinator/specialist graphs with a scripted model."""
import asyncio
import importlib

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from agent import main_agent


class ScriptedToolModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


@pytest.mark.parametrize("mode,delegate,tool_name,spec_name", [
    ("database", "query_database", "list_sql_tables", "database_query_agent"),
    ("internet", "search_internet", "internet_search", "internet_search_agent"),
])
def test_coordinator_delegates_to_real_specialist_graph(monkeypatch, mode, delegate, tool_name, spec_name):
    calls = []
    @tool(tool_name, description="Test external lookup")
    def lookup(query: str = "") -> str:
        calls.append(tool_name)
        return "Verified result: 42"
    model = ScriptedToolModel(responses=[
        AIMessage(content="", tool_calls=[{"name": delegate, "args": {"query": "Look up the answer"}, "id": "delegate-1", "type": "tool_call"}]),
        AIMessage(content="", tool_calls=[{"name": tool_name, "args": {}, "id": "lookup-1", "type": "tool_call"}]),
        AIMessage(content="Specialist verified 42"),
        AIMessage(content="The answer is 42"),
    ])
    monkeypatch.setattr(importlib.import_module("agent.llm"), "llm", model)
    monkeypatch.setitem(getattr(main_agent, spec_name), "tools", [lookup])
    main_agent.build_agents.cache_clear()
    try:
        assert set(main_agent.build_agents()) == {"auto", "database", "internet"}
        result = asyncio.run(main_agent.run_agent("Look it up", [], "auto"))
        assert result == "The answer is 42"
        assert calls == [tool_name]
    finally:
        main_agent.build_agents.cache_clear()
