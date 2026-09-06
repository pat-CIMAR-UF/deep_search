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
- MySQL 8 (for the database query agent)

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

# Database (section 4.3.2.2)
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=deepagents
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=pharma_db
```

## Database setup

The seed data is `sql/company_data.sql` — a mock pharmaceutical business database with three
tables: `drugs` (10 rows), `inventory` (30 batches) and `sales_records` (20 orders).

### 1. Install and start MySQL

On Ubuntu / WSL:

```bash
sudo apt-get update && sudo apt-get install -y mysql-server
sudo service mysql start
```

### 2. Create the database and application user

Replace `<password>` with the value you put in `MYSQL_PASSWORD`:

```bash
sudo mysql -e "
CREATE DATABASE IF NOT EXISTS pharma_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'deepagents'@'localhost'  IDENTIFIED BY '<password>';
CREATE USER IF NOT EXISTS 'deepagents'@'127.0.0.1' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON pharma_db.* TO 'deepagents'@'localhost';
GRANT ALL PRIVILEGES ON pharma_db.* TO 'deepagents'@'127.0.0.1';
FLUSH PRIVILEGES;"
```

### 3. Load the seed data

```bash
set -a; . ./.env; set +a
mysql -h"$MYSQL_HOST" -P"$MYSQL_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" < sql/company_data.sql
```

Expected result: 10 drugs, 30 inventory rows, 20 sales records.

```bash
mysql -h"$MYSQL_HOST" -P"$MYSQL_PORT" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
SELECT 'drugs' t, COUNT(*) n FROM drugs
UNION ALL SELECT 'inventory',     COUNT(*) FROM inventory
UNION ALL SELECT 'sales_records', COUNT(*) FROM sales_records;"
```

### 4. Viewing the data

Interactive shell:

```bash
set -a; . ./.env; set +a
mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"
```

Then `SHOW TABLES;`, `DESCRIBE inventory;`, `SELECT * FROM drugs\G`.

One-off queries (`--table` draws the boxed output, `--vertical` prints one field per line):

```bash
M="mysql -h$MYSQL_HOST -P$MYSQL_PORT -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE --table"

$M -e "SELECT drug_id, generic_name, brand_name, therapeutic_area FROM drugs;"
$M -e "SELECT d.generic_name, SUM(i.quantity_on_hand) AS stock
       FROM drugs d JOIN inventory i USING(drug_id) GROUP BY 1 ORDER BY stock DESC;"
$M -e "SELECT region, COUNT(*) AS orders, SUM(total_amount) AS revenue
       FROM sales_records GROUP BY 1 ORDER BY revenue DESC;"
```

A GUI (MySQL Workbench, DBeaver) also works — connect to `localhost:3306` with the `.env`
credentials. From Windows against a WSL2 server, `localhost` is forwarded automatically.

> **WSL note:** systemd does not start services automatically, so run `sudo service mysql start`
> again after each WSL restart.

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
sql/company_data.sql         # mock pharmaceutical database seed data
tools/
  gemini_tool.py             # internet_search via Gemini + Google Search grounding
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
