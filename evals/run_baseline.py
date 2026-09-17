"""Run representative questions through the coordinator and record latency, tokens, tool calls, and cost.

Usage:
    uv run python evals/run_baseline.py                 # all questions -> evals/baseline.json
    uv run python evals/run_baseline.py --limit 2       # smoke test
    uv run python evals/run_baseline.py --ids db-01 kb-03 --output evals/scratch.json

Requires the live services configured in .env (coordinator model, Gemini, MongoDB Atlas, RAGFlow).
Questions run sequentially so the single MCP session and the Gemini client are never contended.
"""
import argparse
import asyncio
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

EVALS_DIR = PROJECT_ROOT / "evals"
DEFAULT_QUESTIONS = EVALS_DIR / "baseline_questions.jsonl"
DEFAULT_PRICING = EVALS_DIR / "pricing.yaml"
DEFAULT_OUTPUT = EVALS_DIR / "baseline.json"


def load_questions(path: Path, ids=None, limit=None) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if ids:
        wanted = set(ids)
        rows = [r for r in rows if r["id"] in wanted]
    if limit:
        rows = rows[:limit]
    return rows


def load_pricing(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def estimate_cost(metrics: dict, pricing: dict) -> float:
    """USD for one run: coordinator tokens plus Gemini grounding tokens at the configured rates."""
    c, g = pricing["coordinator"], pricing["gemini"]
    cost = (metrics.get("input_tokens", 0) * c["input_per_million"]
            + metrics.get("output_tokens", 0) * c["output_per_million"]
            + metrics.get("gemini_input_tokens", 0) * g["input_per_million"]
            + metrics.get("gemini_output_tokens", 0) * g["output_per_million"]) / 1_000_000
    return round(cost, 6)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return round(values[0], 2)
    ranked = sorted(values)
    position = (len(ranked) - 1) * pct
    low, high = int(position), min(int(position) + 1, len(ranked) - 1)
    return round(ranked[low] + (ranked[high] - ranked[low]) * (position - low), 2)


def aggregate(rows: list[dict]) -> dict:
    ok = [r for r in rows if not r["error"]]
    latencies = [r["latency_s"] for r in ok]
    def mean(key):
        return round(statistics.fmean(r["metrics"][key] for r in ok), 1) if ok else 0.0
    return {
        "questions": len(rows),
        "errors": len(rows) - len(ok),
        "latency_p50_s": percentile(latencies, 0.5),
        "latency_p95_s": percentile(latencies, 0.95),
        "latency_mean_s": round(statistics.fmean(latencies), 2) if latencies else 0.0,
        "mean_input_tokens": mean("input_tokens"),
        "mean_output_tokens": mean("output_tokens"),
        "mean_gemini_tokens": round(statistics.fmean(
            r["metrics"]["gemini_input_tokens"] + r["metrics"]["gemini_output_tokens"] for r in ok), 1) if ok else 0.0,
        "mean_llm_calls": mean("llm_calls"),
        "mean_tool_calls": mean("tool_call_count"),
        "mean_cost_usd": round(statistics.fmean(r["cost_usd"] for r in ok), 5) if ok else 0.0,
        "total_cost_usd": round(sum(r["cost_usd"] for r in ok), 4),
    }


def by_route(rows: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault("+".join(row["expected_route"]), []).append(row)
    return {route: aggregate(group) for route, group in sorted(groups.items())}


def markdown_table(rows: list[dict], summary: dict, routes: dict) -> str:
    lines = ["| id | route | latency s | in tok | out tok | gemini tok | llm calls | tool calls | sub-agents | cost $ | status |",
             "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|"]
    for r in rows:
        m = r["metrics"]
        subs = ", ".join(f"{k}×{v}" for k, v in m["subagent_calls"].items()) or "-"
        status = "error" if r["error"] else "ok"
        lines.append(f"| {r['id']} | {'+'.join(r['expected_route'])} | {r['latency_s']:.1f} | {m['input_tokens']} | "
                     f"{m['output_tokens']} | {m['gemini_input_tokens'] + m['gemini_output_tokens']} | {m['llm_calls']} | "
                     f"{m['tool_call_count']} | {subs} | {r['cost_usd']:.4f} | {status} |")
    lines += ["", "| route | n | errors | p50 s | p95 s | mean tokens | mean tool calls | mean cost $ |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for route, agg in list(routes.items()) + [("all", summary)]:
        lines.append(f"| {route} | {agg['questions']} | {agg['errors']} | {agg['latency_p50_s']} | {agg['latency_p95_s']} | "
                     f"{agg['mean_input_tokens'] + agg['mean_output_tokens']:.0f} | {agg['mean_tool_calls']} | {agg['mean_cost_usd']:.4f} |")
    return "\n".join(lines)


async def run_one(row: dict, pricing: dict, stamp: str) -> dict:
    from agent.main_agent import run_deep_agent
    from agent.metrics import RunMetrics
    from api.context import reset_run_metrics, set_run_metrics

    metrics = RunMetrics()
    token = set_run_metrics(metrics)
    session_id = f"baseline-{stamp}-{row['id']}"
    answer, error = "", None
    started = time.perf_counter()
    try:
        answer = await run_deep_agent(row["question"], session_id, history=[], mode=row.get("mode", "auto"))
    except Exception as exc:  # noqa: BLE001 - the harness records failures instead of aborting the batch
        error = f"{type(exc).__name__}: {exc}"
    finally:
        latency = time.perf_counter() - started
        reset_run_metrics(token)
    data = metrics.as_dict()
    return {
        "id": row["id"], "question": row["question"], "expected_route": row["expected_route"],
        "tags": row.get("tags", []), "session_id": session_id,
        "latency_s": round(latency, 2), "metrics": data, "cost_usd": estimate_cost(data, pricing),
        "answer_chars": len(answer), "answer_preview": answer[:300], "error": error,
    }


async def run_all(rows: list[dict], pricing: dict, stamp: str) -> list[dict]:
    results = []
    for index, row in enumerate(rows, 1):
        print(f"[{index}/{len(rows)}] {row['id']}: {row['question'][:70]}", flush=True)
        result = await run_one(row, pricing, stamp)
        status = result["error"] or f"{result['latency_s']}s, {result['metrics']['total_tokens']} tok, {result['metrics']['tool_call_count']} tool calls"
        print(f"    -> {status}", flush=True)
        results.append(result)
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--pricing", type=Path, default=DEFAULT_PRICING)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--ids", nargs="*")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args(argv)

    rows = load_questions(args.questions, ids=args.ids, limit=args.limit)
    if not rows:
        print("No questions selected.", file=sys.stderr)
        return 1
    pricing = load_pricing(args.pricing)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = asyncio.run(run_all(rows, pricing, stamp))
    summary, routes = aggregate(results), by_route(results)
    report = {
        "run_at": stamp, "questions_file": str(args.questions.relative_to(PROJECT_ROOT)),
        "pricing": pricing, "summary": summary, "by_route": routes, "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print(markdown_table(results, summary, routes))
    print(f"\nWrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
