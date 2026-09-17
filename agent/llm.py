from dotenv import load_dotenv, find_dotenv
import os
from pydantic import SecretStr
from langchain_openai import ChatOpenAI

_ = load_dotenv(find_dotenv())

class QwenChatOpenAI(ChatOpenAI):
    """Omit agent labels that this OpenAI-compatible endpoint rejects."""

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        for message in payload.get("messages", []):
            if message.get("role") != "tool":
                message.pop("name", None)
        return payload


llm = QwenChatOpenAI(
    model=os.getenv("QWEN_MODEL", "unsloth/Qwen3.8-27B-GGUF:UD-Q6_K_M"),
    base_url=os.environ["QWEN_REMOTE_BASE_URL"],
    api_key=SecretStr(os.environ["QWEN_REMOTE_API_KEY"]),
    timeout=120,
    max_retries=1,
    stream_usage=True,  # usage_metadata on streamed responses, consumed by agent.metrics
)
