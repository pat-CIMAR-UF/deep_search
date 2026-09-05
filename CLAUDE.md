# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A DeepAgents-style research assistant for a mock pharmaceutical company: a main agent
(prompted from `prompt/prompts.yaml`) is meant to coordinate three sub-agents — web search
(Gemini with Google Search grounding, or Tavily), read-only MySQL queries, and a RAGFlow
knowledge base. Progress is pushed to a frontend over FastAPI WebSockets.

**Current state:** the sub-agent specs, tools, monitor/context plumbing and RAGFlow demos exist
and are tested. The main agent graph, the FastAPI app described in `api文档.md`, and a RAGFlow
sub-agent wrapper are *not* wired up yet — `main.py` is a placeholder and `deepagents` is not a
dependency. `Deep_Search_Project_Documentation.md` (and its Chinese twin `深度搜索项目文档.md`)
is the design doc / tutorial the code follows; `api文档.md` is the target HTTP/WebSocket API.

## Commands

Python 3.13 + [uv](https://docs.astral.sh/uv/). Always run through `uv run` so the `.venv` is used.

```bash
uv sync                                   # install deps (incl. dev group: pytest)
uv run pytest                             # full suite (~1s, fully mocked, no .env needed)
uv run pytest tests/test_db_tools.py      # one file
uv run pytest tests/test_db_tools.py -k read_only   # one test / pattern
uv run python -m agent.prompts            # dump the prompts.yaml sections
uv run python tools/db_tools.py           # runs the __main__ smoke query against real MySQL
```

There is no linter/formatter configured. Pytest config lives in `pyproject.toml`
(`testpaths = ["tests"]`, `pythonpath = ["."]`).

Smoke-testing a tool against a live service (needs keys in `.env`):

```bash
uv run python -c "
from tools.gemini_tool import internet_search
r = internet_search.invoke({'query': 'latest stable Python release', 'max_results': 3})
print(r['answer'][:300]); print(r['sources'])
"
```

## Configuration

Everything comes from `.env` at the project root (git-ignored), loaded via
`load_dotenv(find_dotenv())`. Keys in use: `GEMINI_API_KEY`, `GEMINI_MODEL`,
`QWEN_REMOTE_BASE_URL`, `QWEN_REMOTE_API_KEY`, `TAVILY_API_KEY`, `MYSQL_HOST/PORT/USER/PASSWORD/DATABASE`,
`RAGFLOW_API_KEY`, `RAGFLOW_API_URL`. MySQL seed data and setup steps are in `README.md`
(`sql/company_data.sql`: `drugs`, `inventory`, `sales_records`). On WSL, `sudo service mysql start`
after every restart.

## Architecture

**Sub-agent = dict spec, not a class.** Each `agent/subagents/*.py` exports a plain dict with
exactly `name`, `description`, `system_prompt`, `tools` (the DeepAgents `subagents=[...]` shape).
Text fields come from `prompt/prompts.yaml` under `sub_agents.<key>` (`gemini`, `db`, `ragflow`);
tests assert the dict mirrors the YAML section, so never hard-code prompt text in Python.
`agent/llm.py` builds the shared `ChatOpenAI` client pointing at a remote Qwen endpoint.

**Tools are LangChain `@tool` functions** in `tools/`. Both `gemini_tool.py` and `tavily_tool.py`
expose a tool named `internet_search`; the search sub-agent currently imports the Gemini one.
`tools/db_tools.py` enforces read-only SQL (`_is_read_only_query`: single statement, read-only
prefix, no write keywords outside string literals), validates table names with a regex, and
caps output at `_MAX_ROWS = 100` CSV rows.

**Cross-cutting plumbing in `api/`:**
- `api/monitor.py` — `monitor` singleton. Every tool calls `monitor.report_tool(name, args)` on
  entry. `_emit` fans out to (1) the FastAPI WebSocket for the current `thread_id`, (2) a
  `builtins.runtime.stream_writer` if a script runtime set one, (3) console. `ConnectionManager`
  must have `set_loop()` called from inside the running event loop before it can push.
- `api/context.py` — `ContextVar`s for `session_dir` and `thread_id`, so tools deep in the call
  stack know which request they serve without parameter threading. Set before running an agent,
  reset in `finally`.

**Import-time conventions that matter:**
- Modules under `tools/` insert the project root into `sys.path` *before* `from api.monitor import monitor`
  so they can be run as scripts. Keep that order if you add a tool.
- Importing a tool module must not fail when its API key is missing (Gemini client is lazy via
  `_get_client()`; there is a test enforcing this contract for Tavily too). `agent/llm.py` and
  `ragflow/*.py` *do* read env at import — `tests/conftest.py` injects dummy values before any
  project import for that reason.

**Tests** (`tests/`) mock every external service: `fake_db` fixture swaps `mysql.connector.connect`,
Gemini/Tavily/RAGFlow clients are `MagicMock`/`create_autospec`, and the autouse `monitor_calls`
fixture silences the monitor and records `report_tool` calls. Follow the same pattern; tests
must never hit the network or a real database.

**`utils/`:** `resolve_path()` maps model-emitted paths (`/workspace/...`, `/mnt/data/...`,
`output/...`, nested session dirs) onto a per-session directory — the docstring table is the spec.
`convert_md_to_pdf()` uses WeasyPrint (no MS Word).

## Notes

- Comments and docstrings are bilingual (Chinese / English); tool docstrings double as the
  LLM-facing tool descriptions, so wording changes there change agent behaviour.
- `ragflow/*_demo.py` are exploratory scripts with side-effecting `__main__` blocks (they create
  knowledge bases / ask a live assistant); don't run them casually.
