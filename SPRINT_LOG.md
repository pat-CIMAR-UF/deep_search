# Sprint log

One entry per day: what shipped, what was measured, what is pending. Numbers here feed the
Day 14 write-up and the resume bullets.

## Day 1 — 2026-09-17 — Baseline and public-readiness

**Shipped**
- Secrets audit. Five real credential values (1 Tavily key, 1 OpenAI-compatible key, 3 RAGFlow
  keys) were found in `docs/深度搜索项目文档.md`, introduced by one commit on `dev` and never
  removed; the English document had already been sanitized. Redacted at HEAD, all five keys
  revoked at their providers (none was still in use by the app), history rewritten with
  `git filter-repo --replace-text` (10 commits on `dev`, `main` predates the leak), force-pushed.
  A fresh clone shows 0 matches for the leaked patterns. The old commit is still fetchable as
  a dangling object on GitHub until garbage collection.
- GitHub secret scanning and push protection: not available on this private repo (GitHub
  Advanced Security required). **Re-run the enable call the moment the repo goes public.**
- `.env.example` covering all 13 environment variables.
- Public-readiness pass: README rewritten (badges, Mermaid architecture diagram, quickstart,
  configuration table, evaluation and development sections), MIT `LICENSE`, `pyproject.toml`
  metadata, `.github/workflows/tests.yml` (pytest on push/PR, green on first run), long-form
  documents and API contract moved to `docs/`, personal sprint plan git-ignored.
- Run metrics: `agent/metrics.py` (`RunMetrics` + LangChain callback handler counting model
  calls, tokens, tool calls, sub-agent delegations; opt-in via `api.context.set_run_metrics`)
  and Gemini grounding token capture in `tools/gemini_tool.py`.
- Baseline harness: `evals/baseline_questions.jsonl` (20 questions: 6 database, 6 knowledge
  base, 5 web, 3 mixed), `evals/pricing.yaml`, `evals/run_baseline.py` → `evals/baseline.json`.
- Coordinator provider switch: `LLM_PROVIDER=deepseek|qwen` in `agent/llm.py`; `.env` now uses
  DeepSeek `deepseek-flash` because the Cloudflare quick tunnel to the local Qwen server dropped
  twice during the day.
- Test suite: 235 → 247 tests, all mocked.

**Baseline (before any evaluation-driven change)** — run 20260917T175553Z, `evals/baseline.json`

Coordinator: DeepSeek `deepseek-flash` (switched today; the self-hosted Qwen tunnel was too
unreliable to measure). 20/20 questions completed with no harness error; total estimated cost
$0.92 for the run.

| route | n | errors | p50 s | p95 s | mean tokens | mean tool calls | mean cost $ |
|---|---:|---:|---:|---:|---:|---:|---:|
| database | 6 | 0 | 21.2 | 30.5 | 43,522 | 12.7 | 0.0165 |
| ragflow | 6 | 0 | 125.2 | 166.0 | 134,630 | 24.8 | 0.0727 |
| internet | 5 | 0 | 42.5 | 72.9 | 52,826 | 13.0 | 0.0349 |
| mixed | 3 | 0 | 93.7 | 172.4 | 133,703 | 23.3 | 0.0702 |
| all | 20 | 0 | 42.2 | 172.5 | 86,708 | 18.0 | 0.0460 |

A first attempt (`evals/baseline_20260917_ragflow_down.json`, 16:29 UTC) ran while RAGFlow's
chat assistants still pointed at the dead Qwen endpoint: retrieval worked but every answer
stream carried `CONNECTION_ERROR`, so all six kb questions came back as honest "no content"
answers and the coordinator fanned out to the other specialists (ragflow p95 283 s, 173k
tokens). The assistants were re-pointed at `deepseek-flash` inside RAGFlow and the full set
re-run; the table above is the "before" for the sprint.

Observations that Days 2–5 should turn into graded metrics:
- **Routing over-fans-out.** 12/20 runs invoked exactly the expected specialists; 8/20 invoked
  extra ones (web + database agents on kb questions, RAGFlow + database on web questions). No
  run missed an expected specialist. Extra fan-out is the main driver of latency and cost:
  the three kb questions that stayed on RAGFlow alone or nearly so (kb-01, mix-02) took 20–26 s;
  the ones that fanned out took 100–173 s. This is the routing-accuracy baseline for Day 3.
- **Knowledge-base answers are grounded when RAGFlow is healthy**: kb-01 to kb-04 cite the label
  PDF with dosage, contraindication, and storage details. kb-05 (IKEA crib manual) still fails,
  as expected: the manual is diagrams and its indexed text is part labels only. kb-06 (Midea AC)
  was answered from public web sources, not the knowledge base — a routing/provenance miss to
  grade (the answer should come from the installation guide).
- **Database route is tight**: 6/6 correct on spot check, ~21 s, ~13 tool calls, ~$0.017.
- **Mixed database+web questions are the slowest** (mix-01 172 s, 210k input tokens, 31 tool
  calls) because both specialists run in sequence and the coordinator re-verifies.
- Every one of the 20 runs includes an `ls` call from the coordinator's built-in filesystem
  tools; pure overhead for research questions and a Day 5 context-engineering candidate.
- Log noise: the Gemini SDK warns "Direct use of automatic function calling (AFC) in
  Models.generate_content is not recommended" on every web search; harmless, silence on Day 5.

Cost assumptions (`evals/pricing.yaml`): DeepSeek `deepseek-flash` peak-hour cache-miss list
price for the coordinator; Gemini Flash-class list price for grounding tokens. Both are editable
and recorded in `baseline.json`.

**Azure and tooling**
- Azure CLI logged in; subscription "CROO Cloud Services" (Enabled). Budget alert deliberately
  skipped today; decide the sprint subscription before Day 7 and set a $50 monthly budget then.
- Foundry decision: **Path A** (pay-as-you-go subscription; Claude via Microsoft Foundry on Day 9).
- Tools: `az` 2.78.0 (Windows CLI through WSL), `docker` 29.8.0 (Docker Desktop; WSL
  integration currently off, enable before Day 6), `terraform` 1.16.3 (installed to
  `~/.local/bin`), `node` 22 via nvm, `mongodb-mcp-server` 3.0.1, `git-filter-repo`.

**Reading: Anthropic, *Writing effective tools for AI agents* — three changes queued for Day 5**
1. `internet_search`: add a `response_format` (`concise` | `detailed`) and describe the return
   fields explicitly — `answer` is model-generated, `sources` are the ground truth to cite.
   `max_results` is under-specified today.
2. RAGFlow tools: rename `chat_name` → `assistant_name`, state in the description that
   `get_assistant_list` must run first, and describe the return structure (answer plus document
   references) instead of "the answer".
3. Namespacing: tool names span three services without prefixes (`internet_search`,
   `find_documents`, `create_ask_delete`). Evaluate `web_`, `mongo_`, `kb_` prefixes against the
   Day 3 scorecard before renaming; the article notes naming effects vary by model.

**Pending / carry-over**
- RAGFlow still has the stale `qwen-remote` model provider registered (unused); remove it when
  convenient so nothing can fall back to it.
- Budget alert once the subscription is settled.
- Enable secret scanning + push protection when the repo goes public.
- Enable Docker Desktop WSL integration before Day 6.

## Day 2 — 2026-09-18 — Golden dataset

**Shipped** (kept in the working tree on 2026-09-18 at the user's request; committed 2026-09-24 in `5bcf2ab`)
- `evals/golden/v1.jsonl`: **111 rows** (target ≥100), assembled by `evals/golden/build.py` from
  computed database rows plus three hand-authored source files. Schema per row: `id, specialist,
  question, mode, expected_answer, expected_sources, expected_route, difficulty, tags, grader`;
  optional `expected_values`, `governance.must_not_leak`, `gold_passage_ids`, `notes`.
- Dataset card `evals/golden/README.md`: composition, grader methods, how the knowledge-base gold
  passages were derived, routing rationale, licences, known gaps.
- `evals/test_golden_schema.py`: 211 checks, including "v1.jsonl matches the build script", "every
  governance token exists in the seed data", and per-specialist coverage gates. `evals` added to
  pytest `testpaths`, so CI validates the set. Suite: 247 → 458 tests, all mocked.
- `evals/golden/ingest_rag_mini_wikipedia.py` (idempotent) and `evals/golden/push_langsmith.py`
  (idempotent on metadata id). Parquet cache `evals/golden/data/` is git-ignored.
- `CLAUDE.md` knowledge-base table gained the new RAGFlow dataset.

| specialist | prefix | rows | easy / med / hard | gold labels | grader |
|---|---|---:|---|---|---|
| Database Query Agent | `db-` | 31 | 8 / 17 / 6 | computed from `mongo/seed/*.json` by `build.py`; live Atlas counts matched (10 / 30 / 20) | `numeric` 15, `contains_all` 15, `contains_any` 1 (negative row: product that does not exist) |
| RAGFlow Agent | `kb-` | 40 | 32 / 7 / 1 | rag-mini-wikipedia test split, verbatim; `gold_passage_ids` derived (see below) | `contains_all` 35, `contains_any` 5 |
| Network Search Agent | `web-` | 20 | 12 / 8 / 0 | hand-authored time-stable facts with expected source domains | `contains_all` 14, `contains_any` 6 |
| Coordinator routing | `route-` / `gov-` | 20 | 11 / 4 / 5 | `expected_route`: 6 database-only, 4 knowledge-base-only, 4 internet-only, 6 mixed (5 of the 20 are governance rows) | `routing` (set equality on delegated sub-agents) |

Every row has a deterministic grader method; `llm_rubric` is defined in the card but not yet
assigned to any row. Day 3 adds the judge on top (groundedness, completeness, report quality).

**Governance rows.** `gov-01..05` mix private records with a public lookup. Each lists the concrete
private tokens (customer names, batch numbers, warehouse names, the 2,153,200 revenue total) that
must not appear in an `internet_search` query; a test asserts every token is traceable to the seed
data. `gov-05` is a direct user instruction to web-search an internal sales department: the gold
route is database-only and complying is a leak. Two routing traps: `route-10` (metformin) and
`route-13` (Lipitor) have catalogue rows but ask public questions.

**Knowledge-base corpus.** The plan assumed rag-mini-wikipedia ships gold passage ids; it does not
(the test split is question/answer only). Derivation: answer string contained in the passage plus
≥2 shared question terms → 195 of 918 questions with one confident candidate → 40 self-contained
questions across 27 topics picked by hand → every gold passage read to confirm it answers. One
indirect case kept as `hard` (`kb-40`: the passage says Singapore is second after Monaco). kb rows
run in forced `ragflow` mode: they measure retrieval and grounding, not routing.

Ingestion: the full 3,200-passage corpus (user's choice over a 300-passage subset) as 32 text
files of 100 passages, each passage one line prefixed `[[passage N]]`, naive chunking at 128
tokens, RAPTOR and GraphRAG **off** (the three existing datasets have both on, which would have
pushed every chunk through an LLM). 1,875 chunks, parsed in about 4 minutes. New assistant
`RAG Mini Wikipedia Assistant` is bound to the dataset and told to keep the markers when quoting;
a live `create_ask_delete` call returned the 1832 answer with `[[passage 289]]` and three file
references. Retrieval ceiling via the SDK `retrieve` call (top 10 chunks):

| metric | result |
|---|---:|
| gold passage in top 10 | 40 / 40 |
| gold passage in top 5 | 39 / 40 |

This is the Day 3 upper bound for the kb cells, not an end-to-end score.

LangSmith: dataset `deep-search-golden-v1`, 111 examples pushed (inputs: question, mode; outputs:
gold fields; metadata: id, specialist, route, difficulty, tags).

**Observations for Day 3**
- Likely low cells: the 6 `hard` DB rows (grouping by the `warehouse_location` prefix, H1/H2
  revenue split, sell-through ratio across three collections) and the 5 governance rows. The kb
  rows are easy-skewed because rag-mini-wikipedia is single-fact lookup.
- RAGFlow SDK quirks: `list_datasets(name=...)` raises "lacks permission" for a name that does not
  exist, so filter the full list; dataset creation accepted a partial `parser_config`.
- Web gold answers were written from author knowledge and not checked against the listed domains;
  Day 3's citation-validity grader is the systematic check. Review `sources/web.jsonl` first.
- All four RAGFlow assistants report `llm_id` `unsloth/Qwen3.8-27B-GGUF@qwen-remote@...`, which
  contradicts the Day 1 note that they were re-pointed at `deepseek-flash`. Answers worked today, so
  either the provider entry itself was re-pointed or the Day 1 note is wrong; check inside RAGFlow
  before the Day 3 run and fix whichever is stale.

**Reading:** Anthropic, *Define success criteria and build evaluations* — **not read yet**; queued
for the start of Day 3, before writing graders. Things to check against it: the code/human/LLM
grading split above, and the Likert rubric example for the 1–5 report-quality grader.

**Pending / carry-over**
- Review `sources/web.jsonl` and `sources/routing.jsonl`. The Day 2 work was committed on
  2026-09-24 (`5bcf2ab`), but no review of these two files is recorded; do it before the Day 3 run.
- Resolve the RAGFlow assistant model question above; remove the stale `qwen-remote` provider only
  if nothing depends on it.
- Day 1 carry-overs unchanged: Azure budget once the subscription is settled, secret scanning when
  the repo goes public, Docker Desktop WSL integration before Day 6.

## Day 3 — 2026-09-26 — Graders and the first scorecard

**Shipped** (branch `day3-graders`)
- Evidence capture: `RunMetrics.events` in `agent/metrics.py` records sub-agent delegations (with the
  text sent to the specialist), outbound `internet_search` queries with Gemini's executed search
  queries, sources and grounded summary, RAGFlow's retrieved chunks (from the streamed references),
  and MongoDB/file tool results. Only when an evaluation installs metrics; the API path is unchanged.
- `evals/run_golden.py`: records golden rows to `evals/runs/<run>/results.jsonl` (append-only,
  `--resume`, `--ids`, `--specialist`); `run.json` keeps commit, coordinator model and pricing.
- Code graders `evals/graders/code.py`: numeric/contains (formatting-insensitive numbers), routing
  (set equality on delegated specialists, Jaccard partial credit), governance (no private token on
  any outbound web surface: tool query, Gemini's executed queries, delegation text), citation
  validity (every cited URL fetched; HTTP 200 and ≥1 key term on the page; PDFs read with pypdf).
- LLM judge `evals/graders/judge.py`: **gpt-6-sol on Azure** (OpenAI-compatible `/openai/v1`
  endpoint; the model rejects `temperature` and `max_tokens`, so calls use `max_completion_tokens`
  and a strict JSON schema). Three rubrics in `prompt/prompts.yaml` (`evals.judge`): groundedness
  against recorded evidence, completeness against the gold answer, report quality 1–5 Likert.
- Harness: **promptfoo** (`evals/promptfoo/`): Python provider that replays a recorded run (or runs
  the agent live for CI), test cases generated from `v1.jsonl`, Python assertions for the code
  graders and groundedness, `llm-rubric` assertions for completeness and report quality routed to
  the Azure judge through a grading provider. **Ragas** faithfulness / context precision / context
  recall on the kb rows (`evals/graders/ragas_eval.py`; needs an import shim with ragas 0.4.3).
- `evals/score.py` → `evals/reports/<run>.md` (per sub-agent, difficulty, routing, governance,
  Ragas, calibration, failures, per row) and `scores.json` for the Day 5 diff.
- Calibration: `evals/calibration/sample.py` (stratified 25-row sample, review sheet without the
  judge's verdicts, `human_grades.jsonl` to fill) and `agreement.py` (agreement %, Cohen's kappa for
  the binary metrics, within-±1 for the 1–5 rating).
- Tests 458 → 490, all mocked (`tests/test_graders.py`, `tests/test_eval_scoring.py`, metrics events).

**Environment findings**
- All four RAGFlow assistants still point at `unsloth/Qwen3.8-27B-GGUF@qwen-remote`; the Qwen tunnel
  is down again, so retrieval works but every answer stream is `CONNECTION_ERROR`. The Day 1 note
  about re-pointing them at `deepseek-flash` does not match the service state. Re-pointing them is a
  shared-service change left to the user (RAGFlow UI → each assistant → Model). Until then the kb
  rows, the four `route-` kb rows and `route-15` cannot be measured.
- Azure judge endpoint verified: `AZURE_ENDPOINT` already contains `/openai/v1`; use it verbatim as the
  OpenAI base URL. ~6 s per judge call.
- promptfoo 0.123.1 flattens list vars into strings before Python assertions and offers no way to
  pass `temperature`-free requests to the stock OpenAI provider for this model; both worked around.
- ragas 0.4.3 imports `langchain_community.chat_models.vertexai`, removed in langchain-community 0.4.

**Interim scorecard** (`evals/reports/v1_baseline.md`, run `v1_baseline`, 71 of 111 rows recorded:
db + web + routing; kb rows blocked on RAGFlow). Graded so far: the 51 db + web rows; the full
grading pass was stopped by Claude Code for low system memory and needs re-running.

| sub-agent | n | answer (code) | routing exact | groundedness | completeness | report quality (1–5) | citations | p50 s | p95 s | mean cost $ |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| Database Query Agent | 31 | 30/31 (97%) | 27/31 (87%) | 14/31 (45%), mean 0.96 | 31/31 (100%) | 3.06 | – | 16.9 | 25.9 | 0.0149 |
| Network Search Agent | 20 | 17/18 (94%) | 13/18 (72%) | 4/18 (22%), mean 0.92 | 18/18 (100%) | 2.83 | 0/18 (0%), mean 0.11 | 51.7 | 70.5 | 0.0338 |
| Coordinator routing | 20 | – | not graded yet | – | – | – | – | 60.0 | 151.8 | 0.0435 |

What the numbers say (before calibration):
- **Citations are the lowest cell**: 10 of 18 web answers contain no URL at all, although the search
  specialist ran 5–10 Gemini searches per question and Gemini returned sources for most of them. The
  links die between the specialist and the coordinator's final answer. Day 5 candidate #1.
- **Groundedness fails on embellishment, not on the core facts** (mean score 0.92–0.96, pass rate
  22–45%): the coordinator adds unverified checks ("no refunds occurred", "no expired batches",
  amounts "in yen", a wrong "9.5× the mean"). Whether those are material is exactly what the human
  calibration decides; the rubric already treats process narration as neutral.
- **Routing over-fans-out**, as on Day 1: 9 of 49 graded auto-mode rows called an extra specialist
  (RAGFlow on db questions, database on web questions); none missed the expected one.
- **Report quality ≈ 3/5**: answers are correct but padded (breakdowns, caveats, method sections).
- Two code-grader failures were grader strictness, fixed today: `web-04` used a Unicode hyphen in
  "Parke‑Davis" (contains graders now fold dashes/spaces), and `db-31`'s negative phrasing ("no
  Vitamin C product", "0 matching") was added to the gold targets (v1.jsonl regenerated).
- One MongoDB MCP `tools/call` hung for 26 min on `route-04` (p95 of the routing group);
  `run_golden.py` now bounds each row at 600 s and the row was re-run (16 s).
- Judge cost: the 51-row grading pass took 29 min wall-clock, mostly citation fetches and ~6 s per
  judge call; promptfoo caches judge calls, so re-grading is cheap.

**Pending / carry-over**
- Re-run the full grading pass (`evals/promptfoo/eval.sh v1_baseline`) — 20 routing rows are recorded but
  ungraded — then `evals/score.py`.
- Fix the RAGFlow assistant model, then: `uv run python evals/run_golden.py --name v1_baseline --specialist kb --resume`,
  re-run `route-06..09`, `route-15` and any row whose events show `CONNECTION_ERROR`, Ragas, re-grade.
- Hand-grade the 25 calibration rows and record the agreement number.
- Reading (promptfoo getting started; anthropics/courses prompt_evaluations 6–9) not done today.
- Day 1/2 carry-overs unchanged (Azure budget, secret scanning, Docker WSL integration, stale
  `qwen-remote` provider in RAGFlow).

**Addendum (state of the Day 3 files as of 2026-10-02)**
- The kb rows were recorded later on 2026-09-26 after all: `results.jsonl` holds all 40, answered by
  `RAG Mini Wikipedia Assistant` with retrieved chunks and no `CONNECTION_ERROR`, so the assistant
  model was fixed the same day. On 2026-09-28, 17 rows were re-run (4 db, 4 web, 9 route; `route-12`
  still errored). Every one of the 111 ids is now recorded, but the grading pass (`promptfoo.json`,
  `scores.json`, 71 rows) and `evals/reports/v1_baseline.md` still date from 2026-09-26: the kb,
  governance, Ragas and calibration sections of the report are empty.
- Calibration: `human_grades.jsonl` has 23 of the 25 sample rows (2026-09-28), 8 still null.
  `agreement.py` run on 2026-10-02 over the 11 rows that both judge and human graded:
  groundedness 55% (kappa 0.0), completeness 100%, report quality 18% within ±1 (judge rates 3 where
  the human rates 5), overall **58% against the ≥80% target**. The judge is systematically stricter on
  embellishment and on report length; the rubric has not been tuned yet. Written to
  `evals/runs/v1_baseline/agreement.json`.
- Nothing from Day 3 is committed yet; `evals/` is untracked on branch `day3-graders`.

## Interlude — 2026-10-02 — RAGFlow re-platformed onto the shared remote server

Not a planned sprint day. The local RAGFlow on `localhost:9380` was down, and the team's RAGFlow now
runs on a remote host reached through an SSH tunnel, with a small `rag` CLI (`~/workspace/RAGFlow_Example`)
as the house standard. Deep Search's knowledge-base service was rewritten to that standard.

**Shipped** (branch `day3-graders`, uncommitted)
- `ragflow/service.py`: knowledge bases addressed by name (the SDK `name=` filters raise when nothing
  matches, so listings are paged and matched locally); a chat assistant is reused when its datasets equal
  exactly the requested set, else `<a>+<b>-assistant` is created with server defaults; `[ID:n]` markers
  map to the reference list (positions kept, out-of-range dropped, HTML tags and entities stripped from
  snippets); retrieval without the LLM; upload-and-parse with polling; 10 s connect / 120 s read timeouts;
  connection failures say "is the SSH tunnel running?". Each question runs in a session named after the
  question that is deleted in `finally` (the CLI keeps its sessions; agent and eval traffic must not).
- `ragflow/cli.py`: `uv run python -m ragflow.cli --list | --retrieve | "question" | --add FILE`, the same
  flags as the house CLI. `ragflow/rag_config.py`: `RAGFLOW_BASE_URL` (default `http://localhost:8080`,
  legacy `RAGFLOW_API_URL` still read), `RAGFLOW_API_KEY`, `RAGFLOW_DATASET`.
- Tools renamed and re-cut: `list_knowledge_bases`, `retrieve_chunks`, `ask_knowledge_base` replace
  `get_assistant_list` / `create_ask_delete` (this also closes Day 1 reading item 2: the descriptions now
  state the call order and the return structure). Sub-agent prompt updated in `prompt/prompts.yaml`; the
  two `ragflow/*_demo.py` scripts removed; `ragflow-sdk` pinned to 0.27.2; README, CLAUDE.md,
  `.env.example` and the golden README updated.
- `ragflow_retrieval` events now carry `knowledge_bases` and `chunk_id`, and retrieval-only calls record an
  event with an empty answer; `evals/graders/code.py` renders both. `ingest_rag_mini_wikipedia.py` reads
  document status through the service layer, copies the server's embedding model and reuses an assistant by
  the exact-dataset-set rule.
- Tests 490 → 543, all mocked (`tests/ragflow_fakes.py`, `tests/test_ragflow.py`, `tests/test_ragflow_tools.py`).

**Server findings (RAGFlow v1.0.0-rc1, verified live)**
- `POST /api/v1/chats/{id}/completions` is gone (404), so `ragflow-sdk` `Session.ask` is broken in 0.27.2
  and 1.0.0rc1. Answers go through `POST /api/v1/chat/completions` with `chat_id`, `session_id`,
  `messages`; the reply has `data.answer` and `data.reference.chunks` (similarity as a string). With
  `stream: true` the server sends deltas, then one event with the full answer plus references.
- Documents report `ingestion_status` and `progress`; `run` is null and the SDK drops `ingestion_status`.
- Assistants linked to two datasets return every reference chunk twice (deduped by chunk id).
- LLM-provider failures arrive as a code-0 completion whose answer starts with `**ERROR**`; treated as a failure.
- Server state: `handbook` (the four PDFs from the former local datasets, 103 chunks) and `rag-mini-wiki`
  (one text file, 469 chunks, **no `[[passage N]]` markers**), both `text-embedding-3-large@Azure-AI@...`;
  assistants `test`, `rag-mini-wiki-assistant`, `handbook+rag-mini-wiki-assistant`. Another Claude Code
  session (`RAGFlow_Example`) shares the server and finds assistants by the same rule; it will warn before
  rebuilding `rag-mini-wiki`.

**Verification**
- Live: `--list`, `--retrieve`, `ask_knowledge_base` (cited AMOXIL storage answer, session count unchanged),
  and a real coordinator run in Knowledge-base mode that called `list_knowledge_bases`, `retrieve_chunks`
  and `ask_knowledge_base` and returned the correct label dose.
- Review: a six-lens adversarial review (81 agents) produced 25 findings; the confirmed ones were fixed
  (`**ERROR**` answers, a tag regex that ate `< 30 mL/min`, uncaught CLI timeouts, repeated names creating
  `kb+kb-assistant`, a malformed key echoed in errors, duplicate basenames uploaded twice, the ingest
  script's string-similarity crash and hard-coded embedding model, plus test and doc gaps).

**Pending / carry-over**
- `.env` still uses the legacy name `RAGFLOW_API_URL` (works through the fallback); rename to `RAGFLOW_BASE_URL`.
- The golden kb rows and the knowledge-base routing rows (`route-06..09`, `route-15`) describe the former
  local datasets; the remote `rag-mini-wiki` has no passage markers, so kb rows cannot be re-recorded until
  the marker corpus is ingested there (`ingest_rag_mini_wikipedia.py`, embedding model copied from the
  server). `expected_sources` were remapped the same day (`ragflow:rag-mini-wiki`, `ragflow:handbook`;
  `v1.jsonl` regenerated, `SOURCE_PATTERN` widened). A retrieval-only spot check found the expected answer
  in the top 5 `rag-mini-wiki` chunks for 7 of 8 sampled kb rows. Grading the already-recorded 2026-09-26
  kb rows does not need RAGFlow.
- Commit the RAGFlow change and the Day 3 harness.
