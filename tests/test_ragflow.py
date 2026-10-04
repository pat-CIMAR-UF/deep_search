"""Tests for ragflow/: settings, the service layer and the command-line client."""
from pathlib import Path

import pytest
import requests
from ragflow_sdk.modules.dataset import DataSet

from ragflow import cli, rag_config, service
from ragflow.rag_config import RAGFlowSettings, dataset_names, load_ragflow_settings
from tests.ragflow_fakes import FakeChat, FakeClient, FakeResponse, completion

HANDBOOK = {"id": "ds-handbook", "name": "handbook", "document_count": 4, "chunk_count": 103, "embedding_model": "emb"}
WIKI = {"id": "ds-wiki", "name": "rag-mini-wiki", "document_count": 1, "chunk_count": 469, "embedding_model": "emb"}


# -------------------------------------------------------------- rag_config --
def test_settings_prefer_base_url_and_strip_trailing_slash(monkeypatch, test_env):
    monkeypatch.setenv("RAGFLOW_BASE_URL", "http://tunnel.test:8080/")
    monkeypatch.setenv("RAGFLOW_API_URL", "http://legacy.test:9380")
    monkeypatch.setenv("RAGFLOW_DATASET", " handbook , rag-mini-wiki ,, ")
    settings = load_ragflow_settings()
    assert settings == RAGFlowSettings(api_key=test_env["RAGFLOW_API_KEY"], base_url="http://tunnel.test:8080",
                                       default_datasets=["handbook", "rag-mini-wiki"])


def test_settings_fall_back_to_legacy_url_then_default(monkeypatch):
    monkeypatch.delenv("RAGFLOW_BASE_URL")
    monkeypatch.setenv("RAGFLOW_API_URL", "http://legacy.test:9380/")
    assert load_ragflow_settings().base_url == "http://legacy.test:9380"
    monkeypatch.delenv("RAGFLOW_API_URL")
    monkeypatch.setenv("RAGFLOW_API_KEY", "")
    settings = load_ragflow_settings()
    assert settings.base_url == rag_config.DEFAULT_BASE_URL == "http://localhost:8080"
    assert settings.api_key is None and settings.default_datasets == []


@pytest.mark.parametrize("value,expected", [(None, []), ("", []), ("a", ["a"]), (" a , b ,, ", ["a", "b"])])
def test_dataset_names(value, expected):
    assert dataset_names(value) == expected


def test_connect_requires_a_clean_key():
    with pytest.raises(service.RAGFlowError, match="RAGFLOW_API_KEY is not set"):
        service.connect(RAGFlowSettings(api_key=None, base_url="http://x"))
    with pytest.raises(service.RAGFlowError, match="whitespace or line breaks"):
        service.connect(RAGFlowSettings(api_key="k\r\nX: y", base_url="http://x"))
    client = service.connect(RAGFlowSettings(api_key=" k ", base_url="http://x"))
    assert isinstance(client, service.RAGFlowClient) and client.api_url == "http://x/api/v1"
    assert client.authorization_header == {"Authorization": "Bearer k"}


# ------------------------------------------------------------ dataset lookup --
def test_get_datasets_matches_names_locally_and_keeps_order():
    client = FakeClient(datasets=[HANDBOOK, WIKI])
    assert [d.name for d in service.get_datasets(client, ["rag-mini-wiki", "handbook"])] == ["rag-mini-wiki", "handbook"]
    with pytest.raises(service.KnowledgeBaseNotFound) as info:
        service.get_datasets(client, ["handbook", "Drug Labels", "Crib"])
    assert info.value.missing == ["Drug Labels", "Crib"] and info.value.available == ["handbook", "rag-mini-wiki"]
    assert str(info.value) == "Knowledge base not found: Drug Labels, Crib. Available: handbook, rag-mini-wiki"


def test_listings_follow_pages():
    datasets = [{"id": f"ds-{i}", "name": f"kb{i}"} for i in range(250)]
    client = FakeClient(datasets=datasets, chats=[FakeChat(f"c{i}", [f"ds-{i}"]) for i in range(150)])
    assert len(service.datasets_by_name(client)) == 250
    assert len(service.list_chats(client)) == 150
    # an assistant beyond the first page is still found, so no duplicate gets created on the server
    assert service.get_chat(client, [DataSet(client, {"id": "ds-149", "name": "kb149"})]).name == "c149"
    assert client.created_chats == []


def test_resolve_datasets_accepts_strings_lists_and_defaults():
    client = FakeClient(datasets=[HANDBOOK, WIKI])
    settings = RAGFlowSettings(api_key="k", base_url="http://x", default_datasets=["rag-mini-wiki"])
    assert [d.id for d in service.resolve_datasets(client, "handbook,rag-mini-wiki", settings)] == ["ds-handbook", "ds-wiki"]
    assert [d.id for d in service.resolve_datasets(client, ["handbook", ""], settings)] == ["ds-handbook"]
    assert [d.id for d in service.resolve_datasets(client, "handbook,handbook, handbook", settings)] == ["ds-handbook"]
    assert [d.id for d in service.resolve_datasets(client, "", settings)] == ["ds-wiki"]
    with pytest.raises(service.RAGFlowError, match="RAGFLOW_DATASET is not set. Available: handbook, rag-mini-wiki"):
        service.resolve_datasets(client, None, RAGFlowSettings(api_key="k", base_url="http://x"))


def test_describe_knowledge_bases_links_assistants():
    client = FakeClient(datasets=[HANDBOOK, WIKI], chats=[FakeChat("test", ["ds-handbook"]),
                                                         FakeChat("both", ["ds-handbook", "ds-wiki"])])
    bases = service.describe_knowledge_bases(client)
    assert [(kb.name, kb.document_count, kb.chunk_count, kb.assistants) for kb in bases] == [
        ("handbook", 4, 103, ["test", "both"]), ("rag-mini-wiki", 1, 469, ["both"])]


# ---------------------------------------------------------------- assistants --
def test_get_chat_requires_an_exact_dataset_set():
    client = FakeClient(datasets=[HANDBOOK, WIKI], chats=[FakeChat("both", ["ds-wiki", "ds-handbook"])])
    handbook, wiki = client.datasets
    assert service.get_chat(client, [handbook, wiki]).name == "both"
    created = service.get_chat(client, [handbook])
    assert created.name == "handbook-assistant" and created.dataset_ids == ["ds-handbook"]
    assert client.created_chats == [created]
    assert service.get_chat(client, [handbook]) is created


# ------------------------------------------------------------------- answers --
def test_parse_references_keeps_positions_and_tolerates_shapes():
    refs = service.parse_references({"chunks": [
        {"id": "a", "document_name": "x.pdf", "content": "one", "similarity": "0.5", "dataset_id": "d"},
        "junk", {"document_keyword": "y.pdf"}]})
    assert [(r.index, r.document, r.content, r.similarity, r.chunk_id, r.dataset_id) for r in refs] == [
        (0, "x.pdf", "one", 0.5, "a", "d"), (1, "", "", None, "", ""), (2, "y.pdf", "", None, "", "")]
    assert service.parse_references([{"document_name": "bare.pdf", "content": "c"}])[0].document == "bare.pdf"
    assert [r.document for r in service.parse_references({"chunks": {"k1": {"document_name": "m.pdf"}}})] == ["m.pdf"]
    assert service.parse_references(None) == [] and service.parse_references({"chunks": "x"}) == []


def test_answer_citations_sources_and_deduplication():
    refs = service.parse_references([
        {"id": "c1", "document_name": "a.pdf", "content": "<table><tr><td>A1</td></tr></table>"},
        {"id": "c2", "document_name": "b.pdf", "content": "B"},
        {"id": "c1", "document_name": "a.pdf", "content": "<table><tr><td>A1</td></tr></table>"},
        "junk"])
    answer = service.Answer("Uses [ID:2] then [ID:0] and [ID:9]", refs)
    assert [r.index for r in answer.cited] == [0, 2]
    assert answer.sources == ["a.pdf"]
    assert [r.chunk_id for r in answer.unique_references()] == ["c1", "c2"]
    assert answer.cited[0].snippet == "A1"
    assert service.Answer("no markers", refs).sources == ["a.pdf", "b.pdf"]


def test_snippet_strips_tags_and_truncates():
    assert service.snippet("<p>Hello</p>\n<b>world</b>") == "Hello world"
    assert service.snippet("Patients &gt; 3 Months &amp; older") == "Patients > 3 Months & older"
    assert service.snippet("CrCl < 30 mL/min and > 3 months, <40 kg") == "CrCl < 30 mL/min and > 3 months, <40 kg"
    assert service.snippet("<td>cell</td><br/><TABLE border=1>x</TABLE>") == "cell x"
    long = "x" * 150
    assert service.snippet(long) == "x" * 100 + "…"
    assert service.snippet(None) == ""


def test_ask_posts_to_the_v1_completion_endpoint_and_cleans_up():
    chat = FakeChat("test", ["ds-handbook"])
    client = FakeClient(datasets=[HANDBOOK], chats=[chat], completion=completion("Answer [ID:0]", [
        {"id": "c1", "document_name": "a.pdf", "content": "text", "similarity": "0.4"}]))
    answer = service.ask(client, client.datasets, "Why?")
    assert answer.content == "Answer [ID:0]" and answer.assistant == "test" and answer.session_name == "Why?"
    assert answer.cited[0].document == "a.pdf" and answer.cited[0].similarity == 0.4
    assert client.posts == [("/chat/completions", {"chat_id": "id-test", "session_id": "session-1", "stream": False,
                                                  "messages": [{"role": "user", "content": "Why?"}]})]
    assert chat.created == ["Why?"] and chat.deleted == [["session-1"]]


def test_ask_raises_on_server_errors_and_empty_answers():
    chat = FakeChat("test", ["ds-handbook"])
    client = FakeClient(datasets=[HANDBOOK], chats=[chat], completion=completion("", [], code=102, message="no model"))
    with pytest.raises(service.RAGFlowError, match="no model"):
        service.ask(client, client.datasets, "Q")
    client.completion = completion(" ", [])
    with pytest.raises(service.RAGFlowError, match="empty answer"):
        service.ask(client, client.datasets, "Q")
    client.completion = {"code": 0, "data": None}
    with pytest.raises(service.RAGFlowError, match="no data"):
        service.ask(client, client.datasets, "Q")
    client.completion = completion("**ERROR**: quota exceeded", [])
    with pytest.raises(service.RAGFlowError, match="RAGFlow assistant error: quota exceeded"):
        service.ask(client, client.datasets, "Q")
    assert chat.deleted == [["session-1"]] * 4


@pytest.mark.parametrize("response,expected", [
    (FakeResponse({"code": 0, "data": 1}), {"code": 0, "data": 1}),
    (FakeResponse(None, text='data:{"code": 500, "message": "m"}'), {"code": 500, "message": "m"}),
])
def test_payload_accepts_json_and_sse_prefixed_bodies(response, expected):
    assert service._payload(response) == expected


def test_payload_rejects_non_json():
    with pytest.raises(service.RAGFlowError, match="unexpected response \\(HTTP 502\\)"):
        service._payload(FakeResponse(None, status_code=502, text="<html>Bad Gateway</html>"))
    with pytest.raises(service.RAGFlowError):
        service._payload(FakeResponse(None, text="data: not json"))


# ----------------------------------------------------------------- documents --
@pytest.mark.parametrize("doc,state", [
    ({"run": "DONE"}, "DONE"), ({"run": "FAIL", "progress": 0.3}, "FAIL"), ({"run": "CANCEL"}, "CANCEL"),
    ({"run": None, "ingestion_status": "COMPLETED", "progress": 1}, "DONE"),
    ({"ingestion_status": "FAILED"}, "FAIL"), ({"ingestion_status": "CANCELLED"}, "CANCEL"),
    ({"ingestion_status": "RUNNING", "progress": 1.0}, "DONE"), ({"progress": -1}, "FAIL"),
    ({"run": "RUNNING", "progress": 0.5}, None), ({"run": "0", "progress": "0"}, None), ({}, None),
])
def test_document_state(doc, state):
    assert service.document_state(doc) == state


def test_wait_for_parsing_reports_progress_and_terminal_states(monkeypatch):
    dataset = DataSet(None, {"id": "ds-handbook", "name": "handbook"})
    rounds = iter([
        [{"id": "d1", "name": "a.pdf", "progress": 0.25}, {"id": "d2", "name": "b.pdf", "progress": 0.25}],
        [{"id": "d1", "name": "a.pdf", "progress": 0.25}, {"id": "d2", "name": "b.pdf", "progress": -1, "progress_msg": "x\nOCR failed"}],
        [{"id": "d1", "name": "a.pdf", "ingestion_status": "COMPLETED", "progress": 1, "chunk_count": 7}],
    ])
    client = FakeClient()
    monkeypatch.setattr(service, "document_records", lambda rag, ds, ids=None: next(rounds))
    monkeypatch.setattr(service.time, "sleep", lambda s: None)
    lines = []
    states = service.wait_for_parsing(client, dataset, ["d1", "d2"], report=lines.append, poll_s=0)
    assert states == {"d2": "FAIL", "d1": "DONE"}
    assert lines == ["  a.pdf: 25%", "  b.pdf: 25%", "  b.pdf: FAIL, 0 chunks - OCR failed", "  a.pdf: DONE, 7 chunks"]


def test_wait_for_parsing_times_out(monkeypatch):
    client = FakeClient(documents={"ds-handbook": [{"id": "d1", "name": "a.pdf", "progress": 0.1}]})
    clock = iter([0, 0, 100, 100])
    monkeypatch.setattr(service.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(service.time, "sleep", lambda s: None)
    with pytest.raises(service.RAGFlowError, match="Timed out after 60s"):
        service.wait_for_parsing(client, client.create_dataset("handbook"), ["d1"], report=lambda _: None, timeout_s=60)


def test_add_documents_creates_skips_uploads_and_waits(tmp_path, monkeypatch):
    uploaded, updated = [], []

    class Doc:
        def __init__(self, name): self.id, self.name = f"doc-{name}", name
        def update(self, message): updated.append((self.name, message))

    def upload_documents(self, document_list):
        uploaded.extend((d["display_name"], d["blob"]) for d in document_list)
        return [Doc(d["display_name"]) for d in document_list]

    parsed = []
    monkeypatch.setattr(DataSet, "upload_documents", upload_documents)
    monkeypatch.setattr(DataSet, "async_parse_documents", lambda self, ids: parsed.append(list(ids)))
    monkeypatch.setattr(service, "wait_for_parsing", lambda rag, ds, ids, **kw: {i: "DONE" for i in ids})
    (tmp_path / "old.pdf").write_bytes(b"old")
    (tmp_path / "new.pdf").write_bytes(b"new")
    client = FakeClient()
    lines = []
    dataset = service.add_documents(client, "benefits", [tmp_path / "old.pdf", tmp_path / "new.pdf"],
                                    chunk_method="manual", report=lines.append)
    assert dataset.name == "benefits" and client.created_datasets == [dataset] and dataset.chunk_method == "manual"
    client.documents[dataset.id].append({"id": "doc-old.pdf", "name": "old.pdf"})
    lines.clear()
    service.add_documents(client, "benefits", [tmp_path / "old.pdf", tmp_path / "new.pdf"], chunk_method="manual",
                          report=lines.append)
    assert lines[0] == "Skipping old.pdf: already in 'benefits' (delete it in the web UI to re-add)"
    assert uploaded[-1] == ("new.pdf", b"new") and updated[-1] == ("new.pdf", {"chunk_method": "manual"})
    assert parsed[-1] == ["doc-new.pdf"]
    assert service.add_documents(client, "benefits", [tmp_path / "old.pdf"], report=lines.append) is dataset
    # chunk_method=None: the dataset keeps the server default and documents are not patched
    fresh = FakeClient()
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "new.pdf").write_bytes(b"dup")
    uploaded.clear(); updated.clear(); parsed.clear(); lines.clear()
    created = service.add_documents(fresh, "plain", [tmp_path / "new.pdf", tmp_path / "other" / "new.pdf"],
                                    report=lines.append)
    assert created.chunk_method == "naive" and fresh.created_datasets == [created]
    assert uploaded == [("new.pdf", b"new")] and updated == [] and parsed == [["doc-new.pdf"]]
    assert lines[-2] == "Skipping new.pdf: already in 'plain' (delete it in the web UI to re-add)"


# ----------------------------------------------------------------------- cli --
@pytest.fixture
def cli_client(monkeypatch):
    client = FakeClient(datasets=[HANDBOOK, WIKI], chats=[FakeChat("test", ["ds-handbook"])],
                        chunks=[{"id": "c1", "document_name": "a.pdf", "content": "Chunk text", "similarity": "0.42"}],
                        completion=completion("Answer [ID:0]", [{"id": "c1", "document_name": "a.pdf", "content": "<b>Chunk</b> text"}]))
    monkeypatch.setattr(service, "connect", lambda settings=None: client)
    monkeypatch.setenv("RAGFLOW_DATASET", "handbook")
    return client


def test_cli_lists_retrieves_and_asks(cli_client, capsys):
    cli.main(["--list"])
    assert capsys.readouterr().out.splitlines() == [
        "handbook: 4 documents, 103 chunks, embedding emb; assistants: test",
        "rag-mini-wiki: 1 documents, 469 chunks, embedding emb; assistants: (none)"]
    cli.main(["--retrieve", "--top", "5", "dress code"])
    assert capsys.readouterr().out == "--- [1] a.pdf  (similarity 0.42)\nChunk text\n\n"
    assert cli_client.retrievals == [(["ds-handbook"], "dress code", 5)]
    cli.main(["--dataset", "handbook,rag-mini-wiki", "Why?"])
    assert capsys.readouterr().out == 'Answer [ID:0]\n\nSources:\n  [ID:0] a.pdf — "Chunk text"\n'
    assert cli_client.created_chats[0].name == "handbook+rag-mini-wiki-assistant"
    posts = len(cli_client.posts)
    cli.main(["--list", "Why?"])  # the catalogue, then the answer
    out = capsys.readouterr().out
    assert out.startswith("handbook: 4 documents") and out.endswith('[ID:0] a.pdf — "Chunk text"\n')
    assert len(cli_client.posts) == posts + 1


def test_cli_argument_errors(cli_client, monkeypatch):
    with pytest.raises(SystemExit):
        cli.main([])
    monkeypatch.setenv("RAGFLOW_DATASET", "")
    with pytest.raises(SystemExit):
        cli.main(["question without dataset"])
    cli.main(["--list"])  # --list needs no dataset
    with pytest.raises(SystemExit):
        cli.main(["--dataset", "a,b", "--add", __file__])
    with pytest.raises(SystemExit):
        cli.main(["--dataset", "a", "--add", str(Path(__file__).parent / "missing.pdf")])


def test_cli_reports_unreachable_server_and_service_errors(cli_client):
    cli_client.list_errors["datasets"] = requests.ConnectionError("refused")
    with pytest.raises(SystemExit, match="is the SSH tunnel to the RAGFlow host running"):
        cli.main(["Why?"])
    cli_client.list_errors["datasets"] = requests.ConnectTimeout("connect timed out")
    with pytest.raises(SystemExit, match="is the SSH tunnel to the RAGFlow host running"):
        cli.main(["Why?"])
    del cli_client.list_errors["datasets"]
    cli_client.completion = requests.ReadTimeout("slow")
    with pytest.raises(SystemExit, match="did not respond within 120 seconds"):
        cli.main(["Why?"])
    with pytest.raises(SystemExit, match="Knowledge base not found: nope"):
        cli.main(["--dataset", "nope", "Why?"])


def test_cli_add_uploads_then_optionally_asks(cli_client, monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(service, "add_documents", lambda rag, name, paths, method: calls.append((name, [p.name for p in paths], method)) or rag.datasets[0])
    f = tmp_path / "a.pdf"
    f.write_bytes(b"x")
    cli.main(["--dataset", "handbook", "--add", str(f), "--chunk-method", "manual"])
    assert calls == [("handbook", ["a.pdf"], "manual")] and cli_client.posts == []
    cli.main(["--dataset", "handbook", "--add", str(f), "Why?"])
    assert len(calls) == 2 and cli_client.posts[0][0] == "/chat/completions"
