"""Judge-versus-human agreement on the calibration sample.

Usage:
    uv run python evals/calibration/agreement.py --run v1_baseline
    # -> evals/runs/v1_baseline/agreement.json (picked up by evals/score.py) and a Markdown summary

Reads evals/calibration/<run>/human_grades.jsonl (filled in by hand) and the judge verdicts in
evals/runs/<run>/promptfoo.json. Agreement is the share of rows where judge and human give the same
pass/fail (groundedness, completeness) or a rating within one point (report_quality); Cohen's kappa
is reported for the binary metrics. Rows still marked null are skipped and counted as pending.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.run_golden import RUNS_DIR  # noqa: E402
from evals.score import load_promptfoo  # noqa: E402

CALIBRATION_DIR = PROJECT_ROOT / "evals" / "calibration"


def load_human(path: Path) -> dict[str, dict]:
    grades = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            grades[record["id"]] = record
    return grades


def as_bool(value) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "pass", "yes", "y", "1"}:
            return True
        if lowered in {"false", "fail", "no", "n", "0"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def cohen_kappa(pairs: list[tuple[bool, bool]]) -> float | None:
    n = len(pairs)
    if n == 0:
        return None
    agree = sum(1 for a, b in pairs if a == b) / n
    p_a_true = sum(1 for a, _ in pairs if a) / n
    p_b_true = sum(1 for _, b in pairs if b) / n
    expected = p_a_true * p_b_true + (1 - p_a_true) * (1 - p_b_true)
    if expected == 1.0:
        return 1.0
    return round((agree - expected) / (1 - expected), 3)


def compute_agreement(human: dict[str, dict], judged: dict[str, dict]) -> dict:
    metrics: dict[str, dict] = {}
    disagreements: list[dict] = []
    for metric in ("groundedness", "completeness"):
        pairs, ids = [], []
        for row_id, record in human.items():
            value = as_bool(record.get(metric))
            verdict = judged.get(row_id, {}).get("grades", {}).get(metric)
            if value is None or verdict is None:
                continue
            pairs.append((verdict["pass"], value))
            ids.append(row_id)
            if verdict["pass"] != value:
                disagreements.append({"id": row_id, "metric": metric, "judge": verdict["pass"], "human": value,
                                      "judge_reason": verdict["reason"][:200], "notes": record.get("notes", "")})
        n = len(pairs)
        metrics[metric] = {"n": n, "agreement": round(sum(1 for a, b in pairs if a == b) / n, 3) if n else None,
                           "kappa": cohen_kappa(pairs), "note": f"kappa {cohen_kappa(pairs)}" if n else "pending"}
    pairs, exact = [], 0
    for row_id, record in human.items():
        value = record.get("report_quality")
        verdict = judged.get(row_id, {}).get("grades", {}).get("report_quality")
        if value is None or verdict is None or verdict.get("rating") is None:
            continue
        try:
            value = int(value)
        except (TypeError, ValueError):
            continue
        pairs.append((verdict["rating"], value))
        if verdict["rating"] == value:
            exact += 1
        if abs(verdict["rating"] - value) > 1:
            disagreements.append({"id": row_id, "metric": "report_quality", "judge": verdict["rating"], "human": value,
                                  "judge_reason": verdict["reason"][:200], "notes": record.get("notes", "")})
    n = len(pairs)
    within_one = sum(1 for a, b in pairs if abs(a - b) <= 1)
    mae = round(sum(abs(a - b) for a, b in pairs) / n, 2) if n else None
    metrics["report_quality"] = {"n": n, "agreement": round(within_one / n, 3) if n else None,
                                 "exact": round(exact / n, 3) if n else None, "mae": mae,
                                 "note": f"within ±1; exact {exact}/{n}, MAE {mae}" if n else "pending"}
    pending = [row_id for row_id, record in human.items()
               if any(record.get(m) is None for m in ("groundedness", "completeness", "report_quality"))]
    graded = [m for m in metrics.values() if m["n"]]
    overall = round(sum(m["agreement"] for m in graded) / len(graded), 3) if graded else None
    return {"metrics": metrics, "overall_agreement": overall, "pending": pending, "disagreements": disagreements,
            "target": 0.8}


def markdown(agreement: dict) -> str:
    lines = ["| metric | n | agreement | note |", "|---|---:|---:|---|"]
    for name, cell in agreement["metrics"].items():
        rate = f"{cell['agreement'] * 100:.0f}%" if cell["agreement"] is not None else "–"
        lines.append(f"| {name} | {cell['n']} | {rate} | {cell['note']} |")
    overall = agreement["overall_agreement"]
    lines.append(f"\nOverall agreement: {overall * 100:.0f}% (target ≥ 80%)" if overall is not None else "\nNo graded rows yet.")
    if agreement["pending"]:
        lines.append(f"Pending human grades: {', '.join(agreement['pending'])}")
    if agreement["disagreements"]:
        lines += ["", "| id | metric | judge | human | judge reason | notes |", "|---|---|---|---|---|---|"]
        for d in agreement["disagreements"]:
            lines.append(f"| {d['id']} | {d['metric']} | {d['judge']} | {d['human']} | {d['judge_reason'].replace('|', '/')} | {d['notes']} |")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    human_path = CALIBRATION_DIR / args.run / "human_grades.jsonl"
    promptfoo_path = RUNS_DIR / args.run / "promptfoo.json"
    if not human_path.exists() or not promptfoo_path.exists():
        print(f"need {human_path} and {promptfoo_path}", file=sys.stderr)
        return 1
    agreement = compute_agreement(load_human(human_path), load_promptfoo(promptfoo_path))
    (RUNS_DIR / args.run / "agreement.json").write_text(json.dumps(agreement, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(markdown(agreement))
    print(f"\nWrote {RUNS_DIR / args.run / 'agreement.json'}; re-run evals/score.py --run {args.run} to refresh the report.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
