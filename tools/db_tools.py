import os  # 系统路径/环境变量处理 / Env var handling
import re
import sys
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from mysql.connector import connect, Error

from langchain_core.tools import tool

_PROJECT_ROOT = str(Path(__file__).parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# 自定义模块：工具调用埋点监控 / Custom module: tool-call monitoring
from api.monitor import monitor  # noqa: E402  (必须在 sys.path 设置之后导入 / must come after the sys.path setup)

# 加载项目根目录的 .env 文件，读取环境变量（如 MYSQL_USER）/ Load .env from the project root
_ = load_dotenv(find_dotenv())

_MAX_ROWS = 100
_READ_ONLY_PREFIXES = ("select", "show", "describe", "desc", "explain", "with")
# 即使以只读关键字开头（如 WITH ... DELETE / SELECT ... INTO OUTFILE），出现这些关键字也视为写操作
# Statements that start read-only (WITH ... DELETE, SELECT ... INTO OUTFILE) are still writes if these appear
_WRITE_KEYWORDS = frozenset({
    "insert", "update", "delete", "drop", "alter", "create", "truncate", "rename",
    "grant", "revoke", "outfile", "dumpfile",
})
_STRING_LITERAL_RE = re.compile(r"'(?:[^'\\]|\\.)*'" + r'|"(?:[^"\\]|\\.)*"')


def get_db_config():
    """Get database configuration from environment variables."""
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "collation": os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
        "autocommit": True,
        "sql_mode": os.getenv("MYSQL_SQL_MODE", "TRADITIONAL")
    }
    # 移除 None 值（核心必要操作）
    config = {k: v for k, v in config.items() if v is not None}

    # 补充：校验核心配置是否存在（可选但推荐）
    required_keys = ["user", "password", "database"]
    missing_keys = [k for k in required_keys if k not in config]
    if missing_keys:
        raise ValueError(f"Missing core database configuration: {', '.join(missing_keys)}")

    return config


def _is_read_only_query(query: str) -> bool:
    body = query.strip().rstrip(";").strip()
    if not body or ";" in body:
        return False
    first = body.lstrip("(").split(None, 1)[0].lower()
    if first not in _READ_ONLY_PREFIXES:
        return False
    # 去掉字符串字面量后再扫描关键字，避免误判 WHERE name = 'delete' 之类的查询
    # Strip string literals before scanning so WHERE name = 'delete' is not rejected
    tokens = set(re.findall(r"[a-z_]+", _STRING_LITERAL_RE.sub("''", body).lower()))
    return not (tokens & _WRITE_KEYWORDS)


@tool
def list_sql_tables() -> str:
    """
    查询当前库中所有可用的表！
    作用：为了模型识别有哪些可用的表！方便进行后续的自定义sql查询
    :return: 有表： 可用的表有：表1,表2,表3....  没有表: 没有可用的表   出现异常：查询出现异常：异常信息
    """
    monitor.report_tool(tool_name="database schema check: list_sql_tables()", args={})

    try:
        config = get_db_config()
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                sql = "show tables"
                cursor.execute(sql)
                tables = cursor.fetchall()

                if not tables:
                    return "No Tables Found"

                table_names = [table[0] for table in tables]

                return f"Found tables: {','.join(table_names)}"
    except (Error, ValueError) as e:
        return f"Exception Captured: {str(e)}"


@tool
def get_table_data(table_name: str) -> str:
    """
    查询指定表名的数据！当前工具调用之前，必须先调用list_sql_tables完成表名的校验！
    此工具的作用：1.可以完成单表数据的查询 2. 可以为多表查询提供表结果信息（列名&数据格式）
    :param table_name: 表名
    :return: csv格式的数据（模拟表格数据格式）
             1.第一行是列信息，列之间使用,（英文的逗号）分割
             2.第二行开始是表数据，值之间也使用,(英文的逗号)分割
             3.行和行之间使用\n分割
             4.至多表数据查询100条
             例如：
                id,name,age\n -> 列头
                1,张三,18\n
                1,张三,18\n    -> 至多查询100条
                1,张三,18\n
                1,张三,18\n
    """
    monitor.report_tool(tool_name="database schema check: get_table_data()", args={"table_name": table_name})

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name or ""):
        return f"Invalid table name: {table_name}"

    try:
        config = get_db_config()
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                sql = f"SELECT * FROM `{table_name}` LIMIT {_MAX_ROWS}"
                cursor.execute(sql)
                description = cursor.description
                if not description:
                    return f"Invalid table name or query produced no columns: {table_name}"
                # description =>  [(id,列长度...),(date,....),()] => 元组 index = 0 列名
                # [列1,列2,列3...]
                columns = [desc[0] for desc in description]  # [1,2,3,4]
                # 表数据
                # [(1,张三),(2,李四),(3,二狗子)]
                rows = cursor.fetchall()
                header_str = ",".join(columns)
                if not rows:
                    return f"Table {table_name} is EMPTY! Columns: {header_str}"
                # (1,张三) -> ('1','张三') -> '1,张三'
                # ['1,张三','1,张三','1,张三','1,张三','1,张三']
                results = [",".join(map(str, row)) for row in rows]

                # columns -> csv -> header
                # id,name,age
                # '1,张三'\n
                data_str = "\n".join(results)
                return f"{header_str}\n{data_str}"

    except (Error, ValueError) as e:
        return f"Exception Captured: {str(e)}"


@tool
def execute_sql_query(query: str) -> str:
    """
    执行自定义查询sql语句！切记：执行之前，需要通过执行 list_sql_tables明确表名！执行get_table_data
    明确表结构和数据格式！
    :param query: 要执行的自定义sql语句
    :return: csv格式的数据（模拟表格数据格式）
             1.第一行是列信息，列之间使用,（英文的逗号）分割
             2.第二行开始是表数据，值之间也使用,(英文的逗号)分割
             3.行和行之间使用\n分割
             4.至多表数据查询100条
             例如：
                id,name,age\n -> 列头
                1,张三,18\n
                1,张三,18\n    -> 至多查询100条
                1,张三,18\n
                1,张三,18\n
    """
    # 埋点,调用工具了告诉前端哪个工具被调用了！！
    monitor.report_tool(tool_name="database schema check: execute_sql_query()", args={"query": query})

    if not _is_read_only_query(query):
        return "Only read-only queries are allowed (SELECT / SHOW / DESCRIBE / EXPLAIN / WITH)."

    try:
        config = get_db_config()
        # 1. 创建一个链接
        with connect(**config) as conn:
            # 2. 创建cursor
            with conn.cursor() as cursor:
                # 3. cursor执行sql语句
                cursor.execute(query)
                # 4. cursor获取返回结果
                # 4.1 获取列的信息
                # 返回的查询结果的列的信息
                # description => [(id,列长度...),(),()]
                # 如果查询没有结果 -》 description 也是None
                description = cursor.description
                if not description:
                    return f"No result found on the sql query: {query}!"
                # 4.2 获取查询结果
                # description =>  [(id,列长度...),(date,....),()] => 元组 index = 0 列名
                # [列1,列2,列3...]
                columns = [desc[0] for desc in description]  # [1,2,3,4]
                # 表数据
                # [(1,张三),(2,李四),(3,二狗子)]
                rows = cursor.fetchmany(_MAX_ROWS)
                # (1,张三) -> ('1','张三') -> '1,张三'
                # ['1,张三','1,张三','1,张三','1,张三','1,张三']
                results = [",".join(map(str, row)) for row in rows]

                # columns -> csv -> header
                # id,name,age
                header_str = ",".join(columns)
                # '1,张三'\n
                data_str = "\n".join(results)
                return f"{header_str}\n{data_str}"
    except (Error, ValueError) as e:
        return f"Exception Captured: {str(e)}"


if __name__ == "__main__":
    print(execute_sql_query.invoke({
        "query": "SELECT * FROM `drugs` dgs JOIN sales_records srd ON dgs.drug_id = srd.drug_id"
    }))
