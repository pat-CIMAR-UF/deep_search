"""Tests for agent/: prompt loading, LLM configuration and sub-agent wiring."""
from pathlib import Path

import pytest
import yaml
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

import agent.prompts as prompts
from agent.llm import llm
from agent.subagents.database_query_agent import database_query_agent
from agent.subagents.internet_search_agent import internet_search_agent

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SUBAGENT_KEYS = {"name", "description", "system_prompt"}


# ----------------------------------------------------------------- prompts --
def test_load_yaml_reads_mapping(tmp_path):
    p = tmp_path / "x.yaml"
    p.write_text("a: 1\nb:\n  c: text\n", encoding="utf-8")
    assert prompts.load_yaml(p) == {"a": 1, "b": {"c": "text"}}
    assert prompts.load_yaml(str(p)) == {"a": 1, "b": {"c": "text"}}


def test_load_yaml_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        prompts.load_yaml(tmp_path / "missing.yaml")


def test_prompt_paths_point_at_project_yaml():
    assert prompts.project_root_path == PROJECT_ROOT
    assert prompts.yaml_file_path == PROJECT_ROOT / "prompt" / "prompts.yaml"
    assert prompts.yaml_file_path.is_file()


def test_prompt_yaml_content_matches_file():
    with open(prompts.yaml_file_path, encoding="utf-8") as f:
        expected = yaml.safe_load(f)
    assert prompts.prompt_yaml_content == expected
    assert prompts.main_agent_content == expected["main_agent"]
    assert prompts.sub_agents_content == expected["sub_agents"]


def test_main_agent_has_system_prompt():
    sp = prompts.main_agent_content.get("system_prompt")
    assert isinstance(sp, str) and sp.strip()


@pytest.mark.parametrize("key", ["gemini", "db", "ragflow"])
def test_every_sub_agent_section_is_complete(key):
    section = prompts.sub_agents_content[key]
    assert REQUIRED_SUBAGENT_KEYS <= set(section)
    for field in REQUIRED_SUBAGENT_KEYS:
        assert isinstance(section[field], str) and section[field].strip(), field


# --------------------------------------------------------------------- llm --
def test_llm_is_chat_openai_configured_from_env(test_env):
    assert isinstance(llm, ChatOpenAI)
    assert llm.openai_api_base == test_env["QWEN_REMOTE_BASE_URL"]
    assert llm.model_name == "unsloth/Qwen3.8-27B-GGUF:UD-Q6_K_M"


def test_llm_api_key_is_secret_and_not_leaked(test_env):
    assert llm.openai_api_key.get_secret_value() == test_env["QWEN_REMOTE_API_KEY"]
    assert test_env["QWEN_REMOTE_API_KEY"] not in repr(llm)
    assert test_env["QWEN_REMOTE_API_KEY"] not in str(llm)


# --------------------------------------------------------------- subagents --
def _assert_subagent_shape(spec):
    assert set(spec) == REQUIRED_SUBAGENT_KEYS | {"tools"}
    for field in REQUIRED_SUBAGENT_KEYS:
        assert isinstance(spec[field], str) and spec[field].strip(), field
    assert isinstance(spec["tools"], list) and spec["tools"]
    for t in spec["tools"]:
        assert isinstance(t, BaseTool)


def test_database_query_agent_shape():
    _assert_subagent_shape(database_query_agent)
    assert [t.name for t in database_query_agent["tools"]] == [
        "list_collections",
        "get_collection_schema",
        "find_documents",
        "aggregate_documents",
        "count_documents",
    ]


def test_database_query_agent_uses_db_prompt_section():
    section = prompts.sub_agents_content["db"]
    assert database_query_agent["name"] == section["name"]
    assert database_query_agent["description"] == section["description"]
    assert database_query_agent["system_prompt"] == section["system_prompt"]


def test_internet_search_agent_shape():
    _assert_subagent_shape(internet_search_agent)
    assert [t.name for t in internet_search_agent["tools"]] == ["internet_search"]


def test_internet_search_agent_uses_gemini_tool():
    from tools.gemini_tool import internet_search

    assert internet_search_agent["tools"] == [internet_search]


def test_internet_search_agent_uses_web_search_prompt_section():
    """The agent must be driven by prompts.yaml, not by hard-coded fallbacks."""
    section = prompts.sub_agents_content["gemini"]
    assert internet_search_agent["name"] == section["name"]
    assert internet_search_agent["description"] == section["description"]
    assert internet_search_agent["system_prompt"] == section["system_prompt"]


def test_subagent_names_are_unique():
    names = [database_query_agent["name"], internet_search_agent["name"]]
    assert len(set(names)) == len(names)


def test_qwen_tool_roundtrip_omits_unsupported_agent_names():
    import httpx
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
    from agent.llm import QwenChatOpenAI
    requests = []
    def respond(request):
        import json
        payload = json.loads(request.content)
        requests.append(payload)
        assert all('name' not in m for m in payload['messages'] if m['role'] != 'tool')
        assert payload['messages'][-1]['tool_call_id'] == 'call-1'
        return httpx.Response(200, json={
            'id': 'test', 'object': 'chat.completion', 'created': 0, 'model': 'qwen-test',
            'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Collections found'}, 'finish_reason': 'stop'}],
        })
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        model = QwenChatOpenAI(model='qwen-test', base_url='http://qwen.test/v1', api_key='test-key', http_client=client)
        result = model.invoke([
            HumanMessage(content='List collections'),
            AIMessage(content='', name='Database Query Agent', tool_calls=[
                {'name': 'list_collections', 'args': {}, 'id': 'call-1', 'type': 'tool_call'}]),
            ToolMessage(content='drugs', tool_call_id='call-1', name='list_collections'),
        ])
    assert result.content == 'Collections found'
    assert len(requests) == 1


# -------------------------------------------------- knowledge base subagent --
def test_knowledge_base_agent_shape_and_prompt_section():
    from agent.subagents.knowledge_base_agent import knowledge_base_agent
    from tools.ragflow_tools import create_ask_delete, get_assistant_list

    _assert_subagent_shape(knowledge_base_agent)
    assert knowledge_base_agent["tools"] == [get_assistant_list, create_ask_delete]
    section = prompts.sub_agents_content["ragflow"]
    assert knowledge_base_agent["name"] == section["name"]
    assert knowledge_base_agent["description"] == section["description"]
    assert knowledge_base_agent["system_prompt"] == section["system_prompt"]


def test_all_three_specialist_names_are_unique_and_referenced_by_coordinator_prompt():
    from agent.subagents.knowledge_base_agent import knowledge_base_agent

    names = [database_query_agent["name"], internet_search_agent["name"], knowledge_base_agent["name"]]
    assert len(set(names)) == 3
    coordinator_prompt = prompts.main_agent_content["system_prompt"]
    for name in names:
        assert f'"{name}"' in coordinator_prompt, name


def test_specialists_map_modes_to_subagent_specs():
    from agent import main_agent
    from agent.subagents.knowledge_base_agent import knowledge_base_agent

    assert main_agent.SPECIALISTS == {
        "database": database_query_agent,
        "internet": internet_search_agent,
        "ragflow": knowledge_base_agent,
    }


def test_prompts_module_prints_every_agent_when_run_as_script(capsys):
    import runpy

    runpy.run_path(str(prompts.yaml_file_path.parents[1] / "agent" / "prompts.py"), run_name="__main__")
    out = capsys.readouterr().out
    assert "------Main Agent------" in out
    for key in ("gemini", "db", "ragflow"):
        assert f"------Sub Agent: {key}------" in out
        assert prompts.sub_agents_content[key]["name"] in out
