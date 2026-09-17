"""Tests for tools/ragflow_tools.py client initialisation and answer/reference handling."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from ragflow_sdk.modules.chat import Chat
from ragflow_sdk.modules.session import Message

import tools.ragflow_tools as ragflow_tools
from tools.ragflow_tools import create_ask_delete, get_assistant_list


@pytest.fixture
def reset_client(monkeypatch):
    monkeypatch.setattr(ragflow_tools, "ragflow_client", None)


@pytest.fixture
def client(monkeypatch):
    fake = Mock()
    monkeypatch.setattr(ragflow_tools, "ragflow_client", fake)
    return fake


def _chat_with_stream(client, parts):
    session = Mock(id="session-id")
    session.ask.return_value = iter(parts)
    chat = Mock()
    chat.create_session.return_value = session
    client.list_chats.return_value = [chat]
    return chat, session


# --------------------------------------------------------------- _get_client --
def test_get_client_is_built_from_env_and_cached(reset_client, monkeypatch, test_env):
    monkeypatch.setenv("RAGFLOW_API_URL", test_env["RAGFLOW_API_URL"] + "/")
    first = ragflow_tools._get_client()
    assert isinstance(first, ragflow_tools._RAGFlowClient)
    assert first.api_url == f"{test_env['RAGFLOW_API_URL']}/api/v1"
    assert first.user_key == test_env["RAGFLOW_API_KEY"]
    assert ragflow_tools._get_client() is first


@pytest.mark.parametrize("env", [(None, "http://ragflow.test"), ("key", None), (None, None)])
def test_get_client_requires_both_settings(reset_client, monkeypatch, env):
    monkeypatch.setattr(ragflow_tools, "_load_ragflow_env", lambda: env)
    with pytest.raises(ValueError, match="RAGFLOW_API_KEY and RAGFLOW_API_URL"):
        ragflow_tools._get_client()


def test_sdk_requests_carry_authorization_header(monkeypatch):
    client = ragflow_tools._RAGFlowClient(api_key="test-key", base_url="http://ragflow.test")
    request = Mock()
    monkeypatch.setattr(ragflow_tools.requests, "request", request)
    client.get("/chats", params={"name": "x"})
    args, kwargs = request.call_args
    assert args == ("GET", "http://ragflow.test/api/v1/chats")
    assert kwargs["headers"] == client.authorization_header
    assert kwargs["params"] == {"name": "x"}


# -------------------------------------------------------- get_assistant_list --
def test_get_assistant_list_reports_no_assistants(client, monitor_calls):
    client.list_chats.return_value = []
    assert get_assistant_list.invoke({}) == "No available assistants"
    assert monitor_calls == [("RAGFlow assistant list tool: get_assistant_list", None)]


def test_get_assistant_list_reports_service_errors(client):
    client.list_chats.side_effect = ConnectionError("refused")
    out = get_assistant_list.invoke({})
    assert out.startswith("Failed to query assistant information") and "refused" in out


def test_get_assistant_list_handles_missing_dataset_metadata(client):
    client.list_chats.return_value = [Chat(client, {"name": "Bare Assistant"})]
    out = get_assistant_list.invoke({})
    assert out == "assistant name:Bare Assistant; description:; associated knowledge bases:  \n"


def test_get_assistant_list_prefers_kb_names_over_legacy_datasets(client):
    client.list_chats.return_value = [Chat(client, {
        "name": "Mixed", "kb_names": ["Current"], "datasets": [{"name": "Legacy"}]})]
    out = get_assistant_list.invoke({})
    assert "associated knowledge bases: Current" in out and "Legacy" not in out


# --------------------------------------------------------- create_ask_delete --
def test_create_ask_delete_reports_monitor_and_asks_by_name(client, monitor_calls):
    chat, session = _chat_with_stream(client, [SimpleNamespace(content="Answer")])
    assert create_ask_delete.invoke({"chat_name": "Drug Labels Assistant", "question": "Dose?"}) == "Answer"
    client.list_chats.assert_called_once_with(name="Drug Labels Assistant")
    chat.create_session.assert_called_once_with(name="temp_session_ask")
    session.ask.assert_called_once_with(question="Dose?", stream=True)
    assert monitor_calls == [("RAGFlow ask-assistant tool: create_ask_delete",
                              {"chat_name": "Drug Labels Assistant", "question": "Dose?"})]


def test_create_ask_delete_collects_sources_from_keywords_and_skips_malformed_references(client):
    chat, _ = _chat_with_stream(client, [
        Message(client, {"content": "Take ", "reference": "not-a-list"}),
        Message(client, {"content": "500mg", "reference": [
            "not-a-dict", {"document_keyword": "amoxil-label.pdf"}, {"chunk_id": "no-name"}]}),
        Message(client, {"content": "", "reference": [
            {"document_name": "nifedipine-label.pdf"}, {"document_keyword": "amoxil-label.pdf"}]}),
    ])
    out = create_ask_delete.invoke({"chat_name": "Drug Labels Assistant", "question": "Dose?"})
    assert out == "Take 500mg\n\nSources:\n- amoxil-label.pdf\n- nifedipine-label.pdf"
    chat.delete_sessions.assert_called_once_with(ids=["session-id"])


def test_create_ask_delete_reports_session_creation_failure_without_deleting(client):
    chat = Mock()
    chat.create_session.side_effect = RuntimeError("quota exceeded")
    client.list_chats.return_value = [chat]
    out = create_ask_delete.invoke({"chat_name": "X", "question": "Q"})
    assert out == "Question failed. Error: quota exceeded"
    chat.delete_sessions.assert_not_called()


def test_create_ask_delete_reports_lookup_failure(client):
    client.list_chats.side_effect = RuntimeError("401 Unauthorized")
    out = create_ask_delete.invoke({"chat_name": "X", "question": "Q"})
    assert out == "Question failed. Error: 401 Unauthorized"


def test_create_ask_delete_whitespace_only_answer_is_a_failure(client):
    chat, _ = _chat_with_stream(client, [SimpleNamespace(content="  \n")])
    out = create_ask_delete.invoke({"chat_name": "X", "question": "Q"})
    assert out == "Question failed: RAGFlow returned an empty answer."
    chat.delete_sessions.assert_called_once_with(ids=["session-id"])
