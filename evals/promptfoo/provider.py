"""promptfoo provider for Deep Search: replay a recorded golden run, or run the coordinator live.

promptfoo calls ``call_api(prompt, options, context)`` once per test. The row id comes from
``context["vars"]["id"]``. In ``replay`` mode (default) the answer and tool events are read from
``evals/runs/<EVAL_RUN>/results.jsonl``; in ``live`` mode the row is run through
``evals/run_golden.run_row`` and appended to that file, so grading and calibration read one source.

Provider metadata handed to the assertions: events, subagent_calls, evidence, latency, cost, error.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.graders.code import evidence_text  # noqa: E402
from evals.run_golden import RUNS_DIR, load_results  # noqa: E402

DEFAULT_RUN = "v1_baseline"
_cache: dict[str, tuple[float, dict[str, dict]]] = {}


def run_name(config: dict) -> str:
    return os.getenv("EVAL_RUN") or config.get("run") or DEFAULT_RUN


def results_path(config: dict) -> Path:
    if config.get("results"):
        return Path(config["results"])
    return RUNS_DIR / run_name(config) / "results.jsonl"


def cached_results(path: Path) -> dict[str, dict]:
    mtime = path.stat().st_mtime if path.exists() else -1.0
    hit = _cache.get(str(path))
    if hit is None or hit[0] != mtime:
        hit = (mtime, load_results(path))
        _cache[str(path)] = hit
    return hit[1]


def response_from_record(record: dict) -> dict:
    metrics = record.get("metrics", {})
    events = metrics.get("events", [])
    output = record.get("answer") or ""
    if record.get("error") and not output:
        output = f"[agent error] {record['error']}"
    return {
        "output": output,
        "metadata": {
            "id": record["id"], "error": record.get("error"), "session_id": record.get("session_id"),
            "latency_s": record.get("latency_s"), "cost_usd": record.get("cost_usd"),
            "subagent_calls": metrics.get("subagent_calls", {}), "tool_calls": metrics.get("tool_calls", {}),
            "total_tokens": metrics.get("total_tokens"), "events": events, "evidence": evidence_text(events),
        },
        "tokenUsage": {"prompt": metrics.get("input_tokens", 0), "completion": metrics.get("output_tokens", 0),
                       "total": metrics.get("total_tokens", 0)},
    }


def run_live(row_id: str, vars_: dict, config: dict) -> dict:
    from evals.run_baseline import load_pricing
    from evals.run_golden import DEFAULT_PRICING, run_row
    row = {"id": row_id, "specialist": vars_.get("specialist", ""), "question": vars_["question"],
           "mode": vars_.get("mode", "auto"), "expected_route": vars_.get("expected_route", [])}
    name = run_name(config)
    record = asyncio.run(run_row(row, load_pricing(DEFAULT_PRICING), name))
    path = results_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as sink:
        sink.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def call_api(prompt: str, options: dict | None = None, context: dict | None = None) -> dict:
    config = (options or {}).get("config") or {}
    vars_ = (context or {}).get("vars") or {}
    row_id = vars_.get("id")
    if not row_id:
        return {"error": "test case has no 'id' var; generate tests with golden_tests.py"}
    mode = os.getenv("EVAL_MODE") or config.get("mode") or "replay"
    if mode == "live":
        return response_from_record(run_live(row_id, vars_, config))
    path = results_path(config)
    record = cached_results(path).get(row_id)
    if record is None:
        return {"error": f"no recorded result for {row_id} in {path}; run evals/run_golden.py first"}
    return response_from_record(record)
