"""Tests for tools/mongo_tools.py with a fake MCP session."""
import json

import pytest
from mcp import MCPError

import tools.mongo_tools as mongo_tools
from tools.mcp_client import MAX_DOCUMENTS_PER_QUERY, get_mongo_config, server_parameters
from tools.mongo_tools import (
    aggregate_documents,
    count_documents,
    find_documents,
    get_collection_schema,
    list_collections,
)

ALL_TOOLS = (list_collections, get_collection_schema, find_documents, aggregate_documents, count_documents)
BAD_NAMES = ["", "drugs; x", "schema.drugs", "1drugs", "drugs d", "`drugs`", "drugs-x", "$cmd"]


# -------------------------------------------------------------- config --
def test_get_mongo_config_reads_env(test_env, monkeypatch):
    monkeypatch.setenv("MONGODB_MCP_COMMAND", "mongodb-mcp-server")
    monkeypatch.setenv("MONGODB_MCP_ARGS", "--foo bar")
    cfg = get_mongo_config()
    assert cfg["uri"] == test_env["MONGODB_URI"]
    assert cfg["database"] == test_env["MONGODB_DATABASE"]
    assert cfg["command"] == "mongodb-mcp-server"
    assert cfg["args"] == ["--foo", "bar"]


def test_get_mongo_config_defaults(monkeypatch):
    monkeypatch.delenv("MONGODB_DATABASE", raising=False)
    monkeypatch.delenv("MONGODB_MCP_COMMAND", raising=False)
    monkeypatch.delenv("MONGODB_MCP_ARGS", raising=False)
    monkeypatch.setattr(mongo_tools_client(), "shutil", FakeShutil(found=False))
    cfg = get_mongo_config()
    assert cfg["database"] == "pharma_db"
    assert cfg["command"] == "npx"
    assert cfg["args"] == ["-y", "mongodb-mcp-server@3"]


def test_get_mongo_config_prefers_installed_binary(monkeypatch):
    monkeypatch.delenv("MONGODB_MCP_COMMAND", raising=False)
    monkeypatch.delenv("MONGODB_MCP_ARGS", raising=False)
    monkeypatch.setattr(mongo_tools_client(), "shutil", FakeShutil(found=True))
    cfg = get_mongo_config()
    assert cfg["command"] == "mongodb-mcp-server" and cfg["args"] == []


def test_get_mongo_config_missing_uri_raises(monkeypatch):
    monkeypatch.delenv("MONGODB_URI")
    with pytest.raises(ValueError, match="MONGODB_URI"):
        get_mongo_config()


def test_server_parameters_are_read_only_and_do_not_leak_uri(test_env, monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.test:3128")
    params = server_parameters(get_mongo_config())
    env = params.env
    assert env["MDB_MCP_CONNECTION_STRING"] == test_env["MONGODB_URI"]
    assert env["MDB_MCP_READ_ONLY"] == "true"
    assert env["MDB_MCP_MAX_DOCUMENTS_PER_QUERY"] == str(MAX_DOCUMENTS_PER_QUERY)
    assert env["MDB_MCP_TELEMETRY"] == "disabled"
    assert env["HTTPS_PROXY"] == "http://proxy.test:3128"
    for category in ("atlas", "create", "update", "delete"):
        assert category in env["MDB_MCP_DISABLED_TOOLS"].split(",")
    assert test_env["MONGODB_URI"] not in " ".join([params.command, *params.args])


class FakeShutil:
    def __init__(self, found):
        self.found = found

    def which(self, name):
        return f"/usr/bin/{name}" if self.found else None


def mongo_tools_client():
    import tools.mcp_client as mcp_client
    return mcp_client


# ------------------------------------------------------------ metadata --
def test_tool_names_and_schemas():
    assert [t.name for t in ALL_TOOLS] == [
        "list_collections", "get_collection_schema", "find_documents", "aggregate_documents", "count_documents",
    ]
    assert list_collections.args == {}
    assert set(get_collection_schema.args) == {"collection"}
    assert set(find_documents.args) == {"collection", "filter", "projection", "sort", "limit"}
    assert set(aggregate_documents.args) == {"collection", "pipeline"}
    assert set(count_documents.args) == {"collection", "filter"}
    for t in ALL_TOOLS:
        assert t.description.strip()


# ---------------------------------------------------- list_collections --
def test_list_collections_returns_names(fake_mcp, monitor_calls):
    h = fake_mcp(structured={"collections": [{"name": "drugs"}, {"name": "inventory"}, {"name": "sales_records"}]})
    assert list_collections.invoke({}) == "Found collections: drugs,inventory,sales_records"
    assert h.calls == [("list-collections", {"database": "test_db"})]
    assert len(monitor_calls) == 1 and monitor_calls[0][1] == {}


def test_list_collections_empty(fake_mcp):
    fake_mcp(structured={"collections": [], "totalCount": 0})
    assert list_collections.invoke({}) == "No Collections Found"


def test_list_collections_server_error(fake_mcp):
    fake_mcp(text="Failed to connect using the configured connection string: boom", is_error=True)
    out = list_collections.invoke({})
    assert out.startswith("Exception Captured:") and "boom" in out


def test_list_collections_transport_error(fake_mcp):
    fake_mcp(error=RuntimeError("Could not start mongodb-mcp-server: npx missing"))
    out = list_collections.invoke({})
    assert out.startswith("Exception Captured:") and "npx missing" in out


def test_list_collections_missing_config(fake_mcp, monkeypatch):
    h = fake_mcp(structured={"collections": []})
    monkeypatch.delenv("MONGODB_URI")
    out = list_collections.invoke({})
    assert out.startswith("Exception Captured:") and "MONGODB_URI" in out
    assert h.calls == []


# ------------------------------------------------ get_collection_schema --
def test_get_collection_schema_returns_json(fake_mcp, monitor_calls):
    schema = {"schema": {"drug_id": ["Int32"], "generic_name": ["String"]}, "fieldsCount": 2}
    h = fake_mcp(structured=schema)
    out = get_collection_schema.invoke({"collection": "drugs"})
    assert json.loads(out) == schema
    assert h.calls == [("collection-schema", {"database": "test_db", "collection": "drugs", "sampleSize": 50})]
    assert monitor_calls[0][1] == {"collection": "drugs"}


@pytest.mark.parametrize("bad", BAD_NAMES)
def test_collection_name_is_validated_before_mcp(fake_mcp, bad):
    h = fake_mcp(structured={})
    assert get_collection_schema.invoke({"collection": bad}) == f"Invalid collection name: {bad}"
    assert find_documents.invoke({"collection": bad}) == f"Invalid collection name: {bad}"
    assert aggregate_documents.invoke({"collection": bad, "pipeline": "[]"}) == f"Invalid collection name: {bad}"
    assert count_documents.invoke({"collection": bad}) == f"Invalid collection name: {bad}"
    assert h.calls == []


# -------------------------------------------------------- find_documents --
def test_find_documents_passes_parsed_arguments(fake_mcp, monitor_calls):
    docs = {"documents": [{"drug_id": 1, "generic_name": "Amoxicillin Capsules"}], "appliedLimits": []}
    h = fake_mcp(structured=docs)
    out = find_documents.invoke({
        "collection": "drugs", "filter": '{"therapeutic_area": "Antibiotic"}',
        "projection": '{"generic_name": 1, "_id": 0}', "sort": '{"drug_id": -1}', "limit": 5,
    })
    assert json.loads(out) == docs
    assert h.calls == [("find", {
        "database": "test_db", "collection": "drugs", "filter": {"therapeutic_area": "Antibiotic"},
        "projection": {"generic_name": 1, "_id": 0}, "sort": {"drug_id": -1}, "limit": 5,
        "responseBytesLimit": mongo_tools._RESPONSE_BYTES_LIMIT,
    })]
    assert monitor_calls[0][1]["collection"] == "drugs"


def test_find_documents_defaults_and_limit_clamp(fake_mcp):
    h = fake_mcp(structured={"documents": []})
    find_documents.invoke({"collection": "drugs", "limit": 500})
    find_documents.invoke({"collection": "drugs", "limit": 0})
    find_documents.invoke({"collection": "drugs"})
    limits = [args["limit"] for _, args in h.calls]
    assert limits == [MAX_DOCUMENTS_PER_QUERY, 1, 20]
    assert all(args["filter"] == {} and "projection" not in args and "sort" not in args for _, args in h.calls)


@pytest.mark.parametrize("field,value", [("filter", "{not json"), ("filter", "[1, 2]"), ("projection", "nope"), ("sort", "[]")])
def test_find_documents_rejects_bad_json_before_mcp(fake_mcp, field, value):
    h = fake_mcp(structured={"documents": []})
    out = find_documents.invoke({"collection": "drugs", field: value})
    assert out.startswith("Exception Captured:") and field in out
    assert h.calls == []


def test_find_documents_falls_back_to_text_content(fake_mcp):
    fake_mcp(text="Query on collection \"drugs\" resulted in 0 documents.")
    assert find_documents.invoke({"collection": "drugs"}).startswith("Query on collection")


def test_find_documents_mcp_error(fake_mcp):
    fake_mcp(error=MCPError(-32001, "Request timed out"))
    out = find_documents.invoke({"collection": "drugs"})
    assert out.startswith("Exception Captured:") and "timed out" in out


# --------------------------------------------------- aggregate_documents --
def test_aggregate_documents_runs_pipeline(fake_mcp):
    pipeline = [{"$group": {"_id": "$region", "revenue": {"$sum": "$total_amount"}}}, {"$sort": {"revenue": -1}}]
    h = fake_mcp(structured={"documents": [{"_id": "North China", "revenue": 717250.0}], "count": 1})
    out = aggregate_documents.invoke({"collection": "sales_records", "pipeline": json.dumps(pipeline)})
    assert json.loads(out)["documents"][0]["_id"] == "North China"
    assert h.calls == [("aggregate", {"database": "test_db", "collection": "sales_records", "pipeline": pipeline,
                                      "responseBytesLimit": mongo_tools._RESPONSE_BYTES_LIMIT})]


@pytest.mark.parametrize("pipeline", [
    '[{"$match": {}}, {"$out": "copy"}]',
    '[{"$merge": {"into": "copy"}}]',
    '[{"$match": {}, "$out": "copy"}]',
    '[]',
    '["$match"]',
])
def test_aggregate_documents_rejects_write_or_malformed_pipelines(fake_mcp, pipeline):
    h = fake_mcp(structured={"documents": []})
    out = aggregate_documents.invoke({"collection": "sales_records", "pipeline": pipeline})
    assert out.startswith("Only read-only pipelines are allowed")
    assert h.calls == []


@pytest.mark.parametrize("pipeline", ["{}", "not json", '{"$match": {}}'])
def test_aggregate_documents_rejects_non_array_pipelines(fake_mcp, pipeline):
    h = fake_mcp(structured={"documents": []})
    out = aggregate_documents.invoke({"collection": "sales_records", "pipeline": pipeline})
    assert out.startswith("Exception Captured:") and "pipeline" in out
    assert h.calls == []


def test_aggregate_documents_server_error(fake_mcp):
    fake_mcp(text="In readOnly mode you can not run pipelines with $out or $merge stages.", is_error=True)
    out = aggregate_documents.invoke({"collection": "sales_records", "pipeline": '[{"$match": {}}]'})
    assert out.startswith("Exception Captured:") and "readOnly" in out


# ------------------------------------------------------- count_documents --
def test_count_documents_uses_query_argument(fake_mcp, monitor_calls):
    h = fake_mcp(structured={"count": 3})
    assert json.loads(count_documents.invoke({"collection": "inventory", "filter": '{"drug_id": 1}'})) == {"count": 3}
    assert h.calls == [("count", {"database": "test_db", "collection": "inventory", "query": {"drug_id": 1}})]
    assert monitor_calls[0][1] == {"collection": "inventory", "filter": '{"drug_id": 1}'}


def test_count_documents_default_filter(fake_mcp):
    h = fake_mcp(structured={"count": 30})
    count_documents.invoke({"collection": "inventory"})
    assert h.calls[0][1]["query"] == {}
