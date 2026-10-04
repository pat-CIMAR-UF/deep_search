"""Tests for tools/ragflow_tools.py: client initialisation, knowledge-base listing, retrieval and answers."""
from unittest.mock import Mock

import pytest
import requests

import tools.ragflow_tools as ragflow_tools
from ragflow import service
from tests.ragflow_fakes import FakeChat, FakeClient, FakeResponse, completion
from tools.ragflow_tools import ask_knowledge_base, list_knowledge_bases, retrieve_chunks

HANDBOOK = {"id": "ds-handbook", "name": "handbook", "description": "Employee handbook", "document_count": 4,
            "chunk_count": 103, "embedding_model": "text-embedding-3-large@Azure"}
WIKI = {"id": "ds-wiki", "name": "rag-mini-wiki", "document_count": 1, "chunk_count": 469,
        "embedding_model": "text-embedding-3-large@Azure"}
LABEL_CHUNK = {"id": "c1", "document_name": "amoxil-label.pdf", "dataset_id": "ds-handbook", "similarity": "0.378",
               "content": "<table><caption>Table 1. Dosing</caption><tr><td>500 mg every 12 hours</td></tr></table>"}
# /retrieval chunks carry document_keyword and a string similarity (the SDK maps the former to document_name)
MANUAL_CHUNK = {"id": "c2", "document_keyword": "Midea U AC Installation Guide.pdf", "dataset_id": "ds-handbook",
                "similarity": "0.21", "content": "Use the thick window bracket."}


@pytest.fixture
def reset_client(monkeypatch):
    monkeypatch.setattr(ragflow_tools, "ragflow_client", None)


def install(monkeypatch, client: FakeClient) -> FakeClient:
    monkeypatch.setattr(ragflow_tools, "ragflow_client", client)
    return client


# --------------------------------------------------------------- _get_client --
def test_get_client_is_built_from_env_and_cached(reset_client, monkeypatch, test_env):
    monkeypatch.setenv("RAGFLOW_BASE_URL", test_env["RAGFLOW_BASE_URL"] + "/")
    first = ragflow_tools._get_client()
    assert isinstance(first, service.RAGFlowClient)
    assert first.api_url == f"{test_env['RAGFLOW_BASE_URL']}/api/v1"
    assert first.user_key == test_env["RAGFLOW_API_KEY"]
    assert ragflow_tools._get_client() is first


def test_get_client_falls_back_to_legacy_api_url(reset_client, monkeypatch):
    monkeypatch.delenv("RAGFLOW_BASE_URL")
    monkeypatch.setenv("RAGFLOW_API_URL", "http://legacy.test:9380")
    assert ragflow_tools._get_client().api_url == "http://legacy.test:9380/api/v1"


def test_get_client_defaults_to_the_tunnel_port(reset_client, monkeypatch):
    monkeypatch.delenv("RAGFLOW_BASE_URL")
    monkeypatch.delenv("RAGFLOW_API_URL", raising=False)
    assert ragflow_tools._get_client().api_url == "http://localhost:8080/api/v1"


def test_missing_key_is_reported_on_use(reset_client, monkeypatch):
    monkeypatch.setenv("RAGFLOW_API_KEY", "")
    with pytest.raises(service.RAGFlowError, match="RAGFLOW_API_KEY is not set"):
        ragflow_tools._get_client()
    assert list_knowledge_bases.invoke({}) == ("Failed to list knowledge bases: RAGFLOW_API_KEY is not set: "
                                               "put it in .env (see .env.example).")


def test_malformed_key_is_rejected_without_echoing_it(reset_client, monkeypatch):
    monkeypatch.setenv("RAGFLOW_API_KEY", "ragflow-secret\nX-Injected: 1")
    out = list_knowledge_bases.invoke({})
    assert out == "Failed to list knowledge bases: RAGFLOW_API_KEY contains whitespace or line breaks; fix it in .env."
    assert "secret" not in out


@pytest.mark.parametrize("call,method,path", [
    (lambda c: c.get("/chats", params={"page": 1}), "GET", "/chats"),
    (lambda c: c.post("/chat/completions", json={"q": 1}), "POST", "/chat/completions"),
    (lambda c: c.delete("/chats/id/sessions", json={"ids": ["s"]}), "DELETE", "/chats/id/sessions"),
    (lambda c: c.put("/datasets/id", json={"name": "x"}), "PUT", "/datasets/id"),
    (lambda c: c.patch("/datasets/id/documents/d", json={"chunk_method": "naive"}), "PATCH", "/datasets/id/documents/d"),
])
def test_sdk_requests_carry_authorization_header_and_timeouts(monkeypatch, call, method, path):
    client = service.RAGFlowClient(api_key="test-key", base_url="http://ragflow.test")
    request = Mock()
    monkeypatch.setattr(service.requests, "request", request)
    call(client)
    args, kwargs = request.call_args
    assert args == (method, "http://ragflow.test/api/v1" + path)
    assert kwargs["headers"] == client.authorization_header
    assert kwargs["timeout"] == (10, 120)


# ------------------------------------------------------- list_knowledge_bases --
def test_list_knowledge_bases_reports_none(monkeypatch, monitor_calls):
    install(monkeypatch, FakeClient())
    assert list_knowledge_bases.invoke({}) == "No knowledge bases available"
    assert monitor_calls == [("RAGFlow knowledge-base list tool: list_knowledge_bases", None)]


def test_list_knowledge_bases_describes_datasets_and_linked_assistants(monkeypatch):
    install(monkeypatch, FakeClient(datasets=[HANDBOOK, WIKI], chats=[
        FakeChat("test", ["ds-handbook"]), FakeChat("handbook+rag-mini-wiki-assistant", ["ds-handbook", "ds-wiki"])]))
    monkeypatch.setenv("RAGFLOW_DATASET", "handbook")
    lines = list_knowledge_bases.invoke({}).splitlines()
    assert lines[0] == ("knowledge base: handbook; description: Employee handbook; documents: 4; chunks: 103; "
                       "embedding model: text-embedding-3-large@Azure; assistants: test, handbook+rag-mini-wiki-assistant")
    assert lines[1] == ("knowledge base: rag-mini-wiki; description: ; documents: 1; chunks: 469; "
                       "embedding model: text-embedding-3-large@Azure; assistants: handbook+rag-mini-wiki-assistant")
    assert lines[2] == "default when no knowledge base is given (RAGFLOW_DATASET): handbook"


def test_list_knowledge_bases_points_at_the_tunnel_when_unreachable(monkeypatch):
    client = install(monkeypatch, FakeClient())
    client.list_errors["datasets"] = requests.ConnectionError("refused")
    assert list_knowledge_bases.invoke({}) == ("Failed to list knowledge bases: Cannot reach RAGFlow at "
                                               "http://ragflow.test:8080/api/v1: is the SSH tunnel to the RAGFlow host "
                                               "running? (see README)")


def test_list_knowledge_bases_reports_service_errors(monkeypatch):
    client = install(monkeypatch, FakeClient(datasets=[HANDBOOK]))
    client.list_errors["chats"] = RuntimeError("401 Unauthorized")
    assert list_knowledge_bases.invoke({}) == "Failed to list knowledge bases: 401 Unauthorized"


# ------------------------------------------------------------ retrieve_chunks --
def test_retrieve_chunks_formats_matches_and_records_the_event(monkeypatch, monitor_calls):
    from agent.metrics import RunMetrics
    from api.context import reset_run_metrics, set_run_metrics
    client = install(monkeypatch, FakeClient(datasets=[HANDBOOK, WIKI], chunks=[LABEL_CHUNK, MANUAL_CHUNK]))
    metrics = RunMetrics()
    token = set_run_metrics(metrics)
    try:
        out = retrieve_chunks.invoke({"knowledge_bases": "handbook, rag-mini-wiki", "question": "dose", "top": 50})
    finally:
        reset_run_metrics(token)
    assert client.retrievals == [(["ds-handbook", "ds-wiki"], "dose", 20)]
    assert out == ("[1] amoxil-label.pdf (similarity 0.38)\n" + LABEL_CHUNK["content"] +
                   "\n\n[2] Midea U AC Installation Guide.pdf (similarity 0.21)\nUse the thick window bracket.")
    assert monitor_calls == [("RAGFlow retrieval tool: retrieve_chunks",
                              {"knowledge_bases": "handbook, rag-mini-wiki", "question": "dose", "top": 50})]
    assert metrics.events == [{"kind": "ragflow_retrieval", "assistant": "", "knowledge_bases": ["handbook", "rag-mini-wiki"],
                               "question": "dose", "answer": "", "chunks": [
                                   {"document": "amoxil-label.pdf", "content": LABEL_CHUNK["content"], "similarity": 0.378, "chunk_id": "c1"},
                                   {"document": "Midea U AC Installation Guide.pdf", "content": "Use the thick window bracket.",
                                    "similarity": 0.21, "chunk_id": "c2"}]}]


def test_retrieve_chunks_reports_no_matches(monkeypatch):
    install(monkeypatch, FakeClient(datasets=[HANDBOOK]))
    assert retrieve_chunks.invoke({"knowledge_bases": "handbook", "question": "x"}) == "No matching chunks."


def test_retrieve_chunks_names_unknown_knowledge_bases(monkeypatch):
    install(monkeypatch, FakeClient(datasets=[HANDBOOK]))
    assert retrieve_chunks.invoke({"knowledge_bases": "Drug Labels", "question": "x"}) == (
        "Retrieval failed: Knowledge base not found: Drug Labels. Available: handbook")


def test_retrieve_chunks_without_names_uses_the_default_or_explains(monkeypatch):
    client = install(monkeypatch, FakeClient(datasets=[HANDBOOK, WIKI], chunks=[MANUAL_CHUNK]))
    assert retrieve_chunks.invoke({"knowledge_bases": "", "question": "x"}) == (
        "Retrieval failed: No knowledge base given and RAGFLOW_DATASET is not set. Available: handbook, rag-mini-wiki")
    assert retrieve_chunks.invoke({"question": "x"}).startswith("Retrieval failed: No knowledge base given")
    monkeypatch.setenv("RAGFLOW_DATASET", "rag-mini-wiki")
    assert retrieve_chunks.invoke({"question": "x"}).startswith("[1] Midea")
    assert client.retrievals[-1] == (["ds-wiki"], "x", 3)


def test_knowledge_bases_accepts_a_list_and_drops_repeats(monkeypatch):
    client = install(monkeypatch, FakeClient(datasets=[HANDBOOK, WIKI], chunks=[MANUAL_CHUNK],
                                             chats=[FakeChat("test", ["ds-handbook"])],
                                             completion=completion("Answer", [])))
    retrieve_chunks.invoke({"knowledge_bases": ["handbook", "rag-mini-wiki", "handbook"], "question": "x"})
    assert client.retrievals[-1] == (["ds-handbook", "ds-wiki"], "x", 3)
    assert ask_knowledge_base.invoke({"knowledge_bases": "handbook, handbook", "question": "Q"}) == "Answer"
    assert client.created_chats == []  # the existing exact-set assistant is reused, no "handbook+handbook-assistant"
    assert client.posts[-1][1]["chat_id"] == "id-test"


# --------------------------------------------------------- ask_knowledge_base --
def test_ask_reuses_the_exact_assistant_and_cites_sources(monkeypatch, monitor_calls):
    from agent.metrics import RunMetrics
    from api.context import reset_run_metrics, set_run_metrics
    exact = FakeChat("test", ["ds-handbook"])
    both = FakeChat("handbook+rag-mini-wiki-assistant", ["ds-handbook", "ds-wiki"])
    duplicate = dict(LABEL_CHUNK)  # multi-dataset assistants repeat chunks; events dedupe by id
    client = install(monkeypatch, FakeClient(datasets=[HANDBOOK, WIKI], chats=[both, exact], completion=completion(
        "Take 500 mg every 12 hours [ID:0]. Not in docs [ID:7]. ", [LABEL_CHUNK, MANUAL_CHUNK, duplicate])))
    question = "What is the adult dose of amoxicillin? " * 3
    metrics = RunMetrics()
    token = set_run_metrics(metrics)
    try:
        out = ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": question})
    finally:
        reset_run_metrics(token)
    assert out == ("Take 500 mg every 12 hours [ID:0]. Not in docs [ID:7].\n\nSources:\n"
                   '[ID:0] amoxil-label.pdf — "Table 1. Dosing 500 mg every 12 hours"')
    assert exact.created == [question[:64]] and exact.deleted == [["session-1"]]
    assert both.created == [] and client.created_chats == []
    assert client.posts == [("/chat/completions", {"chat_id": "id-test", "session_id": "session-1", "stream": False,
                                                  "messages": [{"role": "user", "content": question}]})]
    assert monitor_calls == [("RAGFlow ask tool: ask_knowledge_base", {"knowledge_bases": "handbook", "question": question})]
    event = metrics.events[0]
    assert event["assistant"] == "test" and event["knowledge_bases"] == ["handbook"]
    assert event["answer"] == "Take 500 mg every 12 hours [ID:0]. Not in docs [ID:7]."
    assert [c["chunk_id"] for c in event["chunks"]] == ["c1", "c2"]


def test_ask_creates_a_combined_assistant_when_none_matches(monkeypatch):
    client = install(monkeypatch, FakeClient(datasets=[HANDBOOK, WIKI], chats=[FakeChat("test", ["ds-handbook"])],
                                             completion=completion("Answer [ID:0]", [MANUAL_CHUNK])))
    out = ask_knowledge_base.invoke({"knowledge_bases": "handbook,rag-mini-wiki", "question": "Q"})
    assert out.startswith("Answer [ID:0]\n\nSources:\n[ID:0] Midea U AC Installation Guide.pdf")
    created, = client.created_chats
    assert created.name == "handbook+rag-mini-wiki-assistant" and created.dataset_ids == ["ds-handbook", "ds-wiki"]
    assert created.deleted == [["session-1"]]


def test_ask_keeps_answers_that_merely_mention_errors(monkeypatch):
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[FakeChat("test", ["ds-handbook"])],
                                    completion=completion("**Error handling** is covered in section 3 [ID:0].", [MANUAL_CHUNK])))
    out = ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Q"})
    assert out.startswith("**Error handling** is covered in section 3 [ID:0].\n\nSources:\n[ID:0] Midea")


def test_ask_lists_documents_when_the_answer_has_no_markers(monkeypatch):
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[FakeChat("test", ["ds-handbook"])], completion=completion(
        "Plain answer", [LABEL_CHUNK, MANUAL_CHUNK, {"document_keyword": "amoxil-label.pdf"}, "not-a-dict"])))
    out = ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Q"})
    assert out == "Plain answer\n\nSources:\n- amoxil-label.pdf\n- Midea U AC Installation Guide.pdf"


def test_ask_accepts_id_keyed_reference_chunks(monkeypatch):
    payload = completion("See [ID:1]", [])
    payload["data"]["reference"]["chunks"] = {"c1": LABEL_CHUNK, "c2": MANUAL_CHUNK}
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[FakeChat("test", ["ds-handbook"])], completion=payload))
    assert ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Q"}).endswith(
        '[ID:1] Midea U AC Installation Guide.pdf — "Use the thick window bracket."')


@pytest.mark.parametrize("payload,expected", [
    (completion("", [], code=102, message="The dataset has no embedding model"),
     "Question failed: The dataset has no embedding model"),
    (completion("  \n", [LABEL_CHUNK]), "Question failed: RAGFlow returned an empty answer."),
    (completion("**ERROR**: Authentication failed for model gpt-x: invalid api key", []),
     "Question failed: RAGFlow assistant error: Authentication failed for model gpt-x: invalid api key"),
    (completion("Partial text\n**ERROR**: model unavailable", [LABEL_CHUNK]),
     "Question failed: RAGFlow assistant error: model unavailable"),
    (FakeResponse(None, text='data:{"code": 500, "message": "required argument are missing: messages", "data": {}}'),
     "Question failed: required argument are missing: messages"),
    (FakeResponse(None, status_code=502, text="<html>Bad Gateway</html>"),
     "Question failed: RAGFlow returned an unexpected response (HTTP 502)."),
])
def test_ask_reports_server_failures_and_still_deletes_the_session(monkeypatch, payload, expected):
    chat = FakeChat("test", ["ds-handbook"])
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[chat], completion=payload))
    assert ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Q"}) == expected
    assert chat.deleted == [["session-1"]]


def test_ask_reports_session_creation_failure_without_deleting(monkeypatch):
    chat = FakeChat("test", ["ds-handbook"], fail_create=RuntimeError("quota exceeded"))
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[chat]))
    assert ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Q"}) == "Question failed: quota exceeded"
    assert chat.deleted == []


@pytest.mark.parametrize("error", [requests.ConnectionError("refused"), requests.ConnectTimeout("connect timed out")])
def test_ask_points_at_the_tunnel_when_the_completion_cannot_connect(monkeypatch, error):
    chat = FakeChat("test", ["ds-handbook"])
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[chat], completion=error))
    out = ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Q"})
    assert out == ("Question failed: Cannot reach RAGFlow at http://ragflow.test:8080/api/v1: is the SSH tunnel to the "
                   "RAGFlow host running? (see README)")
    assert chat.deleted == [["session-1"]]


def test_ask_reports_timeouts(monkeypatch):
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[FakeChat("test", ["ds-handbook"])],
                                    completion=requests.ReadTimeout("slow")))
    assert ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Q"}) == (
        "Question failed: RAGFlow did not respond within 120 seconds.")


def test_ask_keeps_the_answer_when_session_deletion_fails(monkeypatch):
    chat = FakeChat("test", ["ds-handbook"], fail_delete=RuntimeError("gone"))
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[chat], completion=completion("Fine", [])))
    assert ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Q"}) == "Fine"


def test_ask_names_unknown_knowledge_bases_before_touching_assistants(monkeypatch):
    chat = FakeChat("test", ["ds-handbook"])
    install(monkeypatch, FakeClient(datasets=[HANDBOOK], chats=[chat]))
    assert ask_knowledge_base.invoke({"knowledge_bases": "Crib Assembly", "question": "Q"}) == (
        "Question failed: Knowledge base not found: Crib Assembly. Available: handbook")
    assert chat.created == []
