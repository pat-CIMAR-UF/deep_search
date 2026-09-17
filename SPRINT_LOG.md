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
