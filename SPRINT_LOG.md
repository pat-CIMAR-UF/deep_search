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
- Test suite: 235 → 245 tests, all mocked.

**Baseline (before any evaluation-driven change)** — run 20260917T162918Z, `evals/baseline.json`

Coordinator: DeepSeek `deepseek-flash` (the self-hosted Qwen tunnel was too unreliable to
measure; switched today). 20/20 questions completed without a harness error; total estimated
cost $0.92.

| route | n | errors | p50 s | p95 s | mean tokens | mean tool calls | mean cost $ |
|---|---:|---:|---:|---:|---:|---:|---:|
| database | 6 | 0 | 15.78 | 17.99 | 34898 | 9.7 | 0.0128 |
| ragflow | 6 | 0 | 124.63 | 282.59 | 172539 | 30.8 | 0.0905 |
| internet | 5 | 0 | 49.57 | 93.36 | 56574 | 13.4 | 0.0363 |
| mixed | 3 | 0 | 54.01 | 58.93 | 79730 | 21.7 | 0.0389 |
| all | 20 | 0 | 47.0 | 193.99 | 88334 | 18.8 | 0.0459 |

Observations that Days 2–5 should turn into graded metrics:
- **Knowledge-base retrieval failed on every kb question.** RAGFlow answered `get_assistant_list`
  and retrieval found the right document (the amoxicillin label PDF appears in the sources),
  but the answer stream carried `**ERROR**: CONNECTION_ERROR`: RAGFlow's own chat model
  backend is unreachable (the assistants point at an LLM endpoint that is down, likely the same
  local server the coordinator just moved off). The RAGFlow Agent therefore reported honestly
  that it had no document text, and the coordinator then fanned out to the web and database
  agents looking for the same facts. That fan-out is why `ragflow` is the slowest and most
  expensive route (p95 283 s, 173k tokens). Root cause to fix before Day 2's golden set.
- **Routing over-fans-out.** 11/20 runs invoked exactly the expected specialists; 9/20 invoked
  extra ones (typically the RAGFlow Agent on web questions, or the web agent on kb questions).
  No run missed an expected specialist. This is the routing-accuracy baseline for Day 3.
- **Database route is tight**: 6/6 correct on spot check, ~16 s, ~10 tool calls, ~$0.013.
- Every run includes one `ls` call from the coordinator's built-in filesystem tools (scratch
  space); a candidate for the Day 5 context-engineering pass.

Cost assumptions (`evals/pricing.yaml`): DeepSeek `deepseek-flash` peak-hour cache-miss list
price for the coordinator; Gemini Flash-class list price for grounding tokens. Both are editable and recorded in `baseline.json`.

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
- Point the three RAGFlow chat assistants at a reachable chat model (RAGFlow → Model providers,
  e.g. DeepSeek), then re-run the kb questions: `uv run python evals/run_baseline.py --ids kb-01 kb-02 kb-03 kb-04 kb-05 kb-06 --output evals/baseline_kb_rerun.json`.
- Budget alert once the subscription is settled.
- Enable secret scanning + push protection when the repo goes public.
- Enable Docker Desktop WSL integration before Day 6.
