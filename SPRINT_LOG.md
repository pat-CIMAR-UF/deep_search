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
