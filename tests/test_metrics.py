"""Tests for agent/metrics.py and the opt-in usage accounting in run_deep_agent."""
import asyncio

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from langchain_core.tools import tool

from agent import main_agent
from agent.metrics import RunMetrics, UsageCallbackHandler
from api.context import get_run_metrics, reset_run_metrics, set_run_metrics
from tests.test_main_agent import install_model, session  # noqa: F401 - fixture re-export


def test_run_metrics_accumulates_and_serializes():
    m = RunMetrics()
    m.add_usage({"input_tokens": 10, "output_tokens": 5, "total_tokens": 15})
    m.add_usage(None)
    m.add_usage({"input_tokens": None, "output_tokens": 2})
    m.add_gemini_usage(100, 20)
    m.tool_calls["find_documents"] += 2
    m.tool_calls["task"] += 1
    m.subagent_calls["Database Query Agent"] += 1
    data = m.as_dict()
    assert (data["input_tokens"], data["output_tokens"], data["total_tokens"]) == (10, 7, 17)
    assert data["gemini_calls"] == 1 and data["gemini_input_tokens"] == 100 and data["gemini_output_tokens"] == 20
    assert data["tool_calls"] == {"find_documents": 2, "task": 1} and data["tool_call_count"] == 3
    assert data["subagent_calls"] == {"Database Query Agent": 1}


def test_callback_handler_reads_usage_and_tool_calls():
    m = RunMetrics()
    h = UsageCallbackHandler(m)
    h.on_chat_model_start({}, [[]])
    h.on_llm_end(LLMResult(generations=[[ChatGeneration(message=AIMessage(
        content="hi", usage_metadata={"input_tokens": 30, "output_tokens": 4, "total_tokens": 34}))]]))
    # Fallback to llm_output when the message carries no usage_metadata.
    h.on_llm_end(LLMResult(generations=[[ChatGeneration(message=AIMessage(content="x"))]],
                           llm_output={"token_usage": {"prompt_tokens": 7, "completion_tokens": 3}}))
    h.on_tool_start({"name": "ignored"}, "", name="task", inputs={"subagent_type": "RAGFlow Agent", "description": "d"})
    h.on_tool_start({"name": "find_documents"}, "{}")
    h.on_tool_start(None, "{}", name="count_documents")
    assert m.llm_calls == 1
    assert (m.input_tokens, m.output_tokens) == (37, 7)
    assert m.tool_calls == {"task": 1, "find_documents": 1, "count_documents": 1}
    assert m.subagent_calls == {"RAGFlow Agent": 1}


def test_run_deep_agent_counts_subagent_tools_and_tokens_when_metrics_installed(monkeypatch, session):
    @tool("list_collections", description="Test lookup")
    def lookup(query: str = "") -> str:
        return "drugs,inventory"
    spec = main_agent.database_query_agent
    monkeypatch.setitem(spec, "tools", [lookup])
    usage = {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110}
    install_model(monkeypatch, [
        AIMessage(content="", usage_metadata=usage, tool_calls=[{"name": "task", "args": {
            "description": "List collections", "subagent_type": spec["name"]}, "id": "d1", "type": "tool_call"}]),
        AIMessage(content="", usage_metadata=usage, tool_calls=[{"name": "list_collections", "args": {}, "id": "l1", "type": "tool_call"}]),
        AIMessage(content="Specialist says two collections", usage_metadata=usage),
        AIMessage(content="Two collections", usage_metadata=usage),
    ])
    metrics = RunMetrics()
    token = set_run_metrics(metrics)
    try:
        assert asyncio.run(main_agent.run_agent("How many collections?", [], "database")) == "Two collections"
    finally:
        reset_run_metrics(token)
    assert metrics.llm_calls == 4
    assert (metrics.input_tokens, metrics.output_tokens) == (400, 40)
    assert metrics.tool_calls["task"] == 1 and metrics.tool_calls["list_collections"] == 1
    assert metrics.subagent_calls == {spec["name"]: 1}
    assert get_run_metrics() is None


def test_run_deep_agent_without_metrics_adds_no_callbacks(monkeypatch, session):
    captured = {}
    class Graph:
        async def astream(self, payload, config=None, **kwargs):
            captured["config"] = config
            yield {"model": {"messages": [AIMessage(content="ok")]}}
    monkeypatch.setattr(main_agent, "main_agent", Graph())
    assert asyncio.run(main_agent.run_deep_agent("Hello", "plain-run")) == "ok"
    assert "callbacks" not in captured["config"]


def test_gemini_tool_records_usage_into_metrics(monkeypatch):
    import tools.gemini_tool as gemini_tool
    class Usage:
        prompt_token_count = 55
        candidates_token_count = 9
    class Response:
        text = "answer"
        candidates = []
        usage_metadata = Usage()
    class Models:
        def generate_content(self, **kwargs):
            return Response()
    class Client:
        models = Models()
    monkeypatch.setattr(gemini_tool, "_get_client", lambda: Client())
    metrics = RunMetrics()
    token = set_run_metrics(metrics)
    try:
        out = gemini_tool.internet_search.invoke({"query": "q"})
    finally:
        reset_run_metrics(token)
    assert out["answer"] == "answer"
    assert (metrics.gemini_calls, metrics.gemini_input_tokens, metrics.gemini_output_tokens) == (1, 55, 9)


def test_callback_records_delegation_and_evidence_events():
    m = RunMetrics()
    h = UsageCallbackHandler(m)
    h.on_tool_start({"name": "task"}, "{}", inputs={"subagent_type": "Network Search Agent", "description": "look up X"})
    h.on_tool_end("rows...", name="find_documents")
    h.on_tool_end("ignored", name="internet_search")
    from langchain_core.messages import ToolMessage
    h.on_tool_end(ToolMessage(content="42", tool_call_id="c1"), name="count_documents")
    assert m.events == [
        {"kind": "delegation", "subagent": "Network Search Agent", "description": "look up X"},
        {"kind": "tool_result", "tool": "find_documents", "output": "rows..."},
        {"kind": "tool_result", "tool": "count_documents", "output": "42"},
    ]
    assert m.events_of("tool_result")[0]["tool"] == "find_documents"
    assert m.as_dict()["events"][0]["kind"] == "delegation"


def test_gemini_and_ragflow_tools_record_events(monkeypatch):
    import tools.gemini_tool as gemini_tool
    import tools.ragflow_tools as ragflow_tools
    from types import SimpleNamespace

    class Web:
        def __init__(self, uri, title):
            self.uri, self.title = uri, title
    chunk = SimpleNamespace(web=Web("https://s.org", "S"))
    meta = SimpleNamespace(web_search_queries=["ran query"], grounding_chunks=[chunk])
    response = SimpleNamespace(text="grounded", candidates=[SimpleNamespace(grounding_metadata=meta)], usage_metadata=None)
    monkeypatch.setattr(gemini_tool, "_get_client", lambda: SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: response)))

    from tests.ragflow_fakes import FakeChat, FakeClient, completion
    chunk = {"id": "c1", "document_name": "d.txt", "content": "[[passage 1]] t", "similarity": "0.9"}
    client = FakeClient(datasets=[{"id": "ds-a", "name": "A"}], chats=[FakeChat("A-assistant", ["ds-a"])],
                        completion=completion("kb answer [ID:0]", [chunk, chunk, {"document_name": "d.txt"}]))
    monkeypatch.setattr(ragflow_tools, "_get_client", lambda: client)

    metrics = RunMetrics()
    token = set_run_metrics(metrics)
    try:
        gemini_tool.internet_search.invoke({"query": "q"})
        ragflow_tools.ask_knowledge_base.invoke({"knowledge_bases": "A", "question": "kb q"})
    finally:
        reset_run_metrics(token)
    kinds = [e["kind"] for e in metrics.events]
    assert kinds == ["internet_search", "ragflow_retrieval"]
    assert metrics.events[0]["search_queries"] == ["ran query"] and metrics.events[0]["answer"] == "grounded"
    assert metrics.events[1]["chunks"] == [{"document": "d.txt", "content": "[[passage 1]] t", "similarity": 0.9, "chunk_id": "c1"}]
    assert metrics.events[1]["answer"] == "kb answer [ID:0]"
    assert metrics.events[1]["assistant"] == "A-assistant" and metrics.events[1]["knowledge_bases"] == ["A"]
