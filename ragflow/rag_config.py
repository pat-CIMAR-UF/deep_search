"""RAGFlow connection settings, read from the environment / project ``.env``.

Variables (same names as the RAGFlow_Example client):

- ``RAGFLOW_API_KEY``: API key from the RAGFlow web UI (required to connect).
- ``RAGFLOW_BASE_URL``: where the API is reachable from this machine, default
  ``http://localhost:8080`` (the local end of the SSH tunnel to the RAGFlow host).
  The former ``RAGFLOW_API_URL`` is still honoured as a fallback.
- ``RAGFLOW_DATASET``: knowledge base(s) used when a caller names none; several are
  separated by commas, e.g. ``handbook,rag-mini-wiki``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DEFAULT_BASE_URL = "http://localhost:8080"


def dataset_names(value: str | None) -> list[str]:
    """Parse a comma-separated list of knowledge-base names (``RAGFLOW_DATASET`` or a tool argument)."""
    return [name.strip() for name in (value or "").split(",") if name.strip()]


@dataclass(frozen=True)
class RAGFlowSettings:
    api_key: str | None
    base_url: str
    default_datasets: list[str] = field(default_factory=list)


def load_ragflow_settings() -> RAGFlowSettings:
    """Current settings; ``RAGFLOW_BASE_URL`` wins over the legacy ``RAGFLOW_API_URL``."""
    base_url = os.getenv("RAGFLOW_BASE_URL") or os.getenv("RAGFLOW_API_URL") or DEFAULT_BASE_URL
    return RAGFlowSettings(
        api_key=os.getenv("RAGFLOW_API_KEY") or None,
        base_url=base_url.strip().rstrip("/"),
        default_datasets=dataset_names(os.getenv("RAGFLOW_DATASET")),
    )
