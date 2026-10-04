"""Command-line client for the RAGFlow knowledge bases (same flags as the RAGFlow_Example ``rag`` tool).

    uv run python -m ragflow.cli "your question"               # answer with cited sources
    uv run python -m ragflow.cli --retrieve --top 5 "query"    # matching chunks only, no LLM
    uv run python -m ragflow.cli --dataset a,b "question"      # search several knowledge bases
    uv run python -m ragflow.cli --dataset kb --add file.pdf   # upload + parse (created if missing)
    uv run python -m ragflow.cli --list                        # knowledge bases and their assistants

Configuration comes from the environment or the project's .env (see .env.example):
RAGFLOW_API_KEY (required), RAGFLOW_BASE_URL, RAGFLOW_DATASET.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):  # run as a script: make the project importable
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests

from ragflow import service
from ragflow.rag_config import dataset_names, load_ragflow_settings


def print_knowledge_bases(rag) -> None:
    bases = service.describe_knowledge_bases(rag)
    if not bases:
        print("No knowledge bases.")
    for kb in bases:
        assistants = ", ".join(kb.assistants) or "(none)"
        print(f"{kb.name}: {kb.document_count} documents, {kb.chunk_count} chunks, "
              f"embedding {kb.embedding_model or '?'}; assistants: {assistants}")


def print_chunks(rag, datasets, question: str, top: int) -> None:
    chunks = service.retrieve(rag, datasets, question, top=top)
    if not chunks:
        print("No matching chunks.")
    for i, chunk in enumerate(chunks, 1):
        similarity = service.chunk_similarity(chunk)
        shown = f"{similarity:.2f}" if similarity is not None else "?"
        print(f"--- [{i}] {chunk.document_name}  (similarity {shown})")
        print((chunk.content or "").strip(), end="\n\n")


def print_answer(rag, datasets, question: str) -> None:
    answer = service.ask(rag, datasets, question)
    print(answer.content)
    cited = answer.cited
    if cited:
        print("\nSources:")
        for ref in cited:
            print(f"  [ID:{ref.index}] {ref.document or '?'} — \"{ref.snippet}\"")
    elif answer.sources:
        print("\nSources:")
        for name in answer.sources:
            print(f"  - {name}")


def main(argv: list[str] | None = None) -> None:
    settings = load_ragflow_settings()
    parser = argparse.ArgumentParser(description="Ask questions against RAGFlow knowledge bases, or upload documents")
    parser.add_argument("question", nargs="?", help="question to ask (optional with --add or --list)")
    parser.add_argument("--dataset", type=dataset_names, default=settings.default_datasets, metavar="NAME[,NAME]",
                        help="knowledge base name, or several separated by commas (default: $RAGFLOW_DATASET)")
    parser.add_argument("--retrieve", action="store_true", help="show matching chunks only, skip the LLM")
    parser.add_argument("--top", type=int, default=3, help="number of chunks for --retrieve")
    parser.add_argument("--add", type=Path, action="append", metavar="FILE", help="upload and parse a file (repeatable)")
    parser.add_argument("--chunk-method", help="parser for --add: naive, manual, book, laws, table, paper, qa, ...")
    parser.add_argument("--list", action="store_true", help="list knowledge bases and their assistants")
    args = parser.parse_args(argv)
    if not args.question and not args.add and not args.list:
        parser.error("give a question, --add FILE or --list")
    if (args.question or args.add) and not args.dataset:
        parser.error("give --dataset or set RAGFLOW_DATASET")
    if args.add and len(args.dataset) > 1:
        parser.error("--add uploads into one knowledge base: give a single --dataset")
    for path in args.add or []:
        if not path.is_file():
            parser.error(f"no such file: {path}")

    try:
        rag = service.connect(settings)
    except service.RAGFlowError as exc:
        raise SystemExit(str(exc)) from None
    try:
        if args.list:
            print_knowledge_bases(rag)
            if not args.question and not args.add:
                return
        if args.add:
            datasets = [service.add_documents(rag, args.dataset[0], args.add, args.chunk_method)]
            if not args.question:
                return
        else:
            datasets = service.get_datasets(rag, args.dataset)
        if args.retrieve:
            print_chunks(rag, datasets, args.question, args.top)
        else:
            print_answer(rag, datasets, args.question)
    except requests.ConnectionError:  # includes ConnectTimeout, so it must come before Timeout
        raise SystemExit(service.unreachable_message(rag)) from None
    except requests.Timeout:
        raise SystemExit(f"RAGFlow did not respond within {service.READ_TIMEOUT_S} seconds") from None
    except service.RAGFlowError as exc:
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()
