"""Tests for the evals/run_baseline.py harness math (no live services)."""
import pytest

from evals import run_baseline

PRICING = {"coordinator": {"input_per_million": 1.0, "output_per_million": 2.0},
           "gemini": {"input_per_million": 0.5, "output_per_million": 4.0}}


def make_row(id_, route, latency, error=None, **metrics):
    base = {"input_tokens": 1000, "output_tokens": 100, "gemini_input_tokens": 0, "gemini_output_tokens": 0,
            "llm_calls": 3, "tool_call_count": 2, "subagent_calls": {}}
    base.update(metrics)
    return {"id": id_, "expected_route": route, "latency_s": latency, "metrics": base,
            "cost_usd": run_baseline.estimate_cost(base, PRICING), "error": error}


def test_estimate_cost_combines_coordinator_and_gemini_rates():
    m = {"input_tokens": 1_000_000, "output_tokens": 500_000, "gemini_input_tokens": 2_000_000, "gemini_output_tokens": 250_000}
    assert run_baseline.estimate_cost(m, PRICING) == pytest.approx(1.0 + 1.0 + 1.0 + 1.0)


def test_percentile_interpolates():
    assert run_baseline.percentile([], 0.5) == 0.0
    assert run_baseline.percentile([4.0], 0.95) == 4.0
    assert run_baseline.percentile([1, 2, 3, 4, 5], 0.5) == 3
    assert run_baseline.percentile([1, 2, 3, 4, 5], 0.95) == 4.8


def test_aggregate_excludes_errors_and_reports_means():
    rows = [make_row("a", ["database"], 10.0), make_row("b", ["database"], 20.0, input_tokens=3000),
            make_row("c", ["internet"], 99.0, error="RuntimeError: boom")]
    agg = run_baseline.aggregate(rows)
    assert agg["questions"] == 3 and agg["errors"] == 1
    assert agg["latency_p50_s"] == 15.0 and agg["latency_mean_s"] == 15.0
    assert agg["mean_input_tokens"] == 2000.0 and agg["mean_tool_calls"] == 2.0
    assert agg["total_cost_usd"] == pytest.approx(rows[0]["cost_usd"] + rows[1]["cost_usd"], abs=1e-6)
    routes = run_baseline.by_route(rows)
    assert set(routes) == {"database", "internet"} and routes["internet"]["errors"] == 1


def test_markdown_table_lists_every_row_and_route():
    rows = [make_row("db-01", ["database"], 12.34, subagent_calls={"Database Query Agent": 1}),
            make_row("mix-01", ["database", "internet"], 40.0, error="TimeoutError: slow")]
    table = run_baseline.markdown_table(rows, run_baseline.aggregate(rows), run_baseline.by_route(rows))
    assert "| db-01 | database | 12.3 |" in table and "Database Query Agent×1" in table
    assert "| mix-01 | database+internet |" in table and "| error |" in table
    assert "| all | 2 | 1 |" in table


def test_load_questions_filters_and_schema(tmp_path):
    rows = run_baseline.load_questions(run_baseline.DEFAULT_QUESTIONS)
    assert len(rows) == 20 and len({r["id"] for r in rows}) == 20
    for r in rows:
        assert {"id", "question", "mode", "expected_route", "tags"} <= set(r)
        assert set(r["expected_route"]) <= {"database", "internet", "ragflow"}
    assert [r["id"] for r in run_baseline.load_questions(run_baseline.DEFAULT_QUESTIONS, ids=["kb-03", "db-01"])] == ["db-01", "kb-03"]
    assert len(run_baseline.load_questions(run_baseline.DEFAULT_QUESTIONS, limit=2)) == 2
    pricing = run_baseline.load_pricing(run_baseline.DEFAULT_PRICING)
    assert {"coordinator", "gemini"} <= set(pricing)
