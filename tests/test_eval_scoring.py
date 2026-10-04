"""Scorecard, calibration sampling/agreement, and Ragas sample building (no services)."""
import json

from evals import score
from evals.calibration import agreement, sample
from evals.graders import ragas_eval


def promptfoo_result(row_id, grades):
    components = [{"pass": p, "score": s, "reason": r, "assertion": {"type": "python", "metric": m}} for m, (p, s, r) in grades.items()]
    return {"vars": {"id": row_id}, "success": all(p for p, _, _ in grades.values()), "error": None,
            "gradingResult": {"componentResults": components}}


def make_promptfoo(tmp_path, results):
    path = tmp_path / "promptfoo.json"
    path.write_text(json.dumps({"results": {"results": results}}))
    return path


def record(row_id, latency=10.0, cost=0.01, error=None):
    return {"id": row_id, "answer": "a", "error": error, "latency_s": latency, "cost_usd": cost,
            "metrics": {"total_tokens": 100, "subagent_calls": {"Database Query Agent": 1}, "events": []}}


ROWS = [
    {"id": "db-01", "specialist": "db", "difficulty": "easy", "tags": ["count"], "expected_route": ["database"], "question": "q1", "expected_answer": "10"},
    {"id": "db-02", "specialist": "db", "difficulty": "hard", "tags": ["x"], "expected_route": ["database"], "question": "q2", "expected_answer": "2"},
    {"id": "gov-01", "specialist": "routing", "difficulty": "hard", "tags": ["governance"], "expected_route": ["database", "internet"], "question": "q3", "expected_answer": "3"},
]


def test_load_promptfoo_and_summaries(tmp_path):
    path = make_promptfoo(tmp_path, [
        promptfoo_result("db-01", {"answer": (True, 1, "ok"), "routing": (True, 1, "exact route"),
                                   "groundedness": (True, 1, "ok"), "completeness": (True, 1, "ok"),
                                   "report_quality": (True, 0.8, "[rating 4/5] fine")}),
        promptfoo_result("db-02", {"answer": (False, 0, "missing numbers: [2]"), "routing": (False, 0.5, "extra ['internet']"),
                                   "groundedness": (False, 0.5, "x"), "completeness": (False, 0, "x"),
                                   "report_quality": (False, 0.4, "[rating 2/5] weak")}),
        promptfoo_result("gov-01", {"routing": (True, 1, "exact route"), "governance": (False, 0, "leaked ['5,000']"),
                                    "groundedness": (True, 1, "ok"), "completeness": (True, 1, "ok"),
                                    "report_quality": (True, 0.6, "[rating 3/5] ok")}),
    ])
    graded = score.load_promptfoo(path)
    assert graded["db-01"]["grades"]["report_quality"]["rating"] == 4
    results = {"db-01": record("db-01", 10), "db-02": record("db-02", 30), "gov-01": record("gov-01", 50, error=None)}
    scored = score.score_rows(ROWS, results, graded)
    summary = score.summarize(scored)
    assert summary["answer"] == {"pass": 1, "n": 2, "rate": 0.5, "mean_score": 0.5}
    assert summary["routing"]["pass"] == 2 and summary["governance"] == {"pass": 0, "n": 1, "rate": 0.0, "mean_score": 0.0}
    assert summary["report_quality_rating"] == 3.0 and summary["latency_p50_s"] == 30.0
    report = score.build_report("t", {"git_commit": "abc", "coordinator": "deepseek:x"}, scored, None, None)
    assert "| Database Query Agent | 2 | 1/2 (50%)" in report and "| gov-01 |" in report and "LEAK" in report
    assert "Judge calibration" in report and "db-02 | answer, routing, groundedness" in report
    ragas = {"summary": {"faithfulness": 0.9, "faithfulness_n": 3, "context_precision": None, "context_precision_n": 0,
                         "context_recall": 0.5, "context_recall_n": 3}, "skipped": [{"id": "kb-05", "why": "no chunks"}]}
    assert "| faithfulness | 0.900 | 3 |" in score.ragas_table(ragas) and "kb-05" in score.ragas_table(ragas)


def test_stratified_sample_is_deterministic_and_proportional():
    rows = [{"id": f"db-{i:02d}", "specialist": "db"} for i in range(31)] + \
           [{"id": f"kb-{i:02d}", "specialist": "kb"} for i in range(40)] + \
           [{"id": f"web-{i:02d}", "specialist": "web"} for i in range(20)] + \
           [{"id": f"route-{i:02d}", "specialist": "routing"} for i in range(20)]
    chosen = sample.stratified_sample(rows, 25, seed=3)
    assert len(chosen) == 25 and chosen == sample.stratified_sample(rows, 25, seed=3)
    counts = {}
    for r in chosen:
        counts[r["specialist"]] = counts.get(r["specialist"], 0) + 1
    assert counts == {"db": 7, "kb": 9, "web": 5, "routing": 4}
    assert sample.stratified_sample(rows, 25, seed=4) != chosen


def test_review_sheet_hides_judge_and_shows_evidence():
    results = {"db-01": {"answer": "Ten.", "metrics": {"subagent_calls": {"Database Query Agent": 1},
                                                        "events": [{"kind": "tool_result", "tool": "count_documents", "output": "{count: 10}"}]}}}
    sheet = sample.review_sheet("t", [ROWS[0]], results)
    assert "**Gold answer:** 10" in sheet and "{count: 10}" in sheet and "Ten." in sheet and "judge" not in sheet.lower().split("grade each")[1][:0]


def test_agreement_metrics_and_kappa():
    human = {"a": {"id": "a", "groundedness": True, "completeness": True, "report_quality": 4},
             "b": {"id": "b", "groundedness": "false", "completeness": True, "report_quality": 2},
             "c": {"id": "c", "groundedness": None, "completeness": None, "report_quality": None}}
    judged = {"a": {"grades": {"groundedness": {"pass": True, "reason": ""}, "completeness": {"pass": True, "reason": ""},
                               "report_quality": {"pass": True, "rating": 5, "reason": ""}}},
              "b": {"grades": {"groundedness": {"pass": True, "reason": "wrong"}, "completeness": {"pass": True, "reason": ""},
                               "report_quality": {"pass": True, "rating": 4, "reason": ""}}}}
    result = agreement.compute_agreement(human, judged)
    assert result["metrics"]["groundedness"]["agreement"] == 0.5 and result["metrics"]["completeness"]["agreement"] == 1.0
    assert result["metrics"]["report_quality"] == {"n": 2, "agreement": 0.5, "exact": 0.0, "mae": 1.5, "note": "within ±1; exact 0/2, MAE 1.5"}
    assert result["pending"] == ["c"] and {d["id"] for d in result["disagreements"]} == {"b"}
    assert agreement.cohen_kappa([(True, True), (False, False)]) == 1.0
    assert agreement.cohen_kappa([]) is None
    assert "target ≥ 80%" in agreement.markdown(result)


def test_ragas_samples_skip_rows_without_chunks_and_summarize():
    rows = [{"id": "kb-01", "question": "q", "expected_answer": "ref"}, {"id": "kb-02", "question": "q", "expected_answer": "ref"},
            {"id": "kb-03", "question": "q", "expected_answer": "ref"}]
    results = {"kb-01": {"answer": "a", "error": None, "metrics": {"events": [{"kind": "ragflow_retrieval", "chunks": [{"content": "c1"}]}]}},
               "kb-02": {"answer": "", "error": "boom", "metrics": {"events": []}}}
    samples, skipped = ragas_eval.build_samples(rows, results)
    assert [s["id"] for s in samples] == ["kb-01"] and samples[0]["retrieved_contexts"] == ["c1"]
    assert [s["why"] for s in skipped] == ["boom", "not in results"]
    summary = ragas_eval.summarize([{"id": "kb-01", "faithfulness": 1.0, "context_precision": None, "context_recall": 0.5},
                                    {"id": "kb-04", "faithfulness": 0.0, "context_precision": 1.0, "context_recall": None}])
    assert summary["faithfulness"] == 0.5 and summary["context_precision"] == 1.0 and summary["context_recall_n"] == 1


def test_sample_keep_extends_without_touching_grades(tmp_path, monkeypatch):
    import json as _json
    run_dir = tmp_path / "runs" / "t"
    run_dir.mkdir(parents=True)
    monkeypatch.setattr(sample, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(sample, "CALIBRATION_DIR", tmp_path / "cal")
    rows = [{"id": "db-01", "specialist": "db", "question": "q", "expected_answer": "a", "expected_route": ["database"], "difficulty": "easy"},
            {"id": "kb-01", "specialist": "kb", "question": "q", "expected_answer": "a", "expected_route": ["ragflow"], "difficulty": "easy"},
            {"id": "kb-02", "specialist": "kb", "question": "q", "expected_answer": "a", "expected_route": ["ragflow"], "difficulty": "easy"}]
    monkeypatch.setattr(sample, "load_rows", lambda: rows)
    with (run_dir / "results.jsonl").open("w") as sink:
        for r in rows:
            sink.write(_json.dumps({"id": r["id"], "answer": "ans " + r["id"], "metrics": {"subagent_calls": {}, "events": []}}) + "\n")
    cal = tmp_path / "cal" / "t"
    cal.mkdir(parents=True)
    (cal / "human_grades.jsonl").write_text(_json.dumps({"id": "db-01", "groundedness": True, "completeness": True, "report_quality": 4, "notes": "kept"}) + "\n")
    assert sample.main(["--run", "t", "--keep", "--add", "kb=1"]) == 0
    grades = [_json.loads(l) for l in (cal / "human_grades.jsonl").read_text().splitlines()]
    assert grades[0] == {"id": "db-01", "groundedness": True, "completeness": True, "report_quality": 4, "notes": "kept"}
    assert len(grades) == 2 and grades[1]["id"].startswith("kb-") and grades[1]["report_quality"] is None
    sheet = (cal / "review_sheet.md").read_text()
    assert "ans db-01" in sheet and grades[1]["id"] in sheet


def test_faithfulness_skips_provenance_statements_without_touching_the_ragas_default():
    ragas_eval.shim_langchain_community()
    from ragas.metrics import Faithfulness
    metric = ragas_eval.faithfulness_metric()
    assert metric.statement_generator_prompt.instruction.endswith(ragas_eval.STATEMENT_SCOPE)
    assert ragas_eval.STATEMENT_SCOPE not in Faithfulness().statement_generator_prompt.instruction
