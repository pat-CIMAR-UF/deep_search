"""Build the scorecard for a graded golden run.

Usage:
    uv run python evals/score.py --run v1_baseline                    # -> evals/reports/v1_baseline.md + evals/runs/v1_baseline/scores.json
    uv run python evals/score.py --run v1_baseline --report evals/reports/custom.md

Inputs under evals/runs/<run>/: ``results.jsonl`` (evals/run_golden.py), ``promptfoo.json``
(evals/promptfoo/eval.sh) and, when present, ``ragas.json`` (evals/graders/ragas_eval.py) and
``agreement.json`` (evals/calibration/agreement.py). The report has one table per sub-agent plus
routing, governance, Ragas, and failure detail.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.graders.judge import rating_from_reason  # noqa: E402
from evals.run_baseline import percentile  # noqa: E402
from evals.run_golden import RUNS_DIR, load_results, load_rows  # noqa: E402

REPORTS_DIR = PROJECT_ROOT / "evals" / "reports"
SPECIALIST_LABELS = {"db": "Database Query Agent", "kb": "RAGFlow Agent (knowledge base)",
                     "web": "Network Search Agent", "routing": "Coordinator routing"}
METRICS = ("answer", "routing", "governance", "citations", "groundedness", "completeness", "report_quality")


def load_promptfoo(path: Path) -> dict[str, dict]:
    """Per-row grading from promptfoo's JSON output, keyed by golden id."""
    data = json.loads(path.read_text(encoding="utf-8"))
    rows: dict[str, dict] = {}
    for result in data["results"]["results"]:
        row_id = (result.get("vars") or {}).get("id")
        if not row_id:
            continue
        grades = {}
        for component in ((result.get("gradingResult") or {}).get("componentResults") or []):
            metric = (component.get("assertion") or {}).get("metric")
            if not metric:
                continue
            grade = {"pass": bool(component.get("pass")), "score": float(component.get("score") or 0.0),
                     "reason": component.get("reason") or ""}
            if metric == "report_quality":
                grade["rating"] = rating_from_reason(grade["reason"], grade["score"])
            grades[metric] = grade
        rows[row_id] = {"grades": grades, "error": result.get("error"), "success": result.get("success")}
    return rows


def score_rows(rows: list[dict], results: dict[str, dict], graded: dict[str, dict]) -> list[dict]:
    scored = []
    for row in rows:
        record = results.get(row["id"], {})
        grade = graded.get(row["id"], {})
        scored.append({
            "id": row["id"], "specialist": row["specialist"], "difficulty": row["difficulty"], "tags": row.get("tags", []),
            "expected_route": row["expected_route"], "grades": grade.get("grades", {}),
            "harness_error": grade.get("error"), "agent_error": record.get("error"),
            "latency_s": record.get("latency_s"), "cost_usd": record.get("cost_usd"),
            "total_tokens": (record.get("metrics") or {}).get("total_tokens"),
            "subagent_calls": (record.get("metrics") or {}).get("subagent_calls", {}),
        })
    return scored


def pass_rate(scored: list[dict], metric: str) -> tuple[int, int]:
    graded = [s for s in scored if metric in s["grades"]]
    return sum(1 for s in graded if s["grades"][metric]["pass"]), len(graded)


def mean_score(scored: list[dict], metric: str) -> float | None:
    values = [s["grades"][metric]["score"] for s in scored if metric in s["grades"]]
    return round(statistics.fmean(values), 3) if values else None


def mean_rating(scored: list[dict]) -> float | None:
    values = [s["grades"]["report_quality"].get("rating") for s in scored if "report_quality" in s["grades"]]
    values = [v for v in values if v]
    return round(statistics.fmean(values), 2) if values else None


def summarize(scored: list[dict]) -> dict:
    ok = [s for s in scored if s["latency_s"] is not None and not s["agent_error"]]
    latencies = [s["latency_s"] for s in ok]
    summary = {"rows": len(scored), "agent_errors": sum(1 for s in scored if s["agent_error"]),
               "harness_errors": sum(1 for s in scored if s["harness_error"] and not s["grades"]),
               "latency_p50_s": percentile(latencies, 0.5), "latency_p95_s": percentile(latencies, 0.95),
               "mean_cost_usd": round(statistics.fmean(s["cost_usd"] for s in ok), 4) if ok else None,
               "total_cost_usd": round(sum(s["cost_usd"] for s in ok), 4) if ok else 0.0,
               "report_quality_rating": mean_rating(scored)}
    for metric in METRICS:
        passed, total = pass_rate(scored, metric)
        summary[metric] = {"pass": passed, "n": total, "rate": round(passed / total, 3) if total else None,
                           "mean_score": mean_score(scored, metric)}
    return summary


def fmt_rate(cell: dict, with_mean: bool = False) -> str:
    if not cell["n"]:
        return "–"
    text = f"{cell['pass']}/{cell['n']} ({cell['rate'] * 100:.0f}%)"
    if with_mean and cell.get("mean_score") is not None:
        text += f", mean {cell['mean_score']:.2f}"
    return text


def fmt(value, digits=1) -> str:
    if value is None:
        return "–"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def specialist_table(summaries: dict[str, dict]) -> str:
    lines = ["| sub-agent | n | answer (code) | routing exact | groundedness | completeness | report quality (1–5) | citations | governance | p50 s | p95 s | mean cost $ | errors |",
             "|---|---:|---|---|---|---|---:|---|---|---:|---:|---:|---:|"]
    for key, summary in summaries.items():
        lines.append(f"| {SPECIALIST_LABELS.get(key, key)} | {summary['rows']} | {fmt_rate(summary['answer'])} | "
                     f"{fmt_rate(summary['routing'])} | {fmt_rate(summary['groundedness'], True)} | {fmt_rate(summary['completeness'])} | "
                     f"{fmt(summary['report_quality_rating'], 2)} | {fmt_rate(summary['citations'], True)} | {fmt_rate(summary['governance'])} | "
                     f"{fmt(summary['latency_p50_s'])} | {fmt(summary['latency_p95_s'])} | {fmt(summary['mean_cost_usd'], 4)} | "
                     f"{summary['agent_errors']} |")
    return "\n".join(lines)


def difficulty_table(scored: list[dict]) -> str:
    lines = ["| difficulty | n | answer | routing | groundedness | completeness | report quality |", "|---|---:|---|---|---|---|---:|"]
    for level in ("easy", "medium", "hard"):
        subset = [s for s in scored if s["difficulty"] == level]
        if not subset:
            continue
        summary = summarize(subset)
        lines.append(f"| {level} | {len(subset)} | {fmt_rate(summary['answer'])} | {fmt_rate(summary['routing'])} | "
                     f"{fmt_rate(summary['groundedness'])} | {fmt_rate(summary['completeness'])} | {fmt(summary['report_quality_rating'], 2)} |")
    return "\n".join(lines)


def routing_table(scored: list[dict]) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    for s in scored:
        groups["+".join(s["expected_route"])].append(s)
    lines = ["| gold route | n | exact | extra fan-out | missed specialist |", "|---|---:|---|---:|---:|"]
    for route, subset in sorted(groups.items()):
        graded = [s for s in subset if "routing" in s["grades"]]
        exact = sum(1 for s in graded if s["grades"]["routing"]["pass"])
        extra = sum(1 for s in graded if "extra" in s["grades"]["routing"]["reason"])
        missing = sum(1 for s in graded if "missing" in s["grades"]["routing"]["reason"])
        lines.append(f"| {route} | {len(graded)} | {exact}/{len(graded)} | {extra} | {missing} |")
    return "\n".join(lines)


def governance_table(scored: list[dict]) -> str:
    rows = [s for s in scored if "governance" in s["grades"]]
    if not rows:
        return "_No governance rows graded._"
    lines = ["| id | routing | governance | detail |", "|---|---|---|---|"]
    for s in rows:
        routing = s["grades"].get("routing", {})
        gov = s["grades"]["governance"]
        lines.append(f"| {s['id']} | {'pass' if routing.get('pass') else 'fail'}: {routing.get('reason', '')} | "
                     f"{'pass' if gov['pass'] else 'LEAK'} | {gov['reason'][:140]} |")
    return "\n".join(lines)


def ragas_table(ragas: dict | None) -> str:
    if not ragas:
        return "_Ragas not run for this run (evals/graders/ragas_eval.py)._"
    summary = ragas["summary"]
    lines = ["| metric | mean | rows |", "|---|---:|---:|"]
    for name in ("faithfulness", "context_precision", "context_recall"):
        lines.append(f"| {name} | {fmt(summary.get(name), 3)} | {summary.get(f'{name}_n', 0)} |")
    if ragas.get("skipped"):
        lines.append(f"\n{len(ragas['skipped'])} kb rows skipped: " + "; ".join(f"{s['id']} ({s['why']})" for s in ragas["skipped"][:10]))
    return "\n".join(lines)


def agreement_section(agreement: dict | None) -> str:
    if not agreement:
        return ("_Judge calibration pending: sample outputs with `evals/calibration/sample.py`, hand-grade them, then run "
                "`evals/calibration/agreement.py`._")
    lines = ["| metric | n | agreement | note |", "|---|---:|---:|---|"]
    for name, cell in agreement["metrics"].items():
        lines.append(f"| {name} | {cell['n']} | {cell['agreement'] * 100:.0f}% | {cell.get('note', '')} |")
    return "\n".join(lines)


def failures_table(scored: list[dict]) -> str:
    lines = ["| id | failing metrics | detail |", "|---|---|---|"]
    count = 0
    for s in scored:
        failing = [m for m in METRICS if m in s["grades"] and not s["grades"][m]["pass"]]
        if s["agent_error"]:
            failing.insert(0, "agent error")
        if not failing:
            continue
        count += 1
        detail = s["agent_error"] or "; ".join(f"{m}: {s['grades'][m]['reason'][:110]}" for m in failing if m in s["grades"])
        lines.append(f"| {s['id']} | {', '.join(failing)} | {detail.replace('|', '/')} |")
    return "\n".join(lines) if count else "_No failures._"


def per_row_table(scored: list[dict]) -> str:
    lines = ["| id | answer | routing | grounded | complete | quality | citations | governance | latency s | cost $ |",
             "|---|---|---|---|---|---:|---|---|---:|---:|"]
    for s in scored:
        def cell(metric):
            grade = s["grades"].get(metric)
            if grade is None:
                return "–"
            return "✓" if grade["pass"] else "✗"
        quality = s["grades"].get("report_quality", {}).get("rating")
        lines.append(f"| {s['id']} | {cell('answer')} | {cell('routing')} | {cell('groundedness')} | {cell('completeness')} | "
                     f"{quality or '–'} | {cell('citations')} | {cell('governance')} | {fmt(s['latency_s'])} | {fmt(s['cost_usd'], 4)} |")
    return "\n".join(lines)


def build_report(run: str, meta: dict, scored: list[dict], ragas: dict | None, agreement: dict | None) -> str:
    by_specialist = {key: summarize([s for s in scored if s["specialist"] == key])
                     for key in ("db", "kb", "web", "routing") if any(s["specialist"] == key for s in scored)}
    overall = summarize(scored)
    judge = meta.get("judge", "Azure deployment (evals/graders/judge.py)")
    parts = [
        f"# Scorecard: {run}",
        "",
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} from `evals/runs/{run}/` "
        f"(golden set `{meta.get('golden', 'evals/golden/v1.jsonl')}`, commit `{meta.get('git_commit', '?')}`, "
        f"coordinator `{meta.get('coordinator', '?')}`, judge `{judge}`).",
        "",
        "Metrics: **answer** = the row's code grader (numeric / contains); **routing exact** = delegated specialists equal "
        "the gold route (extra fan-out fails); **groundedness** = LLM judge over the evidence recorded during the run; "
        "**completeness** = LLM judge against the gold answer; **report quality** = LLM judge, 1–5 rubric; "
        "**citations** = every cited URL resolves with HTTP 200 and mentions a key term (rows with a web route; mean = share of "
        "valid URLs, 0 when the answer cites none); "
        "**governance** = no private token in outbound web queries (gov rows).",
        "",
        "## Per sub-agent",
        "",
        specialist_table(by_specialist),
        "",
        f"Overall: {overall['rows']} rows, {overall['agent_errors']} agent errors, total estimated cost "
        f"${overall['total_cost_usd']:.2f}, p50 {fmt(overall['latency_p50_s'])} s, p95 {fmt(overall['latency_p95_s'])} s.",
        "",
        "## By difficulty",
        "",
        difficulty_table(scored),
        "",
        "## Routing",
        "",
        routing_table(scored),
        "",
        "## Governance rows",
        "",
        governance_table(scored),
        "",
        "## Ragas (knowledge-base rows)",
        "",
        ragas_table(ragas),
        "",
        "## Judge calibration",
        "",
        agreement_section(agreement),
        "",
        "## Failures",
        "",
        failures_table(scored),
        "",
        "## Per row",
        "",
        per_row_table(scored),
        "",
    ]
    return "\n".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    run_dir = RUNS_DIR / args.run
    promptfoo_path = run_dir / "promptfoo.json"
    if not promptfoo_path.exists():
        print(f"{promptfoo_path} missing; grade the run with evals/promptfoo/eval.sh {args.run}", file=sys.stderr)
        return 1
    results = load_results(run_dir / "results.jsonl")
    rows = [r for r in load_rows() if r["id"] in results]
    graded = load_promptfoo(promptfoo_path)
    scored = score_rows(rows, results, graded)
    meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8")) if (run_dir / "run.json").exists() else {}
    ragas = json.loads((run_dir / "ragas.json").read_text(encoding="utf-8")) if (run_dir / "ragas.json").exists() else None
    agreement = json.loads((run_dir / "agreement.json").read_text(encoding="utf-8")) if (run_dir / "agreement.json").exists() else None
    report = build_report(args.run, meta, scored, ragas, agreement)
    report_path = args.report or REPORTS_DIR / f"{args.run}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    summary = {"run": args.run, "overall": summarize(scored),
               "by_specialist": {k: summarize([s for s in scored if s["specialist"] == k]) for k in ("db", "kb", "web", "routing")},
               "ragas": ragas["summary"] if ragas else None, "agreement": agreement, "rows": scored}
    (run_dir / "scores.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(specialist_table({k: v for k, v in summary["by_specialist"].items() if v["rows"]}))
    print(f"\nWrote {report_path} and {run_dir / 'scores.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
