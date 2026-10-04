"""In-memory stand-ins for the RAGFlow client used by the knowledge-base tool tests.

They model the slice of ``ragflow.service.RAGFlowClient`` the service layer touches: paged dataset
and chat listings, chat creation, retrieval, raw ``post``/``get`` calls (chat completions and
document records) and sessions on a chat.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

from ragflow_sdk.modules.chunk import Chunk
from ragflow_sdk.modules.dataset import DataSet


class FakeResponse:
    def __init__(self, payload=None, status_code: int = 200, text: str | None = None):
        self._payload, self.status_code = payload, status_code
        self.text = text if text is not None else (json.dumps(payload) if payload is not None else "")

    def json(self):
        if self._payload is None:
            raise ValueError("not JSON")
        return self._payload


class FakeChat:
    def __init__(self, name: str, dataset_ids, session_id: str = "session-1", fail_create: Exception | None = None,
                 fail_delete: Exception | None = None):
        self.id, self.name, self.dataset_ids = f"id-{name}", name, list(dataset_ids)
        self.session_id, self.fail_create, self.fail_delete = session_id, fail_create, fail_delete
        self.created: list[str] = []
        self.deleted: list[list[str]] = []

    def create_session(self, name: str = "New session"):
        if self.fail_create is not None:
            raise self.fail_create
        self.created.append(name)
        return SimpleNamespace(id=self.session_id)

    def delete_sessions(self, ids=None, delete_all: bool = False):
        if self.fail_delete is not None:
            raise self.fail_delete
        self.deleted.append(list(ids or []))


def completion(answer: str, chunks=None, code: int = 0, message: str = "") -> dict:
    """A ``POST /chat/completions`` body like RAGFlow v1.0.0-rc1 returns it."""
    data = {"answer": answer, "reference": {"chunks": list(chunks or []), "doc_aggs": [], "total": len(chunks or [])},
            "session_id": "session-1", "final": True}
    return {"code": code, "message": message, "data": data}


class FakeClient:
    api_url = "http://ragflow.test:8080/api/v1"

    def __init__(self, datasets=(), chats=(), chunks=(), completion=None, documents=None, page_size: int = 100):
        self.datasets = [d if isinstance(d, DataSet) else DataSet(self, dict(d)) for d in datasets]
        self.chats = list(chats)
        self.chunks = [c if isinstance(c, Chunk) else Chunk(self, dict(c)) for c in chunks]
        self.completion = completion
        # dataset id -> list of raw document records (``GET /datasets/{id}/documents``)
        self.documents: dict[str, list[dict]] = documents or {}
        self.page_size = page_size
        self.posts: list[tuple[str, dict | None]] = []
        self.gets: list[tuple[str, dict | None]] = []
        self.created_chats: list[FakeChat] = []
        self.created_datasets: list[DataSet] = []
        self.retrievals: list[tuple[list[str], str, int]] = []
        self.list_errors: dict[str, Exception] = {}

    # -- listings -------------------------------------------------------------------------
    def _page(self, items, page, page_size):
        start = (page - 1) * page_size
        return items[start:start + page_size]

    def list_datasets(self, page: int = 1, page_size: int = 30, **_):
        if "datasets" in self.list_errors:
            raise self.list_errors["datasets"]
        return self._page(self.datasets, page, page_size)

    def list_chats(self, page: int = 1, page_size: int = 30, **_):
        if "chats" in self.list_errors:
            raise self.list_errors["chats"]
        return self._page(self.chats, page, page_size)

    # -- creation -------------------------------------------------------------------------
    def create_chat(self, name: str, dataset_ids=None, **_):
        chat = FakeChat(name, dataset_ids or [])
        self.chats.append(chat)
        self.created_chats.append(chat)
        return chat

    def create_dataset(self, name: str, chunk_method: str = "naive", **_):
        dataset = DataSet(self, {"id": f"ds-{name}", "name": name, "chunk_method": chunk_method})
        self.datasets.append(dataset)
        self.created_datasets.append(dataset)
        self.documents.setdefault(dataset.id, [])
        return dataset

    # -- retrieval and raw HTTP ---------------------------------------------------------
    def retrieve(self, dataset_ids, question: str = "", page_size: int = 30, **_):
        self.retrievals.append((list(dataset_ids), question, page_size))
        return self.chunks

    def post(self, path: str, json=None, stream: bool = False, files=None):
        self.posts.append((path, json))
        if isinstance(self.completion, Exception):
            raise self.completion
        if isinstance(self.completion, FakeResponse):
            return self.completion
        return FakeResponse(self.completion)

    def get(self, path: str, params=None, json=None):
        self.gets.append((path, params))
        if path.startswith("/datasets/") and path.endswith("/documents"):
            dataset_id = path.split("/")[2]
            page = int((params or {}).get("page") or 1)
            docs = self._page(self.documents.get(dataset_id, []), page, int((params or {}).get("page_size") or 30))
            return FakeResponse({"code": 0, "data": {"docs": docs, "total": len(docs)}})
        return FakeResponse({"code": 100, "message": f"unexpected GET {path}"})
