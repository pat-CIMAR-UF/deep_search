"""Generate promptfoo test cases from the golden set (``tests: file://golden_tests.py:generate_tests``).

One test per golden row. The row's fields become vars; the assertions are chosen from the row:
answer (code grader), routing, governance, citations, groundedness, completeness, report_quality.
All are Python assertions in asserts.py; the three judge metrics render their rubrics from
``prompt/prompts.yaml`` (``evals.judge``) so the judge is versioned with the other prompts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.run_golden import load_rows  # noqa: E402

ASSERT_FILE = "file://asserts.py"


def python_assert(function: str, metric: str | None = None) -> dict:
    return {"type": "python", "value": f"{ASSERT_FILE}:{function}", "metric": metric or function}


def test_case(row: dict) -> dict:
    grader = row.get("grader", {})
    governance = (row.get("governance") or {}).get("must_not_leak") or []
    # promptfoo flattens list vars into strings before they reach Python assertions, so lists travel as JSON.
    vars_ = {
        "id": row["id"], "specialist": row["specialist"], "question": row["question"], "mode": row.get("mode", "auto"),
        "expected_answer": row["expected_answer"], "expected_route": json.dumps(row["expected_route"]),
        "expected_sources": json.dumps(row.get("expected_sources", [])), "difficulty": row["difficulty"],
        "tags": json.dumps(row.get("tags", [])), "grader_method": grader.get("method") or "",
        "grader_targets": json.dumps(grader.get("targets", [])), "must_not_leak": json.dumps(governance),
        "gold_passage_ids": json.dumps(row.get("gold_passage_ids", [])),
    }
    asserts = []
    if grader.get("method") in {"numeric", "contains_all", "contains_any"}:
        asserts.append(python_assert("answer"))
    asserts.append(python_assert("routing"))
    if governance:
        asserts.append(python_assert("governance"))
    if "internet" in row["expected_route"]:
        asserts.append(python_assert("citations"))
    asserts.append(python_assert("groundedness"))
    asserts.append(python_assert("completeness"))
    asserts.append(python_assert("report_quality"))
    return {
        "description": f"{row['id']}: {row['question'][:70]}",
        "vars": vars_,
        "assert": asserts,
        "metadata": {"specialist": row["specialist"], "difficulty": row["difficulty"], "tags": row.get("tags", [])},
    }


def generate_tests(ids: list[str] | None = None, specialists: list[str] | None = None) -> list[dict]:
    return [test_case(row) for row in load_rows(ids=ids, specialists=specialists)]
