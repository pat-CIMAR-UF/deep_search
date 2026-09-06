"""Run the real DeepAgents graph with a scripted tool-calling model."""
import asyncio
import importlib

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from agent import main_agent
from api.context import (get_session_context, get_thread_context, set_session_context,
                         reset_session_context, set_thread_context)


class ScriptedToolModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self

    def get_num_tokens_from_messages(self, messages, tools=None):
        return sum(len(str(message.content)) // 4 for message in messages)


@pytest.fixture
def session(tmp_path):
    a = set_session_context(str(tmp_path))
    b = set_thread_context("test-graph")
    yield tmp_path
    reset_session_context(a, b)


def install_model(monkeypatch, responses):
    model = ScriptedToolModel(responses=responses)
    monkeypatch.setattr(importlib.import_module("agent.llm"), "llm", model)
    monkeypatch.setattr(main_agent, "main_agent", None)
    return model


@pytest.mark.parametrize("mode,tool_name,spec_name", [
    ("database", "list_sql_tables", "database_query_agent"),
    ("internet", "internet_search", "internet_search_agent"),
    ("ragflow", "get_assistant_list", "knowledge_base_agent"),
])
def test_coordinator_delegates_to_real_specialist_graph(monkeypatch, session, mode, tool_name, spec_name):
    calls = []
    @tool(tool_name, description="Test external lookup")
    def lookup(query: str = "") -> str:
        calls.append((tool_name, get_thread_context(), get_session_context()))
        return "Verified result: 42"
    spec = getattr(main_agent, spec_name)
    monkeypatch.setitem(spec, "tools", [lookup])
    install_model(monkeypatch, [
        AIMessage(content="", tool_calls=[{"name": "task", "args": {
            "description": "Look up the answer", "subagent_type": spec['name']},
            "id": "delegate-1", "type": "tool_call"}]),
        AIMessage(content="", tool_calls=[{"name": tool_name, "args": {}, "id": "lookup-1", "type": "tool_call"}]),
        AIMessage(content="Specialist verified 42"),
        AIMessage(content="The answer is 42"),
    ])
    result = asyncio.run(main_agent.run_agent("Look it up", [], mode))
    assert result == "The answer is 42"
    assert calls == [(tool_name, "test-graph", str(session))]


def test_file_tools_are_callable_from_coordinator(monkeypatch, session):
    install_model(monkeypatch, [
        AIMessage(content="", tool_calls=[{"name": "generate_markdown", "args": {
            "content": "# Verified report", "filename": "report"}, "id": "write-1", "type": "tool_call"}]),
        AIMessage(content="Report saved."),
    ])
    assert asyncio.run(main_agent.run_agent("Write a report", [], "auto")) == "Report saved."
    assert (session / "report.md").read_text() == "# Verified report"


def test_followup_replays_history_once(monkeypatch, session):
    install_model(monkeypatch, [AIMessage(content="First answer"), AIMessage(content="Second answer")])
    async def run():
        await main_agent.run_agent("First question", [])
        await main_agent.run_agent("Second question", [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
        ])
        state = await main_agent.get_main_agent().aget_state({"configurable": {"thread_id": "test-graph"}})
        users = [m for m in state.values['messages'] if isinstance(m, HumanMessage)]
        assert len(users) == 2
        assert users[0].content == "First question"
    asyncio.run(run())


def test_errors_propagate_and_context_is_reset(monkeypatch, session):
    class FailingGraph:
        async def astream(self, *args, **kwargs):
            raise RuntimeError("provider failed")
            yield
    monkeypatch.setattr(main_agent, "main_agent", FailingGraph())
    with pytest.raises(RuntimeError, match="provider failed"):
        asyncio.run(main_agent.run_deep_agent("Hello", "inner-session"))
    assert get_thread_context() == "test-graph"
    assert get_session_context() == str(session)


def test_empty_response_is_an_error(monkeypatch, session):
    install_model(monkeypatch, [AIMessage(content="")])
    with pytest.raises(RuntimeError, match="empty answer"):
        asyncio.run(main_agent.run_agent("Hello", []))
