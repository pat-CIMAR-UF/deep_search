from agent.prompts import sub_agents_content
from tools.mongo_tools import (aggregate_documents, count_documents, find_documents,
                               get_collection_schema, list_collections)

database_query_agent = {
    "name": sub_agents_content["db"]["name"],
    "description": sub_agents_content["db"]["description"],
    "system_prompt": sub_agents_content["db"]["system_prompt"],
    "tools": [list_collections, get_collection_schema, find_documents, aggregate_documents, count_documents],
}
