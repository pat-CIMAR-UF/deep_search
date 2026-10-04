"""Ragas RAG metrics on the knowledge-base rows of a golden run.

Usage:
    uv run python evals/graders/ragas_eval.py --run v1_baseline            # -> evals/runs/v1_baseline/ragas.json
    uv run python evals/graders/ragas_eval.py --run v1_baseline --ids kb-01 kb-02

Metrics (all LLM-based, judged by the Azure deployment in evals/graders/judge.py):
- faithfulness: claims in the answer supported by the retrieved chunks;
- context_precision: retrieved chunks ranked by relevance to the reference answer;
- context_recall: reference answer covered by the retrieved chunks.
The retrieved chunks come from the ``ragflow_retrieval`` events the run recorded (the RAGFlow
references streamed with the answer), so this measures the actual run, not a separate retrieve call.
"""
from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.graders.code import retrieved_contexts  # noqa: E402
from evals.run_golden import RUNS_DIR, load_results, load_rows  # noqa: E402

METRIC_NAMES = ("faithfulness", "context_precision", "context_recall")


def shim_langchain_community() -> None:
    """ragas 0.4.3 imports the Vertex AI chat model that langchain-community 0.4 removed.

    The classes are only used in isinstance checks, so placeholders keep the import working.
    Remove once ragas no longer imports ``langchain_community.chat_models.vertexai``.
    """
    name = "langchain_community.chat_models.vertexai"
    if name not in sys.modules:
        module = types.ModuleType(name)
        module.ChatVertexAI = type("ChatVertexAI", (), {})
        sys.modules[name] = module
    import langchain_community.llms as llms
    try:
        llms.VertexAI
    except Exception:  # noqa: BLE001 - lazy attribute lookup raises when the integration is gone
        llms.VertexAI = type("VertexAI", (), {})


def build_samples(rows: list[dict], results: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    """(samples, skipped): one Ragas sample per kb row with an answer and retrieved chunks."""
    samples, skipped = [], []
    for row in rows:
        record = results.get(row["id"])
        if record is None:
            skipped.append({"id": row["id"], "why": "not in results"})
            continue
        contexts = retrieved_contexts(record["metrics"].get("events", []))
        if record.get("error") or not record.get("answer"):
            skipped.append({"id": row["id"], "why": record.get("error") or "empty answer"})
            continue
        if not contexts:
            skipped.append({"id": row["id"], "why": "no retrieved chunks recorded"})
            continue
        samples.append({"id": row["id"], "user_input": row["question"], "response": record["answer"],
                        "retrieved_contexts": contexts, "reference": row["expected_answer"]})
    return samples, skipped


def run_ragas(samples: list[dict]) -> list[dict]:
    shim_langchain_community()
    from ragas import EvaluationDataset, evaluate
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import Faithfulness, LLMContextPrecisionWithReference, LLMContextRecall
    from ragas.run_config import RunConfig

    from evals.graders.judge import build_judge_chat_model

    llm = LangchainLLMWrapper(build_judge_chat_model())
    dataset = EvaluationDataset.from_list([{k: v for k, v in s.items() if k != "id"} for s in samples])
    metrics = [Faithfulness(llm=llm), LLMContextPrecisionWithReference(llm=llm), LLMContextRecall(llm=llm)]
    result = evaluate(dataset=dataset, metrics=metrics, llm=llm, run_config=RunConfig(max_workers=4, timeout=180),
                      show_progress=False)
    frame = result.to_pandas()
    scores = []
    for sample, (_, row) in zip(samples, frame.iterrows()):
        entry = {"id": sample["id"], "n_contexts": len(sample["retrieved_contexts"])}
        for name in METRIC_NAMES:
            value = row.get(name)
            entry[name] = None if value is None or value != value else round(float(value), 4)  # NaN -> None
        scores.append(entry)
    return scores


def summarize(scores: list[dict]) -> dict:
    summary = {"rows": len(scores)}
    for name in METRIC_NAMES:
        values = [s[name] for s in scores if s.get(name) is not None]
        summary[name] = round(sum(values) / len(values), 4) if values else None
        summary[f"{name}_n"] = len(values)
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", required=True, help="run name under evals/runs/")
    parser.add_argument("--ids", nargs="*")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    run_dir = RUNS_DIR / args.run
    rows = load_rows(ids=args.ids, specialists=["kb"])
    results = load_results(run_dir / "results.jsonl")
    samples, skipped = build_samples(rows, results)
    if not samples:
        print(f"No gradable kb rows in {run_dir} ({len(skipped)} skipped).", file=sys.stderr)
        return 1
    print(f"Scoring {len(samples)} kb rows with Ragas ({len(skipped)} skipped)…", flush=True)
    scores = run_ragas(samples)
    report = {"run": args.run, "summary": summarize(scores), "scores": scores, "skipped": skipped}
    output = args.output or run_dir / "ragas.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
