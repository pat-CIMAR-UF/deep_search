"""Run golden-set rows through the coordinator and record answers, tool events, latency, and cost.

Usage:
    uv run python evals/run_golden.py --name v1_baseline                 # all rows -> evals/runs/v1_baseline/
    uv run python evals/run_golden.py --name smoke --limit 2             # smoke test
    uv run python evals/run_golden.py --name v1_baseline --specialist db web routing
    uv run python evals/run_golden.py --name v1_baseline --ids kb-01 kb-02 --resume
    uv run python evals/run_golden.py --name v1_baseline --ids route-04 --force     # re-run rows (last line wins)

Every row is appended to ``evals/runs/<name>/results.jsonl`` as soon as it finishes; ``--resume``
skips ids already present, so an interrupted run can be continued, and ``--force`` re-runs the
selected rows (the last line for an id wins). Each row is bounded by ``--timeout`` seconds (default
600) so a hung service call cannot stall the batch; a timed-out row is recorded as an error. ``run.json`` records the
configuration. Rows run sequentially so the single MCP session and the Gemini client are never
contended. Grading happens separately (promptfoo: evals/promptfoo/; Ragas: evals/graders/ragas_eval.py).

Requires the live services configured in .env (coordinator model, Gemini, MongoDB Atlas, RAGFlow).
"""
import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.run_baseline import estimate_cost, load_pricing  # noqa: E402

EVALS_DIR = PROJECT_ROOT / "evals"
GOLDEN = EVALS_DIR / "golden" / "v1.jsonl"
RUNS_DIR = EVALS_DIR / "runs"
DEFAULT_PRICING = EVALS_DIR / "pricing.yaml"


def load_rows(path: Path = GOLDEN, ids=None, specialists=None, limit=None) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if ids:
        wanted = set(ids)
        rows = [r for r in rows if r["id"] in wanted]
    if specialists:
        rows = [r for r in rows if r["specialist"] in set(specialists)]
    if limit:
        rows = rows[:limit]
    return rows


def load_results(path: Path) -> dict[str, dict]:
    """Results keyed by row id; a later line for the same id wins."""
    if not path.exists():
        return {}
    results = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            results[record["id"]] = record
    return results


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT_ROOT, capture_output=True,
                              text=True, check=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001 - metadata only
        return "unknown"


def coordinator_label() -> str:
    from agent.llm import provider_settings
    try:
        settings = provider_settings()
        return f"{settings['provider']}:{settings['model']}"
    except Exception:  # noqa: BLE001 - metadata only
        return os.getenv("LLM_PROVIDER", "unknown")


DEFAULT_TIMEOUT_S = 600


async def run_row(row: dict, pricing: dict, run_name: str, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    """Run one golden row and return the result record (never raises for agent failures)."""
    from agent.main_agent import run_deep_agent
    from agent.metrics import RunMetrics
    from api.context import reset_run_metrics, set_run_metrics

    metrics = RunMetrics()
    token = set_run_metrics(metrics)
    session_id = f"golden-{run_name}-{row['id']}"[:80]
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    answer, error = "", None
    started = time.perf_counter()
    try:
        answer = await asyncio.wait_for(
            run_deep_agent(row["question"], session_id, history=[], mode=row.get("mode", "auto")), timeout=timeout_s)
    except asyncio.TimeoutError:
        error = f"TimeoutError: row exceeded {timeout_s:.0f}s"
    except Exception as exc:  # noqa: BLE001 - the harness records failures instead of aborting the batch
        error = f"{type(exc).__name__}: {exc}"
    finally:
        latency = time.perf_counter() - started
        reset_run_metrics(token)
    data = metrics.as_dict()
    return {
        "id": row["id"], "specialist": row["specialist"], "question": row["question"],
        "mode": row.get("mode", "auto"), "expected_route": row["expected_route"],
        "session_id": session_id, "started_at": started_at, "latency_s": round(latency, 2),
        "metrics": data, "cost_usd": estimate_cost(data, pricing), "answer": answer, "error": error,
    }


async def run_all(rows: list[dict], pricing: dict, run_name: str, results_path: Path,
                  timeout_s: float = DEFAULT_TIMEOUT_S) -> list[dict]:
    results = []
    with results_path.open("a", encoding="utf-8") as sink:
        for index, row in enumerate(rows, 1):
            print(f"[{index}/{len(rows)}] {row['id']}: {row['question'][:70]}", flush=True)
            result = await run_row(row, pricing, run_name, timeout_s)
            status = result["error"] or (f"{result['latency_s']}s, {result['metrics']['total_tokens']} tok, "
                                         f"{result['metrics']['tool_call_count']} tool calls, "
                                         f"sub-agents {result['metrics']['subagent_calls']}")
            print(f"    -> {status}", flush=True)
            sink.write(json.dumps(result, ensure_ascii=False) + "\n")
            sink.flush()
            results.append(result)
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                        help="run directory name under evals/runs/")
    parser.add_argument("--golden", type=Path, default=GOLDEN)
    parser.add_argument("--pricing", type=Path, default=DEFAULT_PRICING)
    parser.add_argument("--ids", nargs="*")
    parser.add_argument("--specialist", nargs="*", choices=["db", "kb", "web", "routing"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true", help="skip ids already in results.jsonl")
    parser.add_argument("--force", action="store_true", help="re-run the selected rows even if recorded")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S, help="seconds per row")
    args = parser.parse_args(argv)

    rows = load_rows(args.golden, ids=args.ids, specialists=args.specialist, limit=args.limit)
    run_dir = RUNS_DIR / args.name
    run_dir.mkdir(parents=True, exist_ok=True)
    results_path = run_dir / "results.jsonl"
    if args.resume:
        done = load_results(results_path)
        rows = [r for r in rows if r["id"] not in done]
    elif args.force:
        pass
    elif results_path.exists() and results_path.stat().st_size:
        print(f"{results_path} exists; pass --resume to continue it or choose another --name.", file=sys.stderr)
        return 1
    if not rows:
        print("No rows selected (all done?).", file=sys.stderr)
        return 0
    pricing = load_pricing(args.pricing)
    meta_path = run_dir / "run.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {
        "name": args.name, "golden": str(args.golden.relative_to(PROJECT_ROOT)) if args.golden.is_relative_to(PROJECT_ROOT) else str(args.golden),
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": git_commit(), "coordinator": coordinator_label(), "pricing": pricing, "invocations": [],
    }
    meta["invocations"].append({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "rows": [r["id"] for r in rows], "argv": sys.argv[1:]})
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    results = asyncio.run(run_all(rows, pricing, args.name, results_path, args.timeout))
    errors = [r["id"] for r in results if r["error"]]
    print(f"\n{len(results)} rows, {len(errors)} errors {errors if errors else ''}; "
          f"total cost ${sum(r['cost_usd'] for r in results):.4f}\nWrote {results_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
