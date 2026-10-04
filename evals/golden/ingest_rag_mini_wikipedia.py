"""Ingest rag-datasets/rag-mini-wikipedia (3,200 passages, CC-BY 3.0) into a RAGFlow knowledge base.

    uv run --with pyarrow python evals/golden/ingest_rag_mini_wikipedia.py [--dataset "RAG Mini Wikipedia"]
                                                                        [--embedding-model <id>]

Passages are batched 100 per text file; each passage is one line prefixed with a `[[passage N]]`
marker so retrieved chunks stay traceable to gold passage ids. RAPTOR and GraphRAG are disabled
for this dataset (they would send every chunk through an LLM). Idempotent: an existing dataset,
already-uploaded files and an existing chat assistant are reused. The parquet files are cached in
evals/golden/data/ (downloaded from Hugging Face on first run).

The server is the one configured for the app (ragflow/rag_config.py). A new dataset takes the
embedding model of the datasets already on that server when they agree (bases searched together
must share one); pass --embedding-model to override. Document status uses the raw records through
ragflow.service, because RAGFlow v1.0 reports ingestion_status/progress instead of run.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ragflow import service  # noqa: E402

DATA_DIR = HERE / "data"
HF_BASE = "https://huggingface.co/datasets/rag-datasets/rag-mini-wikipedia/resolve/main/data"
FILES = {"passages.parquet": f"{HF_BASE}/passages.parquet/part.0.parquet",
         "test.parquet": f"{HF_BASE}/test.parquet/part.0.parquet"}
BATCH = 100
FALLBACK_EMBEDDING_MODEL = "text-embedding-3-small@OpenAI"  # used only when the server has no dataset to copy from
PARSER_CONFIG = {"chunk_token_num": 128, "delimiter": "\n",
                 "raptor": {"use_raptor": False}, "graphrag": {"use_graphrag": False}}
CHAT_SYSTEM = ("You are an intelligent assistant answering from the RAG Mini Wikipedia knowledge base. "
               "Answer concisely from the retrieved passages and cite them. Passages start with a "
               "[[passage N]] marker; keep those markers in your answer when quoting. When the knowledge base "
               "content is irrelevant to the question, your answer must include the sentence "
               "\"The answer you are looking for is not found in the dataset!\"\n"
               "Here is the knowledge base:\n{knowledge}\nThe above is the knowledge base.")


def ensure_data() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    for name, url in FILES.items():
        target = DATA_DIR / name
        if not target.exists():
            print(f"downloading {name}")
            target.write_bytes(requests.get(url, timeout=120).content)


def load_passages():
    import pandas as pd
    df = pd.read_parquet(DATA_DIR / "passages.parquet")
    return list(zip(df.index.astype(int).tolist(), df["passage"].tolist()))


def batch_files(passages) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for start in range(0, len(passages), BATCH):
        chunk = passages[start:start + BATCH]
        name = f"rag_mini_wikipedia_{chunk[0][0]:04d}-{chunk[-1][0]:04d}.txt"
        body = "\n\n".join(f"[[passage {pid}]] {' '.join(text.split())}" for pid, text in chunk) + "\n"
        files[name] = body.encode("utf-8")
    return files


def server_embedding_model(client) -> str | None:
    """The embedding model shared by the datasets already on the server, or None when they differ or none exist."""
    models = {kb.embedding_model for kb in service.describe_knowledge_bases(client) if kb.embedding_model}
    return models.pop() if len(models) == 1 else None


def get_or_create_dataset(client, name: str, embedding_model: str | None):
    from ragflow_sdk.modules.dataset import DataSet
    # list_datasets(name=...) raises for a name that does not exist; list and match locally instead.
    existing = service.datasets_by_name(client).get(name)
    if existing is not None:
        print(f"dataset '{name}' exists ({existing.id}, embedding {existing.embedding_model})")
        return existing
    model = embedding_model or server_embedding_model(client) or FALLBACK_EMBEDDING_MODEL
    ds = client.create_dataset(name=name, description="rag-datasets/rag-mini-wikipedia passages (CC-BY 3.0) for evals",
                               embedding_model=model, chunk_method="naive",
                               parser_config=DataSet.ParserConfig(client, PARSER_CONFIG))
    print(f"created dataset '{name}' ({ds.id}) with embedding model {model}")
    return ds


def upload_missing(client, ds, files: dict[str, bytes]) -> list:
    have = {doc.get("name") for doc in service.document_records(client, ds)}
    todo = [{"display_name": n, "name": n, "blob": b} for n, b in files.items() if n not in have]
    uploaded = []
    for i in range(0, len(todo), 8):
        uploaded.extend(ds.upload_documents(todo[i:i + 8]))
    print(f"uploaded {len(uploaded)} new files ({len(have)} already present)")
    return uploaded


def _needs_parsing(doc: dict) -> bool:
    """Unparsed, failed or cancelled documents (and finished ones without chunks); a running document is left alone."""
    state = service.document_state(doc)
    if state == "DONE":
        return (doc.get("chunk_count") or 0) == 0
    if state in ("FAIL", "CANCEL"):
        return True
    return float(doc.get("progress") or 0) <= 0


def parse_and_wait(client, ds, timeout_s: int = 3600) -> None:
    pending = [doc for doc in service.document_records(client, ds) if _needs_parsing(doc)]
    if pending:
        ids = [doc["id"] for doc in pending]
        for i in range(0, len(ids), 16):
            ds.async_parse_documents(ids[i:i + 16])
        print(f"parsing {len(ids)} documents")
    start = time.time()
    while True:
        docs = service.document_records(client, ds)
        states = {doc["id"]: service.document_state(doc) for doc in docs}
        done = [doc for doc in docs if states[doc["id"]] == "DONE" and (doc.get("chunk_count") or 0) > 0]
        failed = [doc for doc in docs if states[doc["id"]] in ("FAIL", "CANCEL")]
        print(f"  {len(done)}/{len(docs)} done, {len(failed)} failed, "
              f"chunks={sum(doc.get('chunk_count') or 0 for doc in docs)}", flush=True)
        if len(done) == len(docs):
            return
        if failed:
            raise SystemExit("failed: " + ", ".join(f"{doc.get('name')}: {(doc.get('progress_msg') or '')[-200:]}"
                                                    for doc in failed))
        if time.time() - start > timeout_s:
            raise SystemExit("timed out waiting for parsing")
        time.sleep(15)


def get_or_create_chat(client, ds, name: str):
    # Reuse by name, or by the shared exact-dataset-set rule the app and the RAGFlow_Example CLI follow.
    chats = service.list_chats(client)
    existing = [c for c in chats if c.name == name] or [c for c in chats if set(c.dataset_ids or []) == {ds.id}]
    if existing:
        print(f"chat '{existing[0].name}' exists for dataset '{ds.name}'")
        return existing[0]
    llm_id = chats[0].llm_id if chats else None
    chat = client.create_chat(name=name, dataset_ids=[ds.id], llm_id=llm_id,
                              prompt_config={"system": CHAT_SYSTEM, "quote": True, "refine_multiturn": False,
                                             "empty_response": "Sorry! No relevant content was found in the knowledge base!",
                                             "parameters": [{"key": "knowledge", "optional": False}]})
    print(f"created chat '{name}' with llm {llm_id}")
    return chat


def verify_retrieval(client, ds) -> None:
    for q in ["When did Lincoln begin his political career?", "What is the capital of Uruguay?"]:
        chunks = service.retrieve(client, [ds], q, top=3)
        print(f"retrieve: {q}")
        for ch in chunks:
            similarity = service.chunk_similarity(ch)  # the server sends it as a string
            shown = f"{similarity:.3f}" if similarity is not None else "    ?"
            print(f"   {shown} {ch.content[:110]!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", default="RAG Mini Wikipedia")
    parser.add_argument("--chat", default="RAG Mini Wikipedia Assistant")
    parser.add_argument("--skip-chat", action="store_true")
    parser.add_argument("--embedding-model", default=None,
                        help="embedding model for a new dataset (default: the one the server's datasets share)")
    args = parser.parse_args()

    ensure_data()
    passages = load_passages()
    files = batch_files(passages)
    print(f"{len(passages)} passages -> {len(files)} files")
    client = service.connect()
    ds = get_or_create_dataset(client, args.dataset, args.embedding_model)
    upload_missing(client, ds, files)
    parse_and_wait(client, ds)
    if not args.skip_chat:
        get_or_create_chat(client, ds, args.chat)
    verify_retrieval(client, ds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
