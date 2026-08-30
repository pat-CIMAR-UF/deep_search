from dotenv import load_dotenv, find_dotenv
import os
from pydantic import SecretStr
from langchain_openai import ChatOpenAI

_ = load_dotenv(find_dotenv())
'''
llm = ChatOpenAI(
    model="unsloth/Qwen3.8-27B-GGUF:UD-Q6_K_M",
    base_url="http://127.0.0.1:8888/v1",
    api_key=os.getenv("QWEN_API_KEY"),
)
'''
llm = ChatOpenAI(
    model="unsloth/Qwen3.8-27B-GGUF:UD-Q6_K_M",
    base_url=os.environ["QWEN_REMOTE_BASE_URL"],
    api_key=SecretStr(os.environ["QWEN_REMOTE_API_KEY"])
)
