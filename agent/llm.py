"""Coordinator chat model on an OpenAI-compatible endpoint, selected by LLM_PROVIDER.

Providers:
- ``deepseek`` — DeepSeek API (https://api.deepseek.com); DEEPSEEK_API_KEY, optional DEEPSEEK_MODEL
  (default ``deepseek-flash``, served by DeepSeek-V4.1-Flash).
- ``qwen`` — a self-hosted OpenAI-compatible server; QWEN_REMOTE_BASE_URL, QWEN_REMOTE_API_KEY,
  optional QWEN_MODEL.
"""
from dotenv import load_dotenv, find_dotenv
import os
from pydantic import SecretStr
from langchain_openai import ChatOpenAI

_ = load_dotenv(find_dotenv())

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-flash"
DEFAULT_QWEN_MODEL = "unsloth/Qwen3.8-27B-GGUF:UD-Q6_K_M"


class CompatibleChatOpenAI(ChatOpenAI):
    """ChatOpenAI for any configured provider, minus agent labels some endpoints reject.

    DeepAgents tags assistant messages with ``name``; the self-hosted Qwen server rejects it.
    Tool messages keep their ``name`` and tool calls keep their IDs.
    """

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        for message in payload.get("messages", []):
            if message.get("role") != "tool":
                message.pop("name", None)
        return payload


def provider_settings(provider: str | None = None) -> dict:
    """Resolve model, base URL, and API key for the configured provider."""
    provider = (provider or os.getenv("LLM_PROVIDER", "qwen")).strip().lower()
    if provider == "deepseek":
        return {
            "provider": provider,
            "model": os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", DEEPSEEK_BASE_URL),
            "api_key": os.environ["DEEPSEEK_API_KEY"],
        }
    if provider == "qwen":
        return {
            "provider": provider,
            "model": os.getenv("QWEN_MODEL", DEFAULT_QWEN_MODEL),
            "base_url": os.environ["QWEN_REMOTE_BASE_URL"],
            "api_key": os.environ["QWEN_REMOTE_API_KEY"],
        }
    raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Use 'deepseek' or 'qwen'.")


def build_llm(provider: str | None = None) -> CompatibleChatOpenAI:
    settings = provider_settings(provider)
    return CompatibleChatOpenAI(
        model=settings["model"],
        base_url=settings["base_url"],
        api_key=SecretStr(settings["api_key"]),
        timeout=120,
        max_retries=1,
        stream_usage=True,  # usage_metadata on streamed responses, consumed by agent.metrics
    )


llm = build_llm()
