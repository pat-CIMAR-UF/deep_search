# Deep Search

A DeepAgents-based research assistant: a main agent coordinates sub-agents for web search
(Gemini + Google Search grounding, or Tavily) and structured database queries.

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
