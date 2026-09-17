"""Read-only MongoDB tools for the Database Query Agent, executed through mongodb-mcp-server.

Every wrapper validates its input in Python before touching MCP, then calls one of the
allowlisted server tools (list-collections, collection-schema, find, aggregate, count).
The server itself runs with MDB_MCP_READ_ONLY=true, so writes are impossible even if a
wrapper were bypassed.
"""
import json
import re
import sys
from pathlib import Path

import anyio
from langchain_core.tools import tool
from mcp import MCPError
from mcp.types import CallToolResult

_PROJECT_ROOT = str(Path(__file__).parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from api.monitor import monitor  # noqa: E402
from tools.mcp_client import MAX_DOCUMENTS_PER_QUERY, call_mcp_tool, get_mongo_config  # noqa: E402

_MAX_DOCUMENTS = MAX_DOCUMENTS_PER_QUERY
_RESPONSE_BYTES_LIMIT = 65536
_COLLECTION_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# 只读模式下服务端也会拒绝，这里提前拦截 / The server rejects these in readOnly mode too; fail fast here
_WRITE_STAGES = frozenset({"$out", "$merge"})
_TOOL_ERRORS = (ValueError, RuntimeError, TimeoutError, MCPError,
                anyio.ClosedResourceError, anyio.BrokenResourceError)


def _valid_collection(name: str) -> bool:
    return bool(_COLLECTION_NAME_RE.fullmatch(name or ""))


def _parse_json(text, label: str, expected: type):
    """Parse a JSON argument (Extended JSON allowed) and check its container type."""
    if text is None or (isinstance(text, str) and not text.strip()):
        return expected()
    value = text
    if isinstance(text, str):
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label} must be valid JSON: {exc.msg}") from None
    if not isinstance(value, expected):
        kind = "object" if expected is dict else "array"
        raise ValueError(f"{label} must be a JSON {kind}.")
    return value


def _is_read_only_pipeline(pipeline: list) -> bool:
    for stage in pipeline:
        if not isinstance(stage, dict) or len(stage) != 1:
            return False
        if next(iter(stage)) in _WRITE_STAGES:
            return False
    return True


def _text(result: CallToolResult) -> str:
    return "\n".join(block.text for block in result.content if getattr(block, "type", "") == "text").strip()


def _format(result: CallToolResult) -> str:
    if result.is_error:
        return f"Exception Captured: {_text(result) or 'MCP tool failed'}"
    if result.structured_content is not None:
        return json.dumps(result.structured_content, ensure_ascii=False, default=str)
    return _text(result) or "No result returned."


def _run(name: str, arguments: dict) -> str:
    database = get_mongo_config()["database"]
    return _format(call_mcp_tool(name, {"database": database, **arguments}))


@tool
def list_collections() -> str:
    """List the collections in the business database. Call this first to learn which
    collections exist before querying. Returns collection names or an error message."""
    monitor.report_tool(tool_name="database query: list_collections()", args={})
    try:
        database = get_mongo_config()["database"]
        result = call_mcp_tool("list-collections", {"database": database})
        if result.is_error:
            return _format(result)
        content = result.structured_content
        if isinstance(content, dict) and isinstance(content.get("collections"), list):
            names = [c.get("name") if isinstance(c, dict) else str(c) for c in content["collections"]]
            names = [n for n in names if n]
            return f"Found collections: {','.join(names)}" if names else "No Collections Found"
        return _format(result)
    except _TOOL_ERRORS as e:
        return f"Exception Captured: {e}"


@tool
def get_collection_schema(collection: str) -> str:
    """Infer a collection's fields and value types from a sample of documents. Call
    list_collections first to confirm the name.

    Args:
        collection: Collection name, e.g. drugs (letters, digits, underscores only).

    Returns:
        JSON with the inferred schema, or an error message."""
    monitor.report_tool(tool_name="database query: get_collection_schema()", args={"collection": collection})
    if not _valid_collection(collection):
        return f"Invalid collection name: {collection}"
    try:
        return _run("collection-schema", {"collection": collection, "sampleSize": 50})
    except _TOOL_ERRORS as e:
        return f"Exception Captured: {e}"


@tool
def find_documents(collection: str, filter: str = "{}", projection: str | None = None,
                   sort: str | None = None, limit: int = 20) -> str:
    """Read documents from a collection with an optional MongoDB filter. Results are capped
    at 100 documents; use aggregate_documents for totals or grouped statistics.

    Args:
        collection: Collection name, e.g. drugs.
        filter: MongoDB query as a JSON string, e.g. {"therapeutic_area": "Antibiotic"}.
        projection: Optional JSON string of fields to include, e.g. {"generic_name": 1, "_id": 0}.
        sort: Optional JSON string, e.g. {"sale_date": -1}.
        limit: Maximum number of documents (1-100).

    Returns:
        JSON with the matching documents, or an error message."""
    monitor.report_tool(tool_name="database query: find_documents()",
                        args={"collection": collection, "filter": filter, "limit": limit})
    if not _valid_collection(collection):
        return f"Invalid collection name: {collection}"
    try:
        arguments = {
            "collection": collection,
            "filter": _parse_json(filter, "filter", dict),
            "limit": max(1, min(int(limit), _MAX_DOCUMENTS)),
            "responseBytesLimit": _RESPONSE_BYTES_LIMIT,
        }
        if projection:
            arguments["projection"] = _parse_json(projection, "projection", dict)
        if sort:
            arguments["sort"] = _parse_json(sort, "sort", dict)
        return _run("find", arguments)
    except _TOOL_ERRORS as e:
        return f"Exception Captured: {e}"


@tool
def aggregate_documents(collection: str, pipeline: str) -> str:
    """Run a read-only aggregation pipeline for totals, grouping, sorting, or joins
    ($lookup on drug_id). $out and $merge stages are rejected. Results are capped at
    100 documents.

    Args:
        collection: Collection name to start the pipeline from, e.g. sales_records.
        pipeline: JSON array of stages, e.g.
            [{"$group": {"_id": "$region", "revenue": {"$sum": "$total_amount"}}}, {"$sort": {"revenue": -1}}]

    Returns:
        JSON with the resulting documents, or an error message."""
    monitor.report_tool(tool_name="database query: aggregate_documents()",
                        args={"collection": collection, "pipeline": pipeline})
    if not _valid_collection(collection):
        return f"Invalid collection name: {collection}"
    try:
        stages = _parse_json(pipeline, "pipeline", list)
        if not stages or not _is_read_only_pipeline(stages):
            return "Only read-only pipelines are allowed (each stage a single-key object; $out / $merge are rejected)."
        return _run("aggregate", {"collection": collection, "pipeline": stages,
                                  "responseBytesLimit": _RESPONSE_BYTES_LIMIT})
    except _TOOL_ERRORS as e:
        return f"Exception Captured: {e}"


@tool
def count_documents(collection: str, filter: str = "{}") -> str:
    """Count the documents in a collection that match an optional filter.

    Args:
        collection: Collection name, e.g. inventory.
        filter: MongoDB query as a JSON string; {} counts everything.

    Returns:
        The count, or an error message."""
    monitor.report_tool(tool_name="database query: count_documents()",
                        args={"collection": collection, "filter": filter})
    if not _valid_collection(collection):
        return f"Invalid collection name: {collection}"
    try:
        return _run("count", {"collection": collection, "query": _parse_json(filter, "filter", dict)})
    except _TOOL_ERRORS as e:
        return f"Exception Captured: {e}"


if __name__ == "__main__":
    print(list_collections.invoke({}))
    print(aggregate_documents.invoke({
        "collection": "sales_records",
        "pipeline": '[{"$group": {"_id": "$region", "revenue": {"$sum": "$total_amount"}}}, {"$sort": {"revenue": -1}}]',
    }))
