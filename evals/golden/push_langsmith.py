"""Push evals/golden/v1.jsonl to a LangSmith dataset so Day 3+ experiments are versioned.

    LANGSMITH_API_KEY=... uv run python evals/golden/push_langsmith.py [--name deep-search-golden-v1]

Idempotent: existing examples are matched on metadata.id and updated; new ones are created.
Inputs = {question, mode}; outputs = the gold fields; metadata = id, specialist, route, difficulty, tags.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

HERE = Path(__file__).resolve().parent
V1 = HERE / "v1.jsonl"


def rows() -> list[dict]:
    return [json.loads(line) for line in V1.read_text(encoding="utf-8").splitlines() if line.strip()]


def split(row: dict) -> tuple[dict, dict, dict]:
    inputs = {"question": row["question"], "mode": row["mode"]}
    outputs = {k: row[k] for k in ("expected_answer", "expected_sources", "expected_route", "grader") if k in row}
    for k in ("expected_values", "governance", "gold_passage_ids"):
        if k in row:
            outputs[k] = row[k]
    metadata = {"id": row["id"], "specialist": row["specialist"], "route": "+".join(row["expected_route"]),
                "difficulty": row["difficulty"], "tags": row["tags"]}
    return inputs, outputs, metadata


def main() -> int:
    load_dotenv(find_dotenv())
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", default="deep-search-golden-v1")
    args = parser.parse_args()
    if not os.getenv("LANGSMITH_API_KEY"):
        print("LANGSMITH_API_KEY is not set", file=sys.stderr)
        return 2
    from langsmith import Client

    client = Client()
    data = rows()
    if client.has_dataset(dataset_name=args.name):
        dataset = client.read_dataset(dataset_name=args.name)
    else:
        dataset = client.create_dataset(dataset_name=args.name,
                                        description="Deep Search golden set v1 (evals/golden/v1.jsonl)")
    existing = {ex.metadata.get("id"): ex for ex in client.list_examples(dataset_id=dataset.id) if ex.metadata}
    created = updated = 0
    for row in data:
        inputs, outputs, metadata = split(row)
        if row["id"] in existing:
            client.update_example(example_id=existing[row["id"]].id, inputs=inputs, outputs=outputs, metadata=metadata)
            updated += 1
        else:
            client.create_example(inputs=inputs, outputs=outputs, metadata=metadata, dataset_id=dataset.id)
            created += 1
    print(f"dataset {args.name} ({dataset.id}): {created} created, {updated} updated, {len(data)} rows total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
