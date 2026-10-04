"""Code graders, judge plumbing, and the promptfoo adapters (no network, no judge model)."""
import json

import pytest

from evals import score
from evals.graders import code, judge
from evals.promptfoo import asserts as pf_asserts, golden_tests as pf_tests, provider as pf_provider


# --------------------------------------------------------------------------- #
# Answer graders
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("text,expected", [
    ("25,000 units", [25000.0]),
    ("25 000 units across 3 batches", [25000.0, 3.0]),
    ("total 2,153,200 (2.15 million)", [2153200.0, 2.15]),
    ("20mg*7 tablets", [20.0, 7.0]),
    ("no numbers", []),
])
def test_numbers_in_normalizes_separators(text, expected):
    assert code.numbers_in(text) == expected


def test_grade_numeric_accepts_any_formatting_and_reports_missing():
    assert code.grade_numeric("We hold **25,000** units.", [25000])["pass"]
    assert code.grade_numeric("336000 units", [336000])["pass"]
    result = code.grade_numeric("10 drugs", [10, 4])
    assert not result["pass"] and result["score"] == 0.5 and result["details"]["missing"] == [4]


def test_grade_numeric_does_not_match_digits_inside_other_numbers():
    assert not code.grade_numeric("There are 100 drugs", [10])["pass"]


def test_contains_all_and_any_are_case_insensitive_and_handle_numbers():
    answer = "Lianhua Qingwen Capsules lead with 160,000 units."
    assert code.grade_contains_all(answer, ["lianhua qingwen capsules", 160000])["pass"]
    assert not code.grade_contains_all(answer, ["Lianhua", "Tianjin"])["pass"]
    assert code.grade_contains_any("It is a third-generation cephalosporin", ["3rd generation", "third-generation"])["pass"]
    assert not code.grade_contains_any("unknown", ["clay", "silicate"])["pass"]


def test_contains_folds_unicode_dashes_and_spaces():
    assert code.grade_contains_all("developed by **Parke\u2011Davis** in 1996", ["Parke-Davis", "1996"])["pass"]
    assert code.grade_contains_any("third\u2013generation agent", ["third-generation"])["pass"]
    assert code.fold("A\u00a0B\u2014C") == "a b-c"


def test_grade_answer_dispatches_and_rejects_unknown_method():
    assert code.grade_answer("numeric", "4", [4])["pass"]
    with pytest.raises(ValueError):
        code.grade_answer("routing", "x", ["database"])


# --------------------------------------------------------------------------- #
# Trace graders
# --------------------------------------------------------------------------- #
def delegation(subagent, description="do it"):
    return {"kind": "delegation", "subagent": subagent, "description": description}


def test_routing_exact_extra_and_missing():
    events = [delegation("Database Query Agent")]
    assert code.grade_routing(["database"], events)["pass"]
    extra = code.grade_routing(["database"], events + [delegation("Network Search Agent")])
    assert not extra["pass"] and extra["details"]["extra"] == ["internet"] and extra["score"] == 0.5
    missing = code.grade_routing(["database", "internet"], events)
    assert not missing["pass"] and missing["details"]["missing"] == ["internet"]
    # subagent_calls from RunMetrics counts even without delegation events
    assert code.grade_routing(["ragflow"], [], {"RAGFlow Agent": 2})["pass"]


def test_governance_detects_tokens_on_every_outbound_surface():
    tokens = ["Heilongjiang Provincial Hospital", "5,000"]
    clean = [delegation("Database Query Agent", "biggest oseltamivir customer"),
             delegation("Network Search Agent", "oseltamivir treatment course guidance"),
             {"kind": "internet_search", "query": "oseltamivir treatment course", "search_queries": ["oseltamivir dosing"], "sources": []}]
    assert code.grade_governance(tokens, clean)["pass"]
    leak_query = clean + [{"kind": "internet_search", "query": "Heilongjiang provincial hospital oseltamivir 5000 units", "search_queries": [], "sources": []}]
    result = code.grade_governance(tokens, leak_query)
    assert not result["pass"] and {l["token"] for l in result["details"]["leaks"]} == set(tokens)
    leak_delegation = clean + [delegation("Network Search Agent", "Find who Heilongjiang Provincial Hospital is")]
    assert code.grade_governance(tokens, leak_delegation)["details"]["leaks"][0]["surface"].startswith("delegation")
    leak_gemini = clean + [{"kind": "internet_search", "query": "x", "search_queries": ["5000 oseltamivir hospital"], "sources": []}]
    assert not code.grade_governance(tokens, leak_gemini)["pass"]


def test_citations_use_injected_fetch():
    answer = ("Fleming discovered penicillin in 1928 ([source](https://www.nobelprize.org/x)), "
              "see also https://example.com/dead. and https://example.com/offtopic")
    pages = {"https://www.nobelprize.org/x": (200, "https://www.nobelprize.org/x", "Alexander Fleming penicillin 1928"),
             "https://example.com/dead": (404, "https://example.com/dead", ""),
             "https://example.com/offtopic": (200, "https://example.com/offtopic", "nothing relevant")}
    result = code.check_citations(answer, ["fleming", "1928"], fetch=lambda url: pages[url])
    assert not result["pass"] and result["score"] == pytest.approx(1 / 3, abs=1e-3)
    checked = {c["url"]: c for c in result["details"]["checked"]}
    assert checked["https://www.nobelprize.org/x"]["valid"] and checked["https://www.nobelprize.org/x"]["matched_terms"] == ["fleming", "1928"]
    assert checked["https://example.com/dead"]["status"] == 404
    assert code.check_citations("no links here", ["x"], fetch=lambda url: (200, url, "x"))["reason"].startswith("no URL")
    assert code.cited_urls("(https://a.org/p).") == ["https://a.org/p"]


def test_key_terms_fall_back_to_expected_answer_words():
    assert code.key_terms(["Fleming", 1928]) == ["fleming", "1928"]
    assert code.key_terms([], "Alexander Fleming, 1928.") == ["alexander", "fleming", "1928"]


def test_evidence_text_and_retrieved_contexts():
    events = [{"kind": "tool_result", "tool": "count_documents", "output": '{"count": 10}'},
              {"kind": "internet_search", "query": "q", "answer": "grounded summary", "search_queries": [],
               "sources": [{"title": "T", "url": "https://t"}]},
              {"kind": "ragflow_retrieval", "assistant": "A", "question": "q", "answer": "kb answer",
               "chunks": [{"document": "d.txt", "content": "[[passage 1]] text"}, {"document": "d.txt", "content": "[[passage 1]] text"}]}]
    text = code.evidence_text(events)
    assert "count_documents" in text and "grounded summary" in text and "<https://t>" in text and "[[passage 1]] text" in text
    assert "knowledge base 'A' answered:\nkb answer" in text
    assert code.retrieved_contexts(events) == ["[[passage 1]] text"]
    assert code.evidence_text(events, limit=20).endswith("[evidence truncated]")


def test_evidence_text_describes_new_ragflow_events():
    chunk = {"document": "amoxil.pdf", "content": "500 mg", "similarity": 0.4, "chunk_id": "c1"}
    events = [{"kind": "ragflow_retrieval", "assistant": "", "knowledge_bases": ["handbook", "rag-mini-wiki"],
               "question": "q", "chunks": [chunk], "answer": ""},
              {"kind": "ragflow_retrieval", "assistant": "test", "knowledge_bases": ["handbook"],
               "question": "q", "chunks": [chunk, dict(chunk)], "answer": "Take 500 mg [ID:0]"}]
    text = code.evidence_text(events)
    assert "[1] knowledge base 'handbook, rag-mini-wiki' answered:\n(retrieval only; no answer generated)" in text
    assert "[2] knowledge base 'handbook' (assistant 'test') answered:\nTake 500 mg [ID:0]" in text
    assert text.count("(amoxil.pdf) 500 mg") == 3
    assert code.retrieved_contexts(events) == ["500 mg"]


# --------------------------------------------------------------------------- #
# Judge plumbing
# --------------------------------------------------------------------------- #
def test_judge_prompts_come_from_yaml_with_placeholders():
    prompts = judge.judge_prompts()
    assert {"system", "rubric_prompt", "groundedness", "completeness", "report_quality"} <= set(prompts)
    for name in ("question", "evidence", "answer"):
        assert "{{" + name + "}}" in prompts["groundedness"]
    assert "{{expected_answer}}" in prompts["completeness"]
    assert "{{output}}" in prompts["rubric_prompt"] and "{{rubric}}" in prompts["rubric_prompt"]


def test_render_leaves_unknown_placeholders_for_promptfoo():
    assert judge.render("a {{x}} b {{ y }} {{output}}", x=1, y="two") == "a 1 b two {{output}}"


def test_parse_json_tolerates_fences_and_prose():
    assert judge.parse_json('```json\n{"pass": true, "score": 1, "reason": "ok"}\n```')["pass"] is True
    assert judge.parse_json('Verdict: {"pass": false, "score": 0.2, "reason": "x"}')["score"] == 0.2
    with pytest.raises(ValueError):
        judge.parse_json("no json")


def test_normalize_grade_and_rating():
    grade = judge.normalize_grade({"pass": "yes", "score": "1.7", "reason": "[rating 4/5] fine"})
    assert grade == {"pass": True, "score": 1.0, "reason": "[rating 4/5] fine", "unsupported_claims": [], "usage": None}
    assert judge.normalize_grade({"pass": True, "score": None, "reason": ""})["score"] == 1.0
    assert judge.rating_from_reason("[rating 4/5] fine") == 4
    assert judge.rating_from_reason("no prefix", 0.6) == 3
    assert judge.rating_from_reason("no prefix") is None


def test_judge_functions_render_prompts_and_normalize(monkeypatch):
    calls = []

    def fake_complete(prompt, system=None, schema=None):
        calls.append((prompt, system))
        return {"pass": True, "score": 0.9, "reason": "[rating 5/5] great", "unsupported_claims": ["x"]}

    monkeypatch.setattr(judge, "complete_json", fake_complete)
    grounded = judge.judge_groundedness("Q?", "A.", "EVIDENCE")
    assert grounded["pass"] and grounded["unsupported_claims"] == ["x"]
    assert "<evidence>EVIDENCE</evidence>" in calls[0][0] and calls[0][1] == judge.judge_prompts()["system"]
    complete = judge.judge_completeness("Q?", "A.", "GOLD")
    assert complete["score"] == 0.9 and "Reference answer: GOLD" in calls[1][0] and "<answer>A.</answer>" in calls[1][0]
    quality = judge.judge_report_quality("Q?", "A.")
    assert quality["rating"] == 5


def test_complete_json_sends_reasoning_effort(monkeypatch):
    monkeypatch.setenv("AZURE_ENDPOINT", "https://example.openai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_API_KEY", "k")
    monkeypatch.setenv("AZURE_REASONING_EFFORT", "high")
    monkeypatch.setenv("AZURE_DEPLOYMENT_NAME", "gpt-6.1-sol")
    captured = {}

    class Completions:
        def create(self, **kwargs):
            captured.update(kwargs)
            from types import SimpleNamespace
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"pass": true, "score": 1, "reason": "ok"}'))],
                                   usage=SimpleNamespace(prompt_tokens=5, completion_tokens=3))

    from types import SimpleNamespace
    monkeypatch.setattr(judge, "_get_client", lambda: SimpleNamespace(chat=SimpleNamespace(completions=Completions())))
    data = judge.complete_json("prompt", system="sys", schema=judge.GRADE_SCHEMA)
    assert data["pass"] is True and data["_usage"] == {"prompt_tokens": 5, "completion_tokens": 3}
    assert captured["reasoning_effort"] == "high" and captured["max_completion_tokens"] == judge.MAX_COMPLETION_TOKENS
    assert "temperature" not in captured and "max_tokens" not in captured
    assert captured["response_format"]["json_schema"]["strict"] is True
    assert [m["role"] for m in captured["messages"]] == ["system", "user"]



def test_complete_json_retries_empty_content_and_sums_usage(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv("AZURE_ENDPOINT", "https://example.openai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_API_KEY", "k")
    monkeypatch.setenv("AZURE_DEPLOYMENT_NAME", "gpt-6.1-sol")
    contents = iter(["", '{"pass": true, "score": 1, "reason": "ok"}'])

    class Completions:
        def create(self, **kwargs):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=next(contents)))],
                                   usage=SimpleNamespace(prompt_tokens=5, completion_tokens=1500))

    monkeypatch.setattr(judge, "_get_client", lambda: SimpleNamespace(chat=SimpleNamespace(completions=Completions())))
    data = judge.complete_json("prompt", schema=judge.GRADE_SCHEMA)
    assert data["pass"] is True and data["_usage"] == {"prompt_tokens": 10, "completion_tokens": 3000}
    contents = iter([""] * judge.JUDGE_ATTEMPTS)
    with pytest.raises(ValueError):
        judge.complete_json("prompt")


def test_complete_json_on_claude_uses_messages_api_effort_and_schema(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv("AZURE_ENDPOINT", "https://res.openai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_API_KEY", "k")
    monkeypatch.setenv("AZURE_DEPLOYMENT_NAME", "claude-sonnet-5-5")
    monkeypatch.setenv("AZURE_REASONING_EFFORT", "low")
    captured, replies = [], iter([
        SimpleNamespace(stop_reason="max_tokens", content=[SimpleNamespace(type="thinking", thinking="")],
                        usage=SimpleNamespace(input_tokens=7, output_tokens=16000)),
        SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="thinking", thinking=""),
                                                          SimpleNamespace(type="text", text='{"pass": false, "score": 0, "reason": "no"}')],
                        usage=SimpleNamespace(input_tokens=7, output_tokens=40)),
    ])

    class Messages:
        def create(self, **kwargs):
            captured.append(kwargs)
            return next(replies)

    monkeypatch.setattr(judge, "_get_client", lambda: SimpleNamespace(messages=Messages()))
    data = judge.complete_json("prompt", system="sys", schema=judge.GRADE_SCHEMA)
    assert data["pass"] is False and data["_usage"] == {"prompt_tokens": 14, "completion_tokens": 16040}
    sent = captured[0]
    assert sent["model"] == "claude-sonnet-5-5" and sent["system"] == "sys" and sent["max_tokens"] == judge.CLAUDE_MAX_TOKENS
    assert sent["output_config"] == {"effort": "low", "format": {"type": "json_schema", "schema": judge.GRADE_SCHEMA}}
    assert sent["messages"] == [{"role": "user", "content": "prompt"}]
    assert not {"temperature", "reasoning_effort", "response_format", "thinking"} & set(sent)

    refusal = SimpleNamespace(stop_reason="refusal", stop_details=SimpleNamespace(category="bio"), content=[],
                              usage=SimpleNamespace(input_tokens=1, output_tokens=1))
    monkeypatch.setattr(judge, "_get_client", lambda: SimpleNamespace(messages=SimpleNamespace(create=lambda **k: refusal)))
    with pytest.raises(RuntimeError, match="refused"):
        judge.complete_json("prompt")

def test_judge_settings_require_azure_configuration(monkeypatch):
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)  # the developer's .env must not leak in
    monkeypatch.setenv("AZURE_ENDPOINT", "https://example.openai.azure.com/openai/v1/")
    monkeypatch.setenv("AZURE_API_KEY", "k")
    monkeypatch.delenv("AZURE_DEPLOYMENT_NAME", raising=False)
    monkeypatch.delenv("AZURE_REASONING_EFFORT", raising=False)
    settings = judge.judge_settings()
    assert settings == {"base_url": "https://example.openai.azure.com/openai/v1/", "api_key": "k", "model": "gpt-6.1-sol",
                        "reasoning_effort": "medium", "provider": "openai", "resource": "example"}
    monkeypatch.setenv("AZURE_DEPLOYMENT_NAME", "claude-sonnet-5-5")
    assert judge.judge_settings()["provider"] == "anthropic"
    monkeypatch.delenv("AZURE_DEPLOYMENT_NAME")
    monkeypatch.setenv("AZURE_REASONING_EFFORT", "High")
    assert judge.judge_settings()["reasoning_effort"] == "high"
    monkeypatch.setenv("AZURE_REASONING_EFFORT", "max")
    with pytest.raises(RuntimeError):
        judge.judge_settings()
    monkeypatch.setenv("AZURE_REASONING_EFFORT", "low")
    monkeypatch.delenv("AZURE_API_KEY")
    with pytest.raises(RuntimeError):
        judge.judge_settings()


def test_record_judge_writes_the_deployment_into_run_json(tmp_path, monkeypatch):
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
    monkeypatch.setenv("AZURE_ENDPOINT", "https://example.openai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_API_KEY", "k")
    monkeypatch.setenv("AZURE_DEPLOYMENT_NAME", "claude-sonnet-5-5")
    monkeypatch.delenv("AZURE_REASONING_EFFORT", raising=False)
    (tmp_path / "run.json").write_text(json.dumps({"name": "t", "coordinator": "deepseek:x"}), encoding="utf-8")
    assert judge.record_judge(tmp_path) == "claude-sonnet-5-5"
    meta = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert meta["coordinator"] == "deepseek:x" and meta["judge"] == "claude-sonnet-5-5" and meta["graded_at"]
    assert "claude-sonnet-5-5" in score.build_report("t", meta, [], None, None)


# --------------------------------------------------------------------------- #
# promptfoo adapters
# --------------------------------------------------------------------------- #
GOLDEN_ROWS = pf_tests.load_rows()


def test_generate_tests_covers_every_golden_row_with_the_right_assertions():
    cases = pf_tests.generate_tests()
    assert len(cases) == len(GOLDEN_ROWS)
    by_id = {c["vars"]["id"]: c for c in cases}
    for row in GOLDEN_ROWS:
        case = by_id[row["id"]]
        metrics = [a["metric"] for a in case["assert"]]
        assert metrics[-2:] == ["completeness", "report_quality"]
        assert "routing" in metrics and "groundedness" in metrics
        assert ("answer" in metrics) == (row["grader"]["method"] != "routing")
        assert ("governance" in metrics) == bool(row.get("governance"))
        assert ("citations" in metrics) == ("internet" in row["expected_route"])
        assert json.loads(case["vars"]["expected_route"]) == row["expected_route"]
        assert case["vars"]["expected_answer"] == row["expected_answer"]
    # Judge metrics must stay python assertions: a file:// llm-rubric provider leaks a worker pool per assertion.
    assert all(a["type"] == "python" and a["value"] == f"file://asserts.py:{a['metric']}" for c in cases for a in c["assert"])


def make_record(row_id="db-01", answer="There are 10 drugs.", events=None, error=None):
    return {"id": row_id, "answer": answer, "error": error, "latency_s": 1.5, "cost_usd": 0.01, "session_id": "s",
            "metrics": {"input_tokens": 10, "output_tokens": 2, "total_tokens": 12, "subagent_calls": {"Database Query Agent": 1},
                        "tool_calls": {"task": 1}, "events": events or [delegation("Database Query Agent")]}}


def test_provider_replays_recorded_results(tmp_path, monkeypatch):
    path = tmp_path / "results.jsonl"
    path.write_text(json.dumps(make_record()) + "\n" + json.dumps(make_record("web-01", answer="", error="Boom")) + "\n")
    monkeypatch.delenv("EVAL_MODE", raising=False)
    options = {"config": {"results": str(path)}}
    response = pf_provider.call_api("q", options, {"vars": {"id": "db-01"}})
    assert response["output"] == "There are 10 drugs." and response["metadata"]["subagent_calls"] == {"Database Query Agent": 1}
    assert response["tokenUsage"]["total"] == 12
    failed = pf_provider.call_api("q", options, {"vars": {"id": "web-01"}})
    assert failed["output"].startswith("[agent error]") and failed["metadata"]["error"] == "Boom"
    assert "no recorded result" in pf_provider.call_api("q", options, {"vars": {"id": "kb-99"}})["error"]
    assert "id" in pf_provider.call_api("q", options, {"vars": {}})["error"]


def test_provider_live_mode_runs_the_row_and_appends(tmp_path, monkeypatch):
    path = tmp_path / "results.jsonl"
    rows = []

    async def fake_run_row(row, pricing, name):
        rows.append(row)
        return make_record(row["id"], answer=f"live answer for {row['question']}")

    import evals.run_golden as run_golden
    monkeypatch.setattr(run_golden, "run_row", fake_run_row)
    monkeypatch.setenv("EVAL_MODE", "live")
    response = pf_provider.call_api("q", {"config": {"results": str(path)}},
                                    {"vars": {"id": "db-01", "question": "How many?", "expected_route": '["database"]'}})
    assert response["output"] == "live answer for How many?"
    assert json.loads(path.read_text().splitlines()[0])["id"] == "db-01"
    assert rows[0]["expected_route"] == ["database"]  # list vars arrive JSON-encoded and are decoded for the record


def context_for(row_id, record, **vars_):
    base = {"id": row_id, "question": "q", "expected_answer": "10 drugs.", "grader_method": "numeric",
            "grader_targets": "[10]", "expected_route": '["database"]', "must_not_leak": "[]"}
    base.update(vars_)
    return {"vars": base, "providerResponse": pf_provider.response_from_record(record)}


def test_python_assertions_grade_from_vars_and_metadata(monkeypatch):
    record = make_record()
    ctx = context_for("db-01", record)
    assert pf_asserts.answer(record["answer"], ctx)["pass"]
    assert pf_asserts.routing(record["answer"], ctx)["namedScores"]["routing_exact"] == 1.0
    fanout = make_record(events=[delegation("Database Query Agent"), delegation("Network Search Agent", "look up 10 drugs")])
    ctx_fan = context_for("gov-01", fanout, must_not_leak='["10 drugs"]')
    assert pf_asserts.routing("", ctx_fan)["namedScores"]["routing_extra"] == 1.0
    assert not pf_asserts.governance("", ctx_fan)["pass"]
    errored = context_for("db-02", make_record(answer="", error="Timeout"))
    assert pf_asserts.answer("", errored)["reason"].startswith("agent error")
    monkeypatch.setattr(code, "fetch_page", lambda url: (200, url, "ten drugs 10"))
    cited = pf_asserts.citations("See https://x.org/a", context_for("web-01", record, grader_targets='["10"]'))
    assert cited["pass"] and cited["namedScores"]["citation_count"] == 1.0
    monkeypatch.setattr(judge, "judge_groundedness", lambda q, a, e: {"pass": False, "score": 0.5, "reason": "half", "unsupported_claims": ["c1"]})
    grounded = pf_asserts.groundedness(record["answer"], ctx)
    assert not grounded["pass"] and "Unsupported: c1" in grounded["reason"] and grounded["namedScores"]["unsupported_claims"] == 1.0
    assert pf_asserts.groundedness("", errored)["reason"].startswith("agent error")
    seen = []
    monkeypatch.setattr(judge, "judge_completeness", lambda q, a, gold: seen.append(gold) or {"pass": True, "score": 1.0, "reason": "all"})
    assert pf_asserts.completeness(record["answer"], ctx)["pass"] and seen == ["10 drugs."]
    monkeypatch.setattr(judge, "judge_report_quality",
                        lambda q, a: {"pass": True, "score": 0.8, "reason": "[rating 4/5] fine", "rating": 4})
    quality = pf_asserts.report_quality(record["answer"], ctx)
    assert quality["reason"].startswith("[rating 4/5]") and quality["namedScores"]["report_quality_rating"] == 4.0
    assert pf_asserts.completeness("", errored)["reason"].startswith("agent error")
    assert pf_asserts.report_quality("", errored)["reason"].startswith("agent error")


def test_list_var_decoding_tolerates_plain_strings():
    assert pf_asserts._list({"vars": {"x": '["a", "b"]'}}, "x") == ["a", "b"]
    assert pf_asserts._list({"vars": {"x": "database"}}, "x") == ["database"]
    assert pf_asserts._list({"vars": {"x": ["k"]}}, "x") == ["k"]
    assert pf_asserts._list({"vars": {}}, "x") == []


def test_run_row_records_timeout_as_error(monkeypatch):
    import asyncio
    import evals.run_golden as run_golden

    async def slow(*args, **kwargs):
        await asyncio.sleep(0.2)
        return "late"

    import agent.main_agent as main_agent
    monkeypatch.setattr(main_agent, "run_deep_agent", slow)
    row = {"id": "db-01", "specialist": "db", "question": "q", "expected_route": ["database"]}
    pricing = {"coordinator": {"input_per_million": 1, "output_per_million": 1}, "gemini": {"input_per_million": 1, "output_per_million": 1}}
    record = asyncio.run(run_golden.run_row(row, pricing, "t", timeout_s=0.01))
    assert record["error"].startswith("TimeoutError") and record["answer"] == ""
    ok = asyncio.run(run_golden.run_row(row, pricing, "t", timeout_s=5))
    assert ok["answer"] == "late" and ok["error"] is None and ok["session_id"] == "golden-t-db-01"
