"""LangChain tools for the RAGFlow knowledge-base specialist.

Flow for the model: ``list_knowledge_bases`` (exact names) -> ``ask_knowledge_base`` (answer with
cited sources) or ``retrieve_chunks`` (matching passages, no LLM). ``ragflow/service.py`` does the
work; this module adds progress reporting, evaluation events and model-facing messages.
"""
from pathlib import Path
import sys
_PROJECT_ROOT = str(Path(__file__).parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import requests
from langchain_core.tools import tool

from api.context import get_run_metrics
from api.monitor import monitor
from ragflow import service
from ragflow.rag_config import load_ragflow_settings

MAX_TOP = 20

# Client connected on first use (tests replace it).
ragflow_client = None


def _get_client() -> service.RAGFlowClient:
    """Connect on first use so imports do not require credentials."""
    global ragflow_client
    if ragflow_client is None:
        ragflow_client = service.connect()
    return ragflow_client


def _failure(prefix: str, exc: Exception, client=None) -> str:
    """Model-facing failure text; connection problems point at the SSH tunnel."""
    if isinstance(exc, requests.ConnectionError) and client is not None:
        return f"{prefix}: {service.unreachable_message(client)}"
    if isinstance(exc, requests.Timeout):
        return f"{prefix}: RAGFlow did not respond within {service.READ_TIMEOUT_S} seconds."
    return f"{prefix}: {exc}"


def _record_event(datasets, question: str, chunks: list[dict], assistant: str, answer: str) -> None:
    """Keep the retrieved chunks for evaluation graders (only when a RunMetrics is installed)."""
    metrics = get_run_metrics()
    if metrics is not None:
        metrics.add_event("ragflow_retrieval", assistant=assistant, knowledge_bases=[d.name for d in datasets],
                          question=question, chunks=chunks, answer=answer)


@tool
def list_knowledge_bases() -> str:
    """List the RAGFlow knowledge bases that can be searched.

    Call this first: it returns the exact knowledge-base names that ``retrieve_chunks`` and
    ``ask_knowledge_base`` take, with each base's description, document and chunk counts,
    embedding model, and the chat assistants already linked to it.

    Returns:
        One line per knowledge base, ``No knowledge bases available``, or
        ``Failed to list knowledge bases: <reason>``.
    """
    monitor.report_tool(tool_name="RAGFlow knowledge-base list tool: list_knowledge_bases")
    client = None
    try:
        client = _get_client()
        bases = service.describe_knowledge_bases(client)
    except Exception as exc:  # noqa: BLE001 - every failure becomes a model-readable message
        return _failure("Failed to list knowledge bases", exc, client)
    if not bases:
        return "No knowledge bases available"
    lines = [f"knowledge base: {kb.name}; description: {kb.description}; documents: {kb.document_count}; "
             f"chunks: {kb.chunk_count}; embedding model: {kb.embedding_model}; "
             f"assistants: {', '.join(kb.assistants) or 'none'}" for kb in bases]
    default = load_ragflow_settings().default_datasets
    if default:
        lines.append(f"default when no knowledge base is given (RAGFLOW_DATASET): {', '.join(default)}")
    return "\n".join(lines)


@tool
def retrieve_chunks(question: str, knowledge_bases: str | list[str] = "", top: int = 3) -> str:
    """Return the passages that best match a question, without generating an answer.

    Use it to check what the documents actually contain, to quote exact wording, or when the
    question is a lookup rather than a synthesis.

    Args:
        question: the search query.
        knowledge_bases: exact names from ``list_knowledge_bases``, comma-separated (or a list) to
            search several together (they must share an embedding model). Omit or leave empty to
            use the ``RAGFLOW_DATASET`` default.
        top: number of chunks to return (1-20, default 3).

    Returns:
        Numbered chunks ``[n] <document> (similarity 0.xx)`` each followed by its text,
        ``No matching chunks.``, or ``Retrieval failed: <reason>``.
    """
    monitor.report_tool(tool_name="RAGFlow retrieval tool: retrieve_chunks",
                        args={"knowledge_bases": knowledge_bases, "question": question, "top": top})
    try:
        top = max(1, min(int(top), MAX_TOP))
    except (TypeError, ValueError):
        top = 3
    client = None
    try:
        client = _get_client()
        datasets = service.resolve_datasets(client, knowledge_bases)
        chunks = service.retrieve(client, datasets, question, top=top)
    except Exception as exc:  # noqa: BLE001
        return _failure("Retrieval failed", exc, client)
    records = [{"document": chunk.document_name or "", "content": chunk.content or "",
                "similarity": service.chunk_similarity(chunk), "chunk_id": chunk.id or ""} for chunk in chunks]
    _record_event(datasets, question, records, assistant="", answer="")
    if not records:
        return "No matching chunks."
    parts = []
    for index, record in enumerate(records, 1):
        similarity = record["similarity"]
        shown = f"{similarity:.2f}" if similarity is not None else "?"
        parts.append(f"[{index}] {record['document']} (similarity {shown})\n{record['content'].strip()}")
    return "\n\n".join(parts)


@tool
def ask_knowledge_base(question: str, knowledge_bases: str | list[str] = "") -> str:
    """Ask the chat assistant linked to the given knowledge bases and return its cited answer.

    The assistant linked to exactly these knowledge bases is reused; otherwise one named
    ``<name>-assistant`` (``<a>+<b>-assistant`` for several) is created with the server defaults.
    The question runs in a temporary session that is removed afterwards.

    Args:
        question: one focused question.
        knowledge_bases: exact names from ``list_knowledge_bases``, comma-separated (or a list) for
            several (they must share an embedding model). Omit or leave empty to use the
            ``RAGFLOW_DATASET`` default.

    Returns:
        The assistant's answer, whose ``[ID:n]`` markers point at the ``Sources`` list that
        follows (document name and a snippet of each cited passage), or
        ``Question failed: <reason>`` when the service, knowledge base or answer is unavailable.
    """
    monitor.report_tool(tool_name="RAGFlow ask tool: ask_knowledge_base",
                        args={"knowledge_bases": knowledge_bases, "question": question})
    client = None
    try:
        client = _get_client()
        datasets = service.resolve_datasets(client, knowledge_bases)
        answer = service.ask(client, datasets, question)
    except Exception as exc:  # noqa: BLE001
        return _failure("Question failed", exc, client)
    _record_event(datasets, question, [ref.as_dict() for ref in answer.unique_references()],
                  assistant=answer.assistant, answer=answer.content)
    result = answer.content
    cited = answer.cited
    if cited:
        result += "\n\nSources:\n" + "\n".join(f'[ID:{ref.index}] {ref.document or "?"} — "{ref.snippet}"' for ref in cited)
    elif answer.sources:
        result += "\n\nSources:\n" + "\n".join(f"- {name}" for name in answer.sources)
    return result
