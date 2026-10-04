"""Validate every row of the golden dataset (evals/golden/v1.jsonl). No live services."""
import json
import re
from collections import Counter
from pathlib import Path

import pytest

from evals.golden import build as golden_build

GOLDEN_DIR = Path(__file__).resolve().parent / "golden"

V1 = GOLDEN_DIR / "v1.jsonl"

REQUIRED = {"id", "specialist", "question", "mode", "expected_answer", "expected_sources",
            "expected_route", "difficulty", "tags", "grader"}
OPTIONAL = {"expected_values", "governance", "notes", "gold_passage_ids"}
SPECIALISTS = {"db", "kb", "web", "routing"}
ROUTES = {"database", "internet", "ragflow"}
DIFFICULTIES = {"easy", "medium", "hard"}
MODES = {"auto", "database", "internet", "ragflow"}
GRADER_METHODS = {"numeric", "contains_all", "contains_any", "routing", "llm_rubric"}
ID_PATTERN = re.compile(r"^(db|kb|web|route|gov)-\d{2,3}$")
SOURCE_PATTERN = re.compile(r"^(mongodb:[a-z_]+|ragflow:[A-Za-z0-9][A-Za-z0-9 _+.-]*|rag-mini-wikipedia:passage:\d+|[a-z0-9.-]+\.[a-z]{2,})$")


def load_rows() -> list[dict]:
    assert V1.exists(), "run `uv run python evals/golden/build.py`"
    return [json.loads(line) for line in V1.read_text(encoding="utf-8").splitlines() if line.strip()]


ROWS = load_rows() if V1.exists() else []


def test_dataset_is_up_to_date_with_build_script():
    assert golden_build.dumps(golden_build.build()) == V1.read_text(encoding="utf-8"), \
        "v1.jsonl is stale; run `uv run python evals/golden/build.py`"


def test_ids_are_unique_and_well_formed():
    ids = [r["id"] for r in ROWS]
    assert len(ids) == len(set(ids)), [i for i, n in Counter(ids).items() if n > 1]
    assert all(ID_PATTERN.match(i) for i in ids), [i for i in ids if not ID_PATTERN.match(i)]


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["id"])
def test_row_schema(row):
    keys = set(row)
    assert REQUIRED <= keys, f"missing {REQUIRED - keys}"
    assert keys <= REQUIRED | OPTIONAL, f"unexpected {keys - REQUIRED - OPTIONAL}"
    assert row["specialist"] in SPECIALISTS
    assert row["mode"] in MODES
    assert row["difficulty"] in DIFFICULTIES
    assert isinstance(row["question"], str) and row["question"].strip()
    assert isinstance(row["expected_answer"], str) and row["expected_answer"].strip()
    assert isinstance(row["tags"], list) and row["tags"] and all(isinstance(t, str) for t in row["tags"])
    assert isinstance(row["expected_route"], list) and row["expected_route"]
    assert set(row["expected_route"]) <= ROUTES and len(set(row["expected_route"])) == len(row["expected_route"])
    assert isinstance(row["expected_sources"], list)
    bad = [s for s in row["expected_sources"] if not SOURCE_PATTERN.match(s)]
    assert not bad, f"malformed expected_sources {bad}"
    grader = row["grader"]
    assert grader["method"] in GRADER_METHODS
    assert isinstance(grader["targets"], list) and grader["targets"]
    if grader["method"] == "routing":
        assert sorted(grader["targets"]) == sorted(row["expected_route"])
    if grader["method"] == "numeric":
        assert all(isinstance(t, (int, float)) for t in grader["targets"])


@pytest.mark.parametrize("row", [r for r in ROWS if r["specialist"] == "db"], ids=lambda r: r["id"])
def test_db_rows_name_a_collection(row):
    assert row["expected_route"] == ["database"]
    assert row["expected_sources"] and all(s.startswith("mongodb:") for s in row["expected_sources"])
    assert set(row["expected_sources"]) <= {"mongodb:drugs", "mongodb:inventory", "mongodb:sales_records"}


@pytest.mark.parametrize("row", [r for r in ROWS if r["specialist"] == "web"], ids=lambda r: r["id"])
def test_web_rows_name_a_source_domain(row):
    assert row["expected_route"] == ["internet"]
    assert row["expected_sources"], "web rows need at least one expected source domain"
    assert all("." in s and ":" not in s for s in row["expected_sources"])


@pytest.mark.parametrize("row", [r for r in ROWS if r["specialist"] == "kb"], ids=lambda r: r["id"])
def test_kb_rows_have_gold_passages(row):
    assert row["expected_route"] == ["ragflow"]
    assert row.get("gold_passage_ids"), "kb rows need gold passage ids"
    assert all(isinstance(p, int) for p in row["gold_passage_ids"])
    assert any(s.startswith("rag-mini-wikipedia:passage:") for s in row["expected_sources"])


@pytest.mark.parametrize("row", [r for r in ROWS if "governance" in r["tags"]], ids=lambda r: r["id"])
def test_governance_rows_list_private_tokens(row):
    assert row["governance"]["must_not_leak"], "governance rows need concrete private tokens"
    assert all(isinstance(t, str) and t.strip() for t in row["governance"]["must_not_leak"])


def test_governance_tokens_come_from_seed_data():
    """Every must_not_leak token should be traceable to the seed fixtures so the Day 3 leak check is real."""
    seed = "".join(p.read_text(encoding="utf-8") for p in golden_build.SEED_DIR.glob("*.json"))
    _, _, sales = golden_build.load_seed()
    derived = [str(int(sum(s["total_amount"] for s in sales)))]  # company totals are private too
    seed_compact = seed.replace(",", "") + " " + " ".join(derived)
    for row in ROWS:
        for token in row.get("governance", {}).get("must_not_leak", []):
            probe = token.replace(",", "").replace(" per", "").replace(" million", "")
            assert probe.split(".")[0] in seed_compact or probe in seed_compact, f"{row['id']}: {token!r} not in seed data"


def test_coverage_targets():
    counts = Counter(r["specialist"] for r in ROWS)
    assert counts["db"] >= 30
    assert counts["routing"] >= 20
    assert sum(1 for r in ROWS if "governance" in r["tags"]) >= 5
    assert counts["web"] >= 20
    assert counts["kb"] >= 40
    assert len(ROWS) >= 100
