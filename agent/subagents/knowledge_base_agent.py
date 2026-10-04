from agent.prompts import sub_agents_content
from tools.ragflow_tools import ask_knowledge_base, list_knowledge_bases, retrieve_chunks

knowledge_base_agent = {
    "name": sub_agents_content['ragflow']['name'],
    "description": sub_agents_content['ragflow']['description'],
    "system_prompt": sub_agents_content['ragflow']['system_prompt'],
    "tools": [list_knowledge_bases, retrieve_chunks, ask_knowledge_base],
}
