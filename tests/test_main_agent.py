"""Run the real DeepAgents graph with a scripted tool-calling model."""
import asyncio

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from agent import main_agent
from api.context import (get_session_context, get_thread_context, set_session_context,
                         reset_session_context, set_thread_context)
from tests.graph_fakes import install_model


@pytest.mark.parametrize("mode,tool_name,spec_name", [
    ("database", "list_collections", "database_query_agent"),
    ("internet", "internet_search", "internet_search_agent"),
    ("ragflow", "list_knowledge_bases", "knowledge_base_agent"),
])
def test_coordinator_delegates_to_real_specialist_graph(monkeypatch, graph_session, mode, tool_name, spec_name):
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
    assert calls == [(tool_name, "test-graph", str(graph_session))]


def test_file_tools_are_callable_from_coordinator(monkeypatch, graph_session):
    install_model(monkeypatch, [
        AIMessage(content="", tool_calls=[{"name": "generate_markdown", "args": {
            "content": "# Verified report", "filename": "report"}, "id": "write-1", "type": "tool_call"}]),
        AIMessage(content="Report saved."),
    ])
    assert asyncio.run(main_agent.run_agent("Write a report", [], "auto")) == "Report saved."
    assert (graph_session / "report.md").read_text() == "# Verified report"


def test_followup_replays_history_once(monkeypatch, graph_session):
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


def test_errors_propagate_and_context_is_reset(monkeypatch, graph_session):
    class FailingGraph:
        async def astream(self, *args, **kwargs):
            raise RuntimeError("provider failed")
            yield
    monkeypatch.setattr(main_agent, "main_agent", FailingGraph())
    with pytest.raises(RuntimeError, match="provider failed"):
        asyncio.run(main_agent.run_deep_agent("Hello", "inner-session"))
    assert get_thread_context() == "test-graph"
    assert get_session_context() == str(graph_session)


def test_empty_response_is_an_error(monkeypatch, graph_session):
    install_model(monkeypatch, [AIMessage(content="")])
    with pytest.raises(RuntimeError, match="empty answer"):
        asyncio.run(main_agent.run_agent("Hello", []))


def test_answer_text_joins_text_blocks_and_ignores_non_dict_items():
    assert main_agent.answer_text(AIMessage(content="plain")) == "plain"
    assert main_agent.answer_text(AIMessage(content=[
        {"type": "text", "text": "first"}, "ignored", {"type": "text", "text": "second"}, {"type": "image"},
    ])) == "first\nsecond\n"


@pytest.mark.parametrize("session_id", ["../escape", "with space", "", "a" * 81, "id;rm"])
def test_run_deep_agent_rejects_invalid_session_ids(monkeypatch, graph_session, session_id):
    monkeypatch.setattr(main_agent, "get_main_agent", lambda: pytest.fail("graph must not be built"))
    with pytest.raises(ValueError, match="Invalid conversation ID"):
        asyncio.run(main_agent.run_deep_agent("Hello", session_id))


def test_run_deep_agent_rejects_unknown_modes(monkeypatch, graph_session):
    monkeypatch.setattr(main_agent, "get_main_agent", lambda: pytest.fail("graph must not be built"))
    with pytest.raises(ValueError, match="Unknown agent mode"):
        asyncio.run(main_agent.run_deep_agent("Hello", "ok-session", mode="tavily"))


def test_run_agent_requires_a_thread_context():
    thread_token = set_thread_context(None)
    try:
        with pytest.raises(RuntimeError, match="conversation ID"):
            asyncio.run(main_agent.run_agent("Hello", []))
    finally:
        reset_session_context(set_session_context(None), thread_token)


def test_get_main_agent_builds_once(monkeypatch, graph_session):
    install_model(monkeypatch, [AIMessage(content="ok")])
    assert main_agent.get_main_agent() is main_agent.get_main_agent()


def test_non_auto_mode_appends_delegation_instruction(monkeypatch, graph_session):
    install_model(monkeypatch, [AIMessage(content="A"), AIMessage(content="B")])

    async def run():
        config = {"configurable": {"thread_id": "test-graph"}}
        await main_agent.run_agent("Question", [], "auto")
        state = await main_agent.get_main_agent().aget_state(config)
        auto_prompt = [m for m in state.values["messages"] if isinstance(m, HumanMessage)][-1].content
        await main_agent.run_agent("Question", [], "ragflow")
        state = await main_agent.get_main_agent().aget_state(config)
        ragflow_prompt = [m for m in state.values["messages"] if isinstance(m, HumanMessage)][-1].content
        return auto_prompt, ragflow_prompt

    auto_prompt, ragflow_prompt = asyncio.run(run())
    assert auto_prompt.startswith("Question")
    assert "[Working environment]" in auto_prompt
    assert "delegate research to" not in auto_prompt
    assert f"delegate research to '{main_agent.knowledge_base_agent['name']}'" in ragflow_prompt


def test_history_is_truncated_to_the_last_forty_messages(monkeypatch, graph_session):
    install_model(monkeypatch, [AIMessage(content="Latest")])
    history = []
    for i in range(25):
        history += [{"role": "user", "content": f"Q{i}"}, {"role": "assistant", "content": f"A{i}"}]

    async def run():
        await main_agent.run_agent("Now", history)
        state = await main_agent.get_main_agent().aget_state({"configurable": {"thread_id": "test-graph"}})
        return [m.content for m in state.values["messages"] if isinstance(m, HumanMessage)]

    users = asyncio.run(run())
    assert len(users) == 21
    assert users[0] == "Q5" and users[-2] == "Q24"
    assert users[-1].startswith("Now")


def test_delegation_and_final_answer_are_reported_to_monitor(monkeypatch, graph_session):
    from api.monitor import monitor
    reports = []
    monkeypatch.setattr(monitor, "report_assistant", lambda name, args=None: reports.append(("assistant", name, args)))
    monkeypatch.setattr(monitor, "report_task_result", lambda result: reports.append(("result", result)))
    monkeypatch.setattr(monitor, "report_session_dir", lambda path: reports.append(("dir", path)))
    monkeypatch.setitem(main_agent.database_query_agent, "tools", [])
    install_model(monkeypatch, [
        AIMessage(content="", tool_calls=[{"name": "task", "args": {
            "description": "Count drugs", "subagent_type": main_agent.database_query_agent["name"]},
            "id": "delegate-1", "type": "tool_call"}]),
        AIMessage(content="Specialist says 3"),
        AIMessage(content="There are 3 drugs"),
    ])
    assert asyncio.run(main_agent.run_agent("How many drugs?", [], "database")) == "There are 3 drugs"
    assert reports[0] == ("dir", str(graph_session))
    assert reports[1] == ("assistant", main_agent.database_query_agent["name"], {"description": "Count drugs"})
    assert reports[-1] == ("result", "There are 3 drugs")


def test_legacy_updated_directory_files_are_copied_into_the_session(monkeypatch, graph_session, tmp_path):
    root = tmp_path / "project"
    legacy = root / "updated" / "session_legacy-1"
    legacy.mkdir(parents=True)
    (legacy / "notes.txt").write_text("legacy upload", encoding="utf-8")
    (legacy / ".hidden").write_text("state", encoding="utf-8")
    (legacy / "nested").mkdir()
    (legacy / "link.txt").symlink_to(legacy / "notes.txt")
    monkeypatch.setattr(main_agent, "project_root_path", root)
    install_model(monkeypatch, [AIMessage(content="ok")])
    asyncio.run(main_agent.run_deep_agent("Hello", "legacy-1"))
    assert (graph_session / "notes.txt").read_text(encoding="utf-8") == "legacy upload"
    assert not (graph_session / ".hidden").exists()
    assert not (graph_session / "nested").exists()
    assert not (graph_session / "link.txt").exists()


def test_default_session_directory_is_created_under_output(monkeypatch, tmp_path):
    root = tmp_path / "project"
    monkeypatch.setattr(main_agent, "project_root_path", root)
    install_model(monkeypatch, [AIMessage(content="ok")])
    session_token = set_session_context(None)
    thread_token = set_thread_context(None)
    try:
        assert asyncio.run(main_agent.run_deep_agent("Hello", "fresh-1")) == "ok"
    finally:
        reset_session_context(session_token, thread_token)
    assert (root / "output" / "session_fresh-1").is_dir()
    assert get_session_context() is None and get_thread_context() is None
