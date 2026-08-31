from agent.prompts import sub_agents_content
from tools.gemini_tool import internet_search

internet_search_agent = {
    "name": sub_agents_content.get("internet_search_agent", {}).get("name", "Internet Search Agent"),
    "description": sub_agents_content.get("internet_search_agent", {}).get("description", "An agent that can search the internet for information"),
    "system_prompt": sub_agents_content.get("internet_search_agent", {}).get("system_prompt", "You are a helpful assistant that can search the internet for information"),
    "tools": [internet_search],
}
