# Deep Search

A DeepAgents-based research assistant: a main agent coordinates sub-agents for web search
(Gemini + Google Search grounding), structured database queries, and RAGFlow knowledge retrieval.

## Run the UI and API

The application uses a streaming DeepAgents coordinator with three specialists: **Database Query**,
**Internet Search** (Gemini with Google Search grounding), and **RAGFlow Knowledge Base**.
The coordinator also reads uploaded files and generates downloadable Markdown/PDF reports.

From this project directory in WSL:

```bash
uv sync
uv run main.py
```

Open **http://localhost:8000**. A built UI is included in the current local checkout.
The server binds to loopback and serves the UI, HTTP API and WebSocket on the same port.
This is a local, single-user app; session IDs separate conversations, not authenticated users.
Run one server worker because active requests and WebSocket connections are managed in-process.

To rebuild the UI, install Node.js 20.19+ (or 22.12+) and npm in the environment where you run it:

```bash
cd ui
npm ci
npm run build
cd ..
uv run main.py
```

For frontend development, keep the API running and use `cd ui && npm run dev` in another
terminal. Open the URL printed by Vite. Its proxy forwards `/api` and `/ws` to port 8000.
Restart the backend after creating the first production build.

- **Auto** coordinates all three specialists; the dropdown directs research to the selected specialist.
- Tool activity is delivered live. Status polling and WebSocket snapshots recover interrupted
  connections. Refreshing restores the current conversation and its result.
- **Stop request** cancels agent orchestration. An external read-only call already in flight
  may finish in the background; its late events are ignored. Requests time out after five minutes.
- Attach up to five files: UTF-8 TXT/MD/CSV/TSV/JSON/LOG/SQL (64 KB each, fewer than 99,000 bytes
  total), or PDF/Word (.docx)/Excel (.xlsx/.xls) documents (10 MB each). Text is supplied as reference
  data; documents are read with the file tool. Uploads do not modify the RAGFlow knowledge bases.
- Answers are saved as Markdown. Requested reports can also be generated as PDF. The file sidebar lists attachments and reports for the
  current conversation. Files and conversation state persist under git-ignored `output/`.
- **New chat** starts a separate conversation. The browser remembers the current session ID.

The existing `.env` supplies the services. Optional `QWEN_MODEL` overrides the default model.
Check `GET /api/health` for application readiness; service connectivity is exercised when a
request runs; health reports registered capabilities, not provider connectivity. Set `RAGFLOW_API_URL`
and `RAGFLOW_API_KEY` for the same API-enabled RAGFlow instance. Restart the backend after changing `.env`.

Validation: `uv run pytest` uses mocked external services; `cd ui && npm run build` checks
TypeScript and the production bundle. See `api文档.md` for the implemented API contract.

## Requirements

- Python >= 3.13 with [uv](https://docs.astral.sh/uv/)
- Node.js >= 22.13 (runs `mongodb-mcp-server` for the database query agent)
- A MongoDB database: the project uses a MongoDB Atlas cluster

```bash
uv sync
```

## Configuration

All settings live in `.env` at the project root (git-ignored):

```ini
# LLM / search
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.7-flash
QWEN_REMOTE_BASE_URL=...
QWEN_REMOTE_API_KEY=...

# MongoDB (queried through mongodb-mcp-server, read-only)
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster-host>/pharma_db
MONGODB_DATABASE=pharma_db
# Optional: how to launch the MCP server (defaults: the global `mongodb-mcp-server`
# binary if installed, otherwise `npx -y mongodb-mcp-server@3`)
# MONGODB_MCP_COMMAND=mongodb-mcp-server
# MONGODB_MCP_ARGS=
```

## Database setup

The seed data lives in `mongo/seed/*.json` — a mock pharmaceutical business database with three
collections: `drugs` (10 documents), `inventory` (30 batches) and `sales_records` (20 orders).
The Database Query Agent never talks to MongoDB directly: it calls the official
[`mongodb-mcp-server`](https://github.com/mongodb-js/mongodb-mcp-server) over stdio, which the
backend spawns once per process with `MDB_MCP_READ_ONLY=true`.

### 1. Install Node.js and the MCP server

On Ubuntu / WSL (via [nvm](https://github.com/nvm-sh/nvm)):

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
. ~/.nvm/nvm.sh && nvm install 22 && nvm alias default 22
npm install -g mongodb-mcp-server@3
mongodb-mcp-server --version
```

Start the backend from a shell where `node` is on `PATH` (a new terminal after installing nvm).

### 2. Create the Atlas database user and network access

In MongoDB Atlas: *Database Access* → add a user (for example `deepagents`) with **readWrite** on
`pharma_db` (seeding needs write access; the app itself is read-only through the MCP server),
and *Network Access* → add your current public IP. Copy the `mongodb+srv://` connection string
into `MONGODB_URI` in `.env`, including `/pharma_db` as the default database.

### 3. Load the seed data

```bash
uv run python scripts/seed_mongo.py
```

Expected output: `drugs: 10 documents`, `inventory: 30 documents`, `sales_records: 20 documents`.
The script drops and recreates the three collections and their indexes, so it is safe to re-run.

### 4. Viewing the data

Any MongoDB client works — `mongosh "$MONGODB_URI"`, MongoDB Compass, or the Atlas Data Explorer.
Example aggregations the agent typically runs:

```javascript
db.inventory.aggregate([{ $group: { _id: "$drug_id", stock: { $sum: "$quantity_on_hand" } } },
                        { $sort: { stock: -1 } }])
db.sales_records.aggregate([{ $group: { _id: "$region", orders: { $sum: 1 }, revenue: { $sum: "$total_amount" } } },
                            { $sort: { revenue: -1 } }])
```

Quick check through the same tools the agent uses:

```bash
uv run python -c "from tools.mongo_tools import list_collections; print(list_collections.invoke({}))"
```

## Project layout

```
agent/
  llm.py                     # chat model used by the agents
  prompts.py                 # loads prompt/prompts.yaml
  subagents/
    internet_search_agent.py # web search sub-agent
api/
  context.py                 # per-request session/thread context (ContextVar)
  monitor.py                 # tool-call progress reporting (WebSocket / console)
prompt/prompts.yaml          # main-agent and sub-agent prompts
mongo/seed/*.json            # mock pharmaceutical database seed data
scripts/seed_mongo.py        # loads mongo/seed into MongoDB
tools/
  gemini_tool.py             # internet_search via Gemini + Google Search grounding
  mcp_client.py              # persistent stdio session to mongodb-mcp-server
  mongo_tools.py             # read-only MongoDB tools for the database agent
  tavily_tool.py             # internet_search via Tavily
utils/                       # path resolution, Markdown -> PDF conversion
```

## Smoke-testing a tool

Neither tool file defines a `__main__` block, so call the tool directly. Both tools add the
project root to `sys.path`, so running them as a script (`uv run tools/gemini_tool.py`) resolves
`api.monitor` as well — it just produces no output on its own.

```bash
uv run python -c "
from tools.gemini_tool import internet_search
r = internet_search.invoke({'query': 'latest stable Python release', 'max_results': 3})
print(r['answer'][:300]); print(r['sources'])
"
```
