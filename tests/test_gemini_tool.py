"""Tests for tools/gemini_tool.py with a fake Gemini client."""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import tools.gemini_tool as gemini_tool
from tools.gemini_tool import internet_search


def _chunk(title, uri):
    return SimpleNamespace(web=SimpleNamespace(title=title, uri=uri))


def _response(text="answer", queries=("q1", "q2"), chunks=(), with_metadata=True, with_candidates=True):
    metadata = SimpleNamespace(web_search_queries=list(queries), grounding_chunks=list(chunks))
    cand = SimpleNamespace(grounding_metadata=metadata if with_metadata else None)
    return SimpleNamespace(text=text, candidates=[cand] if with_candidates else [])


@pytest.fixture
def fake_client(monkeypatch):
    client = MagicMock(name="genai.Client")
    monkeypatch.setattr(gemini_tool, "_get_client", lambda: client)
    return client


@pytest.fixture
def reset_client(monkeypatch):
    monkeypatch.setattr(gemini_tool, "_client", None)


# ------------------------------------------------------------- _get_client --
def test_get_client_requires_api_key(monkeypatch, reset_client):
    monkeypatch.delenv("GEMINI_API_KEY")
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        gemini_tool._get_client()


def test_get_client_is_cached(monkeypatch, reset_client, test_env):
    ctor = MagicMock(return_value=object())
    monkeypatch.setattr(gemini_tool.genai, "Client", ctor)
    a = gemini_tool._get_client()
    b = gemini_tool._get_client()
    assert a is b
    ctor.assert_called_once_with(api_key=test_env["GEMINI_API_KEY"])


def test_first_concurrent_searches_share_one_client(monkeypatch, reset_client, test_env):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    import time

    start = Barrier(8)
    def create_client(**kwargs):
        # Keep initialization in progress while the other workers request a client.
        time.sleep(0.05)
        return object()
    constructor = MagicMock(side_effect=create_client)
    monkeypatch.setattr(gemini_tool.genai, "Client", constructor)
    def get_client(_):
        start.wait(timeout=5)
        return gemini_tool._get_client()
    with ThreadPoolExecutor(max_workers=8) as pool:
        clients = list(pool.map(get_client, range(8)))
    assert all(client is clients[0] for client in clients)
    constructor.assert_called_once_with(api_key=test_env["GEMINI_API_KEY"])


def test_default_model_from_env(test_env):
    assert gemini_tool.DEFAULT_MODEL == test_env["GEMINI_MODEL"]


# --------------------------------------------------------- internet_search --
def test_tool_metadata():
    assert internet_search.name == "internet_search"
    assert set(internet_search.args) == {"query", "max_results"}
    assert internet_search.args["max_results"]["default"] == 5
    assert internet_search.description.strip()


def test_internet_search_happy_path(fake_client, monitor_calls):
    fake_client.models.generate_content.return_value = _response(
        text="Python 3.14 is out.",
        queries=["latest python"],
        chunks=[_chunk("python.org", "https://python.org"), _chunk(None, None)],
    )
    out = internet_search.invoke({"query": "latest python", "max_results": 5})

    assert out == {
        "query": "latest python",
        "answer": "Python 3.14 is out.",
        "search_queries": ["latest python"],
        "sources": [
            {"title": "python.org", "url": "https://python.org"},
            {"title": "", "url": ""},
        ],
    }
    assert monitor_calls == [("Internet Search Tool (Gemini)", {"query": "latest python", "max_results": 5})]

    kwargs = fake_client.models.generate_content.call_args.kwargs
    assert kwargs["model"] == gemini_tool.DEFAULT_MODEL
    assert kwargs["contents"] == "latest python"
    cfg = kwargs["config"]
    assert isinstance(cfg, gemini_tool.types.GenerateContentConfig)
    assert len(cfg.tools) == 1 and cfg.tools[0].google_search is not None


def test_internet_search_truncates_sources_to_max_results(fake_client):
    fake_client.models.generate_content.return_value = _response(
        chunks=[_chunk(f"t{i}", f"u{i}") for i in range(10)]
    )
    out = internet_search.invoke({"query": "q", "max_results": 3})
    assert [s["title"] for s in out["sources"]] == ["t0", "t1", "t2"]


def test_internet_search_skips_chunks_without_web(fake_client):
    fake_client.models.generate_content.return_value = _response(
        chunks=[SimpleNamespace(web=None), _chunk("t", "u")]
    )
    out = internet_search.invoke({"query": "q"})
    assert out["sources"] == [{"title": "t", "url": "u"}]


def test_internet_search_without_grounding_metadata(fake_client):
    fake_client.models.generate_content.return_value = _response(with_metadata=False)
    out = internet_search.invoke({"query": "q"})
    assert out["search_queries"] == [] and out["sources"] == []
    assert out["answer"] == "answer"


def test_internet_search_without_candidates_or_text(fake_client):
    fake_client.models.generate_content.return_value = _response(text=None, with_candidates=False)
    out = internet_search.invoke({"query": "q"})
    assert out == {"query": "q", "answer": "", "search_queries": [], "sources": []}


def test_internet_search_default_max_results(fake_client, monitor_calls):
    fake_client.models.generate_content.return_value = _response()
    internet_search.invoke({"query": "q"})
    assert monitor_calls[0][1]["max_results"] == 5


def test_internet_search_propagates_client_errors(fake_client):
    fake_client.models.generate_content.side_effect = RuntimeError("quota")
    with pytest.raises(RuntimeError, match="quota"):
        internet_search.invoke({"query": "q"})
