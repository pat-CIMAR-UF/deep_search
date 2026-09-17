"""Tests for ragflow/: config, knowledge-base demo and chat-assistant demo."""
from unittest.mock import MagicMock, create_autospec

import pytest
from ragflow_sdk import RAGFlow
from ragflow_sdk.modules.chat import Chat
from ragflow_sdk.modules.dataset import DataSet
from ragflow_sdk.modules.session import Message, Session

import ragflow.chat_assistant_demo as chat_demo
import ragflow.knowledge_demo as kb_demo
from ragflow.rag_config import _load_ragflow_env


# -------------------------------------------------------------- rag_config --
def test_load_ragflow_env_reads_env(test_env):
    assert _load_ragflow_env() == (test_env["RAGFLOW_API_KEY"], test_env["RAGFLOW_API_URL"])


def test_load_ragflow_env_missing(monkeypatch):
    monkeypatch.delenv("RAGFLOW_API_KEY")
    monkeypatch.delenv("RAGFLOW_API_URL")
    assert _load_ragflow_env() == (None, None)


@pytest.mark.parametrize("mod", [kb_demo, chat_demo])
def test_module_client_configured_from_env(mod, test_env):
    client = mod.ragflow_client
    assert isinstance(client, RAGFlow)
    assert client.user_key == test_env["RAGFLOW_API_KEY"]
    assert client.api_url.startswith(test_env["RAGFLOW_API_URL"])


# ---------------------------------------------------------- knowledge_demo --
@pytest.fixture
def kb_client(monkeypatch):
    client = create_autospec(RAGFlow, instance=True)
    monkeypatch.setattr(kb_demo, "ragflow_client", client)
    return client


def test_create_knowledge_base_success(kb_client):
    kb_client.create_dataset.return_value = MagicMock(name="kb")
    kb_client.create_dataset.return_value.name = "kb1"

    out = kb_demo.create_knowledge_base("kb1", "desc")

    assert out == "Knowledge base created successfully: kb1"
    kb_client.create_dataset.assert_called_once()
    kwargs = kb_client.create_dataset.call_args.kwargs
    assert kwargs["name"] == "kb1"
    assert kwargs["description"] == "desc"
    assert kwargs.get("embedding_model")


def test_create_knowledge_base_failure_is_reported(kb_client):
    kb_client.create_dataset.side_effect = Exception("server down")
    out = kb_demo.create_knowledge_base("kb1", "desc")
    assert out == "Failed to create knowledge base: server down"


def test_upload_file_to_knowledge_base(kb_client, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.md"
    f1.write_bytes(b"alpha")
    f2.write_bytes(b"# beta")
    dataset = create_autospec(DataSet, instance=True)
    kb_client.list_datasets.return_value = [dataset]

    kb_demo.upload_file_to_knowledge_base("kb-id-1", [str(f1), str(f2)])

    kb_client.list_datasets.assert_called_once()
    assert kb_client.list_datasets.call_args.kwargs["id"] == "kb-id-1"
    dataset.upload_documents.assert_called_once()
    docs = dataset.upload_documents.call_args.args[0]
    assert [(d["display_name"], d["blob"]) for d in docs] == [("a.txt", b"alpha"), ("b.md", b"# beta")]


def test_upload_file_missing_file_raises(kb_client, tmp_path):
    kb_client.list_datasets.return_value = [create_autospec(DataSet, instance=True)]
    with pytest.raises(FileNotFoundError):
        kb_demo.upload_file_to_knowledge_base("kb-id-1", [str(tmp_path / "nope.txt")])


# ----------------------------------------------------- chat_assistant_demo --
def _chat(rag, name, description, datasets):
    return Chat(rag, {"id": f"id-{name}", "name": name, "description": description, "datasets": datasets})


@pytest.fixture
def chat_client(monkeypatch):
    client = create_autospec(RAGFlow, instance=True)
    monkeypatch.setattr(chat_demo, "ragflow_client", client)
    return client


def test_get_assistant_list_formats_every_chat(chat_client):
    chat_client.list_chats.return_value = [
        _chat(chat_client, "Legal", "law help", [{"name": "laws"}, {"name": "cases"}]),
        _chat(chat_client, "Pharma", "drug help", []),
    ]
    out = chat_demo.get_assistant_list()
    lines = out.splitlines()
    assert len(lines) == 2
    assert lines[0] == "assistant name:Legal; description:law help; associated knowledge bases: laws, cases "
    assert lines[1] == "assistant name:Pharma; description:drug help; associated knowledge bases:  "
    chat_client.list_chats.assert_called_once_with()


def test_get_assistant_list_empty(chat_client):
    chat_client.list_chats.return_value = []
    assert chat_demo.get_assistant_list() == ""


def test_ask_question_streams_and_cleans_up(chat_client):
    chat = create_autospec(Chat, instance=True)
    session = create_autospec(Session, instance=True)
    session.id = "sess-1"
    chat.create_session.return_value = session
    session.ask.return_value = iter(
        [Message(chat_client, {"content": "Hel"}), Message(chat_client, {"content": "Hello world"})]
    )
    chat_client.list_chats.return_value = [chat]

    out = chat_demo.ask_question("Legal", "hi?")

    assert out == "Hello world"
    chat_client.list_chats.assert_called_once_with(name="Legal")
    chat.create_session.assert_called_once()
    session.ask.assert_called_once_with(question="hi?", stream=True)
    chat.delete_sessions.assert_called_once_with(ids=["sess-1"])


def test_ask_question_empty_stream_returns_empty(chat_client):
    chat = create_autospec(Chat, instance=True)
    session = create_autospec(Session, instance=True)
    session.id = "s"
    chat.create_session.return_value = session
    session.ask.return_value = iter([])
    chat_client.list_chats.return_value = [chat]
    assert chat_demo.ask_question("Legal", "hi?") == ""
    chat.delete_sessions.assert_called_once_with(ids=["s"])
