"""RAGFlow service layer shared by the knowledge-base tools and the ``ragflow.cli`` command line.

It follows the RAGFlow_Example client conventions:

- knowledge bases (RAGFlow datasets) are addressed by name; ``RAGFLOW_DATASET`` holds the
  comma-separated default list and several bases can be searched together;
- the SDK's ``name=`` filters raise when nothing matches, so lookups list everything and match
  locally;
- a chat assistant is reused when it is linked to exactly the requested datasets, otherwise
  ``<a>+<b>-assistant`` is created with the server defaults (LLM, prompt and retrieval settings
  are configured in the RAGFlow web UI, not here);
- ``[ID:n]`` markers in an answer cite index ``n`` of the returned reference list;
- a connection failure is reported as "is the SSH tunnel running?".

Server compatibility (RAGFlow ``v1.0.0-rc1``, verified 2026-10-02):

- chat completions are ``POST /api/v1/chat/completions`` with ``chat_id``, ``session_id`` and
  ``messages``; the SDK's ``Session.ask`` still posts to ``/chats/{id}/completions`` (404), so
  :func:`ask` sends the request itself and reads ``data.answer`` / ``data.reference.chunks``;
- documents report ``ingestion_status`` and ``progress`` instead of ``run`` (the SDK drops the
  former), so :func:`document_state` also treats ``progress >= 1`` as finished;
- an assistant linked to several datasets can list every reference chunk twice, so
  :meth:`Answer.unique_references` deduplicates by chunk id.

Unlike the command-line client, :func:`ask` removes the temporary session it created, including
when the request fails, so agent and evaluation traffic does not accumulate sessions.
"""
from __future__ import annotations

import html
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

import requests
from ragflow_sdk import RAGFlow
from ragflow_sdk.modules.chat import Chat
from ragflow_sdk.modules.chunk import Chunk
from ragflow_sdk.modules.dataset import DataSet

from ragflow.rag_config import RAGFlowSettings, dataset_names, load_ragflow_settings

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT_S = 10
READ_TIMEOUT_S = 120
PAGE_SIZE = 100
SESSION_NAME_CHARS = 64
ERROR_ANSWER_PREFIX = "**ERROR**"
SNIPPET_CHARS = 100
CITATION = re.compile(r"\[ID:(\d+)\]")
HTML_TAG = re.compile(r"</?[A-Za-z][^<>]*>")  # real tags only; "CrCl < 30" and "> 3 months" are prose
# Terminal parsing states: ``run`` on servers before v1.0, ``ingestion_status`` from v1.0 on.
TERMINAL_RUN_STATES = {"DONE": "DONE", "FAIL": "FAIL", "CANCEL": "CANCEL"}
TERMINAL_INGESTION_STATES = {"COMPLETED": "DONE", "FAILED": "FAIL", "CANCELLED": "CANCEL"}


class RAGFlowError(Exception):
    """A RAGFlow request failed; the message is safe to show to the model or the user."""


class KnowledgeBaseNotFound(RAGFlowError):
    def __init__(self, missing: list[str], available: list[str]):
        self.missing, self.available = list(missing), list(available)
        super().__init__(f"Knowledge base not found: {', '.join(self.missing)}. "
                         f"Available: {', '.join(self.available) or '(none)'}")


class RAGFlowClient(RAGFlow):
    """ragflow-sdk client whose requests time out, so an offline service cannot occupy a worker forever."""

    def _request(self, method, path, **kwargs):
        return requests.request(method, self.api_url + path, headers=self.authorization_header,
                                timeout=(CONNECT_TIMEOUT_S, READ_TIMEOUT_S), **kwargs)

    def get(self, path, params=None, json=None):
        return self._request("GET", path, params=params, json=json)

    def post(self, path, json=None, stream=False, files=None):
        return self._request("POST", path, json=json, stream=stream, files=files)

    def delete(self, path, json):
        return self._request("DELETE", path, json=json)

    def put(self, path, json):
        return self._request("PUT", path, json=json)

    def patch(self, path, json):
        return self._request("PATCH", path, json=json)


def connect(settings: RAGFlowSettings | None = None) -> RAGFlowClient:
    """Client for the configured server; raises :class:`RAGFlowError` when the key is missing."""
    settings = settings or load_ragflow_settings()
    api_key = (settings.api_key or "").strip()
    if not api_key:
        raise RAGFlowError("RAGFLOW_API_KEY is not set: put it in .env (see .env.example).")
    if any(char in api_key for char in "\r\n\t "):
        # requests would otherwise echo the whole header value in its InvalidHeader error
        raise RAGFlowError("RAGFLOW_API_KEY contains whitespace or line breaks; fix it in .env.")
    return RAGFlowClient(api_key=api_key, base_url=settings.base_url)


def unreachable_message(client: RAGFlow) -> str:
    return (f"Cannot reach RAGFlow at {client.api_url}: is the SSH tunnel to the RAGFlow host "
            f"running? (see README)")


def _payload(response) -> dict:
    """JSON body of a response; tolerates the ``data:`` prefix the server uses for SSE errors."""
    try:
        payload = response.json()
    except ValueError:
        text = (response.text or "").strip()
        if text.startswith("data:"):
            try:
                payload = json.loads(text[len("data:"):].strip())
            except ValueError:
                payload = None
        else:
            payload = None
    if not isinstance(payload, dict):
        raise RAGFlowError(f"RAGFlow returned an unexpected response (HTTP {response.status_code}).")
    return payload


def _float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _all_pages(fetch: Callable[[int], list]) -> list:
    items, page = [], 1
    while True:
        batch = list(fetch(page))
        items.extend(batch)
        if len(batch) < PAGE_SIZE:
            return items
        page += 1


# --------------------------------------------------------------------------- knowledge bases --
def datasets_by_name(rag: RAGFlow) -> dict[str, DataSet]:
    """Every dataset keyed by name (``list_datasets(name=...)`` raises when nothing matches)."""
    return {d.name: d for d in _all_pages(lambda page: rag.list_datasets(page=page, page_size=PAGE_SIZE))}


def list_chats(rag: RAGFlow) -> list[Chat]:
    return _all_pages(lambda page: rag.list_chats(page=page, page_size=PAGE_SIZE))


def get_datasets(rag: RAGFlow, names: Iterable[str]) -> list[DataSet]:
    """Datasets for exactly these names, in order; raises :class:`KnowledgeBaseNotFound`."""
    names = list(names)
    datasets = datasets_by_name(rag)
    missing = [name for name in names if name not in datasets]
    if missing:
        raise KnowledgeBaseNotFound(missing, list(datasets))
    return [datasets[name] for name in names]


def resolve_datasets(rag: RAGFlow, names: str | Iterable[str] | None,
                     settings: RAGFlowSettings | None = None) -> list[DataSet]:
    """Datasets for ``names`` (comma-separated string or list); empty falls back to ``RAGFLOW_DATASET``."""
    if names is None or isinstance(names, str):
        wanted = dataset_names(names)
    else:
        wanted = [name.strip() for name in names if name and name.strip()]
    if not wanted:
        wanted = list((settings or load_ragflow_settings()).default_datasets)
    wanted = list(dict.fromkeys(wanted))  # "kb,kb" must not post repeated ids or create "kb+kb-assistant"
    if not wanted:
        available = ", ".join(datasets_by_name(rag)) or "(none)"
        raise RAGFlowError(f"No knowledge base given and RAGFLOW_DATASET is not set. Available: {available}")
    return get_datasets(rag, wanted)


@dataclass
class KnowledgeBase:
    name: str
    description: str
    document_count: int
    chunk_count: int
    embedding_model: str
    assistants: list[str] = field(default_factory=list)


def describe_knowledge_bases(rag: RAGFlow) -> list[KnowledgeBase]:
    """Datasets with their counts and the chat assistants linked to each one."""
    linked: dict[str, list[str]] = {}
    for chat in list_chats(rag):
        for dataset_id in getattr(chat, "dataset_ids", None) or []:
            linked.setdefault(dataset_id, []).append(chat.name)
    return [KnowledgeBase(name=d.name, description=(d.description or "").strip(),
                          document_count=int(d.document_count or 0), chunk_count=int(d.chunk_count or 0),
                          embedding_model=d.embedding_model or "", assistants=linked.get(d.id, []))
            for d in datasets_by_name(rag).values()]


# ------------------------------------------------------------------------------- assistants --
def assistant_name(datasets: list[DataSet]) -> str:
    return f"{'+'.join(d.name for d in datasets)}-assistant"


def get_chat(rag: RAGFlow, datasets: list[DataSet]) -> Chat:
    """Reuse the chat assistant linked to exactly these datasets, else create one with server defaults."""
    ids = [d.id for d in datasets]
    for chat in list_chats(rag):
        if set(getattr(chat, "dataset_ids", None) or []) == set(ids):
            return chat
    return rag.create_chat(assistant_name(datasets), dataset_ids=ids)


# -------------------------------------------------------------------------------- answers --
def snippet(text: str, limit: int = SNIPPET_CHARS) -> str:
    """One-line excerpt: HTML (table) tags and entities removed, whitespace collapsed, truncated with an ellipsis."""
    text = " ".join(html.unescape(HTML_TAG.sub(" ", text or "")).split())
    return text[:limit] + ("…" if len(text) > limit else "")


@dataclass
class Reference:
    index: int
    document: str
    content: str
    similarity: float | None = None
    chunk_id: str = ""
    dataset_id: str = ""

    @property
    def snippet(self) -> str:
        return snippet(self.content)

    def as_dict(self) -> dict:
        return {"document": self.document, "content": self.content, "similarity": self.similarity,
                "chunk_id": self.chunk_id}


@dataclass
class Answer:
    content: str
    references: list[Reference] = field(default_factory=list)
    assistant: str = ""
    session_name: str = ""

    @property
    def cited(self) -> list[Reference]:
        """References the answer cites with in-range ``[ID:n]`` markers, in index order."""
        indices = {int(n) for n in CITATION.findall(self.content)} & set(range(len(self.references)))
        return [self.references[i] for i in sorted(indices)]

    @property
    def sources(self) -> list[str]:
        """Distinct document names: the cited ones, or every reference when the answer has no markers."""
        names: list[str] = []
        for ref in self.cited or self.references:
            if ref.document and ref.document not in names:
                names.append(ref.document)
        return names

    def unique_references(self) -> list[Reference]:
        """References deduplicated by chunk id (multi-dataset assistants repeat every chunk)."""
        seen, unique = set(), []
        for ref in self.references:
            key = ref.chunk_id or (ref.document, ref.content)
            if key in seen or not ref.content.strip():
                continue
            seen.add(key)
            unique.append(ref)
        return unique


def parse_references(reference) -> list[Reference]:
    """Reference chunks of a completion: ``reference.chunks`` (list or id-keyed dict) or a bare list.

    Positions are kept, so ``[ID:n]`` in the answer indexes the result directly; a malformed entry
    becomes an empty placeholder.
    """
    chunks = reference.get("chunks") if isinstance(reference, dict) else reference
    if isinstance(chunks, dict):
        chunks = list(chunks.values())
    if not isinstance(chunks, list):
        return []
    references = []
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            references.append(Reference(index=index, document="", content=""))
            continue
        references.append(Reference(
            index=index,
            document=str(chunk.get("document_name") or chunk.get("document_keyword") or ""),
            content=chunk.get("content") if isinstance(chunk.get("content"), str) else "",
            similarity=_float(chunk.get("similarity")),
            chunk_id=str(chunk.get("id") or ""),
            dataset_id=str(chunk.get("dataset_id") or ""),
        ))
    return references


def complete(rag: RAGFlow, chat: Chat, session_id: str, question: str) -> dict:
    """One non-streaming turn on ``POST /chat/completions``; returns the response ``data`` object."""
    response = rag.post("/chat/completions", {
        "chat_id": chat.id, "session_id": session_id, "stream": False,
        "messages": [{"role": "user", "content": question}],
    })
    payload = _payload(response)
    if payload.get("code") != 0:
        raise RAGFlowError(payload.get("message") or f"RAGFlow completion failed (code {payload.get('code')}).")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RAGFlowError("RAGFlow completion returned no data.")
    return data


def ask(rag: RAGFlow, datasets: list[DataSet], question: str) -> Answer:
    """Ask the assistant linked to ``datasets``; the temporary session is removed afterwards."""
    chat = get_chat(rag, datasets)
    session_name = question[:SESSION_NAME_CHARS]
    session = chat.create_session(name=session_name)
    try:
        data = complete(rag, chat, session.id, question)
    finally:
        try:
            chat.delete_sessions(ids=[session.id])
        except Exception as exc:  # noqa: BLE001 - never mask the answer or the original failure
            logger.warning("Could not delete temporary RAGFlow session %s: %s", session.id, exc)
    answer = Answer(content=(data.get("answer") or "").strip(), references=parse_references(data.get("reference")),
                    assistant=chat.name, session_name=session_name)
    if not answer.content:
        raise RAGFlowError("RAGFlow returned an empty answer.")
    if answer.content.startswith(ERROR_ANSWER_PREFIX) or f"\n{ERROR_ANSWER_PREFIX}" in answer.content:
        # The server reports LLM-provider failures (bad key, quota, model unavailable) as a code-0
        # completion whose answer text starts with "**ERROR**" (or ends with it after a partial
        # answer); that is a failure, not an answer.
        detail = answer.content.split(ERROR_ANSWER_PREFIX, 1)[1].strip(": ")[:300] or "unknown error"
        raise RAGFlowError(f"RAGFlow assistant error: {detail}")
    return answer


# ------------------------------------------------------------------------------- retrieval --
def retrieve(rag: RAGFlow, datasets: list[DataSet], question: str, top: int = 3) -> list[Chunk]:
    """Best-matching chunks across ``datasets`` without calling the LLM."""
    return rag.retrieve(dataset_ids=[d.id for d in datasets], question=question, page_size=top)


def chunk_similarity(chunk: Chunk) -> float | None:
    """``similarity`` as a number (the server sends it as a string)."""
    return _float(getattr(chunk, "similarity", None))


# ------------------------------------------------------------------------------- documents --
def document_state(doc: dict) -> str | None:
    """``DONE`` / ``FAIL`` / ``CANCEL`` once parsing has finished, else ``None``.

    Works for servers that report ``run`` and for v1.0's ``ingestion_status`` + ``progress``.
    """
    run = str(doc.get("run") or "").upper()
    if run in TERMINAL_RUN_STATES:
        return TERMINAL_RUN_STATES[run]
    status = str(doc.get("ingestion_status") or "").upper()
    if status in TERMINAL_INGESTION_STATES:
        return TERMINAL_INGESTION_STATES[status]
    progress = _float(doc.get("progress"))
    if progress is not None:
        if progress >= 1:
            return "DONE"
        if progress < 0:
            return "FAIL"
    return None


def document_records(rag: RAGFlow, dataset: DataSet, ids: Iterable[str] | None = None) -> list[dict]:
    """Raw document records of a dataset (the SDK's ``Document`` drops ``ingestion_status``)."""
    def fetch(page: int) -> list[dict]:
        payload = _payload(rag.get(f"/datasets/{dataset.id}/documents", params={"page": page, "page_size": PAGE_SIZE}))
        if payload.get("code") != 0:
            raise RAGFlowError(payload.get("message") or "Could not list documents.")
        return (payload.get("data") or {}).get("docs") or []

    docs = _all_pages(fetch)
    if ids is None:
        return docs
    wanted = set(ids)
    return [doc for doc in docs if doc.get("id") in wanted]


def wait_for_parsing(rag: RAGFlow, dataset: DataSet, ids: list[str], report: Callable[[str], None] = print,
                     poll_s: float = 5.0, timeout_s: float | None = None) -> dict[str, str]:
    """Poll until every document reaches a terminal state; returns ``{document_id: state}``."""
    pending: dict[str, str | None] = {doc_id: None for doc_id in ids}
    states: dict[str, str] = {}
    started = time.monotonic()
    while pending:
        if timeout_s is not None and time.monotonic() - started > timeout_s:
            raise RAGFlowError(f"Timed out after {timeout_s:.0f}s waiting for parsing: {', '.join(pending)}")
        time.sleep(poll_s)
        for doc in document_records(rag, dataset, ids=list(pending)):
            doc_id = doc.get("id")
            if doc_id not in pending:
                continue
            state = document_state(doc)
            if state:
                log = (doc.get("progress_msg") or "").strip().splitlines()
                detail = f" - {log[-1]}" if log and state != "DONE" else ""
                report(f"  {doc.get('name')}: {state}, {doc.get('chunk_count') or 0} chunks{detail}")
                states[doc_id] = state
                del pending[doc_id]
            else:
                progress = f"{_float(doc.get('progress')) or 0:.0%}"
                if progress != pending[doc_id]:
                    report(f"  {doc.get('name')}: {progress}")
                    pending[doc_id] = progress
    return states


def add_documents(rag: RAGFlow, dataset_name: str, paths: Iterable[Path | str], chunk_method: str | None = None,
                  report: Callable[[str], None] = print, poll_s: float = 5.0,
                  timeout_s: float | None = None) -> DataSet:
    """Upload files into the knowledge base (created if missing) and wait until RAGFlow has parsed them.

    A file whose exact name is already in the dataset is skipped; delete it in the web UI to re-add.
    """
    dataset = datasets_by_name(rag).get(dataset_name)
    if dataset is None:
        report(f"Creating knowledge base {dataset_name!r}")
        dataset = rag.create_dataset(name=dataset_name, chunk_method=chunk_method or "naive")

    existing = {doc.get("name") for doc in document_records(rag, dataset)}
    new_docs = []
    for path in paths:
        path = Path(path)
        if path.name in existing:
            report(f"Skipping {path.name}: already in {dataset_name!r} (delete it in the web UI to re-add)")
            continue
        report(f"Uploading {path.name} ({path.stat().st_size / 1e6:.1f} MB)...")
        doc = dataset.upload_documents([{"display_name": path.name, "blob": path.read_bytes()}])[0]
        if chunk_method:
            doc.update({"chunk_method": chunk_method})
        new_docs.append(doc)
        existing.add(path.name)  # the same basename given twice is uploaded once
    if not new_docs:
        return dataset

    dataset.async_parse_documents([d.id for d in new_docs])
    report("Parsing on the server (Ctrl-C stops waiting; parsing continues remotely)...")
    wait_for_parsing(rag, dataset, [d.id for d in new_docs], report=report, poll_s=poll_s, timeout_s=timeout_s)
    return dataset
