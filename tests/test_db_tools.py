"""Tests for tools/db_tools.py with a fake MySQL connection."""
import pytest
from mysql.connector import Error as MySQLError
from mysql.connector import ProgrammingError

import tools.db_tools as db_tools
from tools.db_tools import (
    _MAX_ROWS,
    _is_read_only_query,
    execute_sql_query,
    get_db_config,
    get_table_data,
    list_sql_tables,
)


# ----------------------------------------------------------- get_db_config --
def test_get_db_config_reads_env(test_env):
    cfg = get_db_config()
    assert cfg["host"] == test_env["MYSQL_HOST"]
    assert cfg["port"] == int(test_env["MYSQL_PORT"])
    assert isinstance(cfg["port"], int)
    assert cfg["user"] == test_env["MYSQL_USER"]
    assert cfg["password"] == test_env["MYSQL_PASSWORD"]
    assert cfg["database"] == test_env["MYSQL_DATABASE"]
    assert cfg["autocommit"] is True
    assert None not in cfg.values()


def test_get_db_config_defaults(monkeypatch):
    for k in ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_CHARSET", "MYSQL_COLLATION", "MYSQL_SQL_MODE"):
        monkeypatch.delenv(k, raising=False)
    cfg = get_db_config()
    assert cfg["host"] == "localhost"
    assert cfg["port"] == 3306
    assert cfg["charset"] == "utf8mb4"
    assert cfg["collation"] == "utf8mb4_unicode_ci"
    assert cfg["sql_mode"] == "TRADITIONAL"


@pytest.mark.parametrize("missing", ["MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"])
def test_get_db_config_missing_required_raises(monkeypatch, missing):
    monkeypatch.delenv(missing)
    with pytest.raises(ValueError, match=missing.removeprefix("MYSQL_").lower()):
        get_db_config()


def test_get_db_config_bad_port_raises(monkeypatch):
    monkeypatch.setenv("MYSQL_PORT", "not-a-port")
    with pytest.raises(ValueError):
        get_db_config()


# ------------------------------------------------------ _is_read_only_query --
@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM drugs",
        "select 1",
        "  SELECT 1  ;  ",
        "SHOW TABLES",
        "DESCRIBE drugs",
        "desc drugs;",
        "EXPLAIN SELECT 1",
        "WITH t AS (SELECT 1) SELECT * FROM t",
        "(SELECT 1) UNION (SELECT 2)",
        "SELECT * FROM a\nJOIN b ON a.id = b.id",
        "SELECT * FROM drugs WHERE name = 'delete me'",
        "SELECT REPLACE(name, 'a', 'b'), updated_at FROM drugs",
        'SELECT * FROM drugs WHERE note = "drop table"',
    ],
)
def test_read_only_queries_allowed(query):
    assert _is_read_only_query(query) is True


@pytest.mark.parametrize(
    "query",
    [
        "",
        "   ",
        ";",
        "INSERT INTO drugs VALUES (1)",
        "UPDATE drugs SET x = 1",
        "DELETE FROM drugs",
        "DROP TABLE drugs",
        "TRUNCATE drugs",
        "ALTER TABLE drugs ADD c INT",
        "CREATE TABLE t (id INT)",
        "GRANT ALL ON *.* TO 'x'@'%'",
        "SELECT 1; DROP TABLE drugs",
        "SELECT 1;; DROP TABLE drugs",
        "-- comment\nDROP TABLE drugs",
        "/* c */ DROP TABLE drugs",
        "WITH t AS (SELECT 1) DELETE FROM drugs",
        "WITH t AS (SELECT 1) UPDATE drugs SET x = 1",
        "WITH t AS (SELECT 1) INSERT INTO drugs SELECT * FROM t",
        "SELECT * FROM drugs INTO OUTFILE '/tmp/x'",
    ],
)
def test_write_or_multi_statement_queries_rejected(query):
    assert _is_read_only_query(query) is False


# ----------------------------------------------------------- tool metadata --
def test_tool_names_and_schemas():
    assert list_sql_tables.name == "list_sql_tables"
    assert get_table_data.name == "get_table_data"
    assert execute_sql_query.name == "execute_sql_query"
    assert list_sql_tables.args == {}
    assert set(get_table_data.args) == {"table_name"}
    assert set(execute_sql_query.args) == {"query"}
    for t in (list_sql_tables, get_table_data, execute_sql_query):
        assert t.description.strip()


# --------------------------------------------------------- list_sql_tables --
def test_list_sql_tables_returns_names(fake_db, monitor_calls):
    h = fake_db(rows=[("drugs",), ("inventory",), ("sales_records",)])
    assert list_sql_tables.invoke({}) == "Found tables: drugs,inventory,sales_records"
    assert h.cursor.executed == ["show tables"]
    assert h.connect_kwargs == get_db_config()
    assert h.connection.closed is True
    assert len(monitor_calls) == 1 and monitor_calls[0][1] == {}


def test_list_sql_tables_empty(fake_db):
    fake_db(rows=[])
    assert list_sql_tables.invoke({}) == "No Tables Found"


def test_list_sql_tables_connection_error(fake_db):
    fake_db(connect_error=MySQLError("boom"))
    out = list_sql_tables.invoke({})
    assert out.startswith("Exception Captured:") and "boom" in out


def test_list_sql_tables_missing_config(fake_db, monkeypatch):
    fake_db()
    monkeypatch.delenv("MYSQL_USER")
    out = list_sql_tables.invoke({})
    assert out.startswith("Exception Captured:") and "user" in out


# ---------------------------------------------------------- get_table_data --
def test_get_table_data_csv(fake_db, monitor_calls):
    h = fake_db(
        rows=[(1, "Aspirin", 9.5), (2, "Ibuprofen", None)],
        description=[("id",), ("name",), ("price",)],
    )
    out = get_table_data.invoke({"table_name": "drugs"})
    assert out == "id,name,price\n1,Aspirin,9.5\n2,Ibuprofen,None"
    assert h.cursor.executed == [f"SELECT * FROM `drugs` LIMIT {_MAX_ROWS}"]
    assert monitor_calls[0][1] == {"table_name": "drugs"}


def test_get_table_data_empty_table(fake_db):
    fake_db(rows=[], description=[("id",), ("name",)])
    out = get_table_data.invoke({"table_name": "drugs"})
    assert out == "Table drugs is EMPTY! Columns: id,name"


def test_get_table_data_no_description(fake_db):
    fake_db(rows=[], description=None)
    out = get_table_data.invoke({"table_name": "drugs"})
    assert "drugs" in out and "no columns" in out


@pytest.mark.parametrize(
    "bad",
    ["", "drugs; DROP TABLE x", "schema.drugs", "1drugs", "drugs d", "`drugs`", "drugs-x"],
)
def test_get_table_data_rejects_invalid_names(fake_db, bad):
    h = fake_db(rows=[(1,)], description=[("id",)])
    out = get_table_data.invoke({"table_name": bad})
    assert out == f"Invalid table name: {bad}"
    assert h.cursor.executed == []  # never reached the database


def test_get_table_data_db_error(fake_db):
    fake_db(execute_error=ProgrammingError("Table 'x' doesn't exist"))
    out = get_table_data.invoke({"table_name": "x"})
    assert out.startswith("Exception Captured:") and "doesn't exist" in out


# ------------------------------------------------------- execute_sql_query --
def test_execute_sql_query_csv(fake_db, monitor_calls):
    h = fake_db(rows=[(1, "a"), (2, "b")], description=[("id",), ("v",)])
    q = "SELECT id, v FROM t"
    assert execute_sql_query.invoke({"query": q}) == "id,v\n1,a\n2,b"
    assert h.cursor.executed == [q]
    assert h.cursor.fetchmany_size == _MAX_ROWS
    assert monitor_calls[0][1] == {"query": q}


def test_execute_sql_query_caps_rows(fake_db):
    fake_db(rows=[(i,) for i in range(_MAX_ROWS + 50)], description=[("id",)])
    out = execute_sql_query.invoke({"query": "SELECT id FROM t"})
    assert len(out.splitlines()) == _MAX_ROWS + 1  # header + capped rows


def test_execute_sql_query_no_result(fake_db):
    fake_db(rows=[], description=None)
    out = execute_sql_query.invoke({"query": "SELECT 1"})
    assert out.startswith("No result found")


@pytest.mark.parametrize("q", ["DELETE FROM t", "SELECT 1; DROP TABLE t", "WITH c AS (SELECT 1) DELETE FROM t"])
def test_execute_sql_query_rejects_writes_before_connecting(fake_db, q):
    h = fake_db(rows=[(1,)], description=[("id",)])
    out = execute_sql_query.invoke({"query": q})
    assert out.startswith("Only read-only queries are allowed")
    assert h.connect_kwargs is None  # connect() never called


def test_execute_sql_query_db_error(fake_db):
    fake_db(execute_error=ProgrammingError("syntax error"))
    out = execute_sql_query.invoke({"query": "SELECT * FORM t"})
    assert out.startswith("Exception Captured:") and "syntax error" in out
