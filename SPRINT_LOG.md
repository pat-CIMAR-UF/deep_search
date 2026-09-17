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

**Baseline (before any evaluation-driven change)**

Pending: the coordinator endpoint (Cloudflare quick tunnel) and RAGFlow were offline when the
harness was ready. A one-question smoke run confirmed the harness records failures cleanly
(0.7 s, `OpenAIConnectionError`). Run when both services are up:

```bash
uv run python evals/run_baseline.py
```

Then paste the printed summary table here.

| route | n | errors | p50 s | p95 s | mean tokens | mean tool calls | mean cost $ |
|---|---:|---:|---:|---:|---:|---:|---:|
| database | 6 | | | | | | |
| ragflow | 6 | | | | | | |
| internet | 5 | | | | | | |
| mixed | 3 | | | | | | |
| all | 20 | | | | | | |

Cost assumptions (`evals/pricing.yaml`): coordinator is self-hosted Qwen behind an
OpenAI-compatible endpoint, counted at $0 per token; Gemini Flash-class list price for
grounding tokens. Both are editable and recorded in `baseline.json`.

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
- Run the 20-question baseline and fill the table above (needs tunnel + RAGFlow up).
- Budget alert once the subscription is settled.
- Enable secret scanning + push protection when the repo goes public.
- Enable Docker Desktop WSL integration before Day 6.
