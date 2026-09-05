"""A coordinator with exactly two specialist agents; no RAGFlow imports."""
from functools import lru_cache

from langchain.agents import create_agent
from langchain_core.tools import tool

from agent.prompts import main_agent_content
from agent.subagents.database_query_agent import database_query_agent
from agent.subagents.internet_search_agent import internet_search_agent
from api.monitor import monitor


def answer_text(result: dict) -> str:
    message = result["messages"][-1]
    content = message.content
    if isinstance(content, str):
        return content
    return "\n".join(block.get("text", "") for block in content if isinstance(block, dict))


@lru_cache(maxsize=1)
def build_agents():
    # Load model credentials only when a request actually needs the model.
    from agent.llm import llm

    specs = {"database": database_query_agent, "internet": internet_search_agent}
    agents = {
        key: create_agent(llm, tools=spec["tools"], system_prompt=spec["system_prompt"])
        for key, spec in specs.items()
    }

    @tool(description=database_query_agent["description"])
    async def query_database(query: str) -> str:
        monitor.report_assistant(database_query_agent["name"], {"query": query})
        result = await agents["database"].ainvoke(
            {"messages": [{"role": "user", "content": query}]}, {"recursion_limit": 30}
        )
        return answer_text(result)

    @tool(description=internet_search_agent["description"])
    async def search_internet(query: str) -> str:
        monitor.report_assistant(internet_search_agent["name"], {"query": query})
        result = await agents["internet"].ainvoke(
            {"messages": [{"role": "user", "content": query}]}, {"recursion_limit": 20}
        )
        return answer_text(result)

    agents["auto"] = create_agent(
        llm, tools=[query_database, search_internet],
        system_prompt=main_agent_content["system_prompt"],
    )
    return agents


async def run_agent(query: str, history: list[dict], mode: str = "auto") -> str:
    agent = build_agents()[mode]
    name = {"auto": "Research coordinator", "database": database_query_agent["name"],
            "internet": internet_search_agent["name"]}[mode]
    monitor.report_assistant(name, {"query": query[:500]})
    result = await agent.ainvoke(
        {"messages": [*history[-40:], {"role": "user", "content": query}]},
        {"recursion_limit": 40},
    )
    answer = answer_text(result).strip()
    if not answer:
        raise RuntimeError("The model returned an empty answer. Please try again.")
    return answer
