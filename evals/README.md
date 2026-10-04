# Evaluation harness

Everything under `evals/` measures the coordinator and its three specialists against the golden
set in `evals/golden/v1.jsonl` (111 rows; dataset card in `evals/golden/README.md`). Runs are
recorded once and graded separately, so grading can be re-run (new rubric, new judge) without
paying for the agent again.

```
evals/
  run_baseline.py        Day 1 latency/token/cost baseline over 20 questions (evals/baseline.json)
  run_golden.py          run golden rows through the coordinator -> evals/runs/<run>/results.jsonl
  graders/code.py        deterministic graders: numeric / contains, routing, governance, citations
  graders/judge.py       LLM-as-judge client (Azure claude-sonnet-5-5 or GPT) + rubrics from prompt/prompts.yaml (evals.judge)
  graders/ragas_eval.py  Ragas faithfulness / context precision / context recall on the kb rows
  promptfoo/             promptfoo harness: replay/live provider, generated tests, python asserts (code graders + LLM judge)
  score.py               scorecard: evals/reports/<run>.md + evals/runs/<run>/scores.json
  calibration/           judge calibration: sample 25 outputs for hand grading, compute agreement
  reports/               committed scorecards (v1_baseline.md is the Day 3 "before")
  runs/                  per-run artifacts; only named baseline runs are committed
```

## Workflow

```bash
# 1. Run the agent over the golden rows (sequential; ~45 s per row; needs all live services in .env)
uv run python evals/run_golden.py --name v1_baseline                # all 111 rows
uv run python evals/run_golden.py --name v1_baseline --specialist kb --resume   # continue / add rows
uv run python evals/run_golden.py --name v1_baseline --ids gov-01 --resume      # re-run one row (last line wins)

# 2. Grade with promptfoo (code graders + LLM judge; judge calls are not cached, so a re-run re-judges every row)
evals/promptfoo/eval.sh v1_baseline                                 # -> evals/runs/v1_baseline/promptfoo.json; records the judge in run.json
evals/promptfoo/eval.sh v1_baseline --filter-pattern '^kb-'         # subset
promptfoo view                                                      # browse results in the browser

# 3. Ragas on the knowledge-base rows (uses the chunks RAGFlow returned during the run)
uv run python evals/graders/ragas_eval.py --run v1_baseline         # -> evals/runs/v1_baseline/ragas.json

# 4. Scorecard
uv run python evals/score.py --run v1_baseline                      # -> evals/reports/v1_baseline.md

# 5. Judge calibration (once per rubric change)
uv run python evals/calibration/sample.py --run v1_baseline         # -> evals/calibration/v1_baseline/{review_sheet.md,human_grades.jsonl}
#    ... fill in human_grades.jsonl by hand ...
uv run python evals/calibration/agreement.py --run v1_baseline      # -> evals/runs/v1_baseline/agreement.json, then re-run score.py
```

`promptfoo` is installed globally with npm (`npm install -g promptfoo`); `eval.sh` points it at
the project virtualenv (`PROMPTFOO_PYTHON`) and loads `.env` for the judge credentials.
`EVAL_MODE=live evals/promptfoo/eval.sh <run>` makes the provider run the coordinator per test
instead of replaying, which is what the Day 5 CI smoke subset uses.

## Metrics

| metric | grader | applies to | pass condition |
|---|---|---|---|
| answer | code (`numeric`, `contains_all`, `contains_any` from the row's `grader`) | db, kb, web rows | every target number/string present; numbers are formatting-insensitive |
| routing | code, set equality on the specialists delegated to (`RunMetrics.subagent_calls` and `delegation` events) | every row | actual == `expected_route`; extra fan-out and missed specialists both fail (Jaccard partial score) |
| governance | code over the run's outbound web surfaces: `internet_search.query`, Gemini's executed `search_queries`, and the delegation text sent to the Network Search Agent | `gov-*` rows | no `must_not_leak` token appears (case/format-insensitive) |
| citations | code, network: every URL in the answer is fetched (redirects followed) | rows with `internet` in the route | HTTP 200 and the page mentions ≥1 key term of the row (grader targets) |
| groundedness | LLM judge (`evals.judge.groundedness`) over the evidence recorded in the run: MongoDB tool results, Gemini grounded summaries + sources, RAGFlow chunks | every row | no material claim unsupported; score = fraction of claims supported |
| completeness | LLM judge (`evals.judge.completeness`, python assertion) against `expected_answer` | every row | all gold facts present and not contradicted |
| report_quality | LLM judge (`evals.judge.report_quality`, python assertion), 1–5 Likert | every row | rating ≥ 3; the scorecard reports the mean rating |
| faithfulness, context_precision, context_recall | Ragas, judged by the same Azure model | kb rows with recorded chunks | reported as means, not pass/fail |

The judge is `claude-sonnet-5-5` on Azure (`AZURE_ENDPOINT`, `AZURE_API_KEY`, `AZURE_DEPLOYMENT_NAME` in
`.env`; `AZURE_REASONING_EFFORT` = `low` | `medium` | `high`, default `medium`, applies to every judge
and Ragas call). `graders/judge.py` sends `claude-*` deployments through the Anthropic SDK's
`AnthropicFoundry` client (Messages API, `output_config` effort and JSON-schema format; a refusal is an
error, not a fallback to another model) and any other deployment through the OpenAI SDK on `/openai/v1`
(`max_completion_tokens`, `reasoning_effort`, strict JSON schema; GPT deployments reject `temperature`
and `max_tokens`). Ragas needs an OpenAI-API model and uses `AZURE_RAGAS_DEPLOYMENT_NAME` (default
`gpt-6.1-sol`) when the judge is Claude. Calibration on 2026-10-04 (25 rows, `evals/runs/v1_baseline/agreement.json`):
overall agreement 0.92, groundedness 0.76 (kappa 0.52; 0.80 in a separate grading pass), completeness 1.00,
report quality 1.00 within ±1. All three judge metrics are
Python assertions in `promptfoo/asserts.py` that call `graders/judge.py`, not `llm-rubric` with a
`file://` grading provider: promptfoo 0.123 gives such a provider a 4-worker Python pool per assertion
and keeps every pool until the eval ends, which exhausted memory on a full 111-row run.
Rubrics live in `prompt/prompts.yaml` under `evals.judge` and are versioned with the agent prompts.

Evidence for the judge is captured by `agent/metrics.py` (`RunMetrics.events`) only when an
evaluation installs metrics; the API path records nothing extra. Gemini's grounded summary is
model-generated text: groundedness for web rows therefore measures agreement with what the search
tool returned, and the citation grader is the check against the actual pages.

## Known limitations

- Citation checks depend on the cited sites answering a plain HTTP GET; a 403 from a bot-blocking
  site counts as invalid. Statuses are kept per URL in the promptfoo result for inspection.
- The judge runs at the model's default temperature; repeated gradings can differ on borderline
  rows, which is what the calibration agreement number bounds.
- `ragas` 0.4.3 still imports a Vertex AI class that `langchain-community` 0.4 removed;
  `graders/ragas_eval.py` installs a small import shim before importing ragas.
