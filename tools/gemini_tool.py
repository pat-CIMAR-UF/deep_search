# 基于 Gemini 原生 Google Search 的联网搜索工具！
# A web search tool backed by Gemini's native Google Search grounding.
# ======================== 导入核心依赖 ========================
# 类型注解：增强代码提示和静态检查能力 / Type hints: better completion and static checking
from typing import Any

# LangChain 工具装饰器：将普通函数转为 Agent 可调用的工具 / LangChain decorator: turn a function into an Agent-callable tool
from langchain_core.tools import tool

# Gemini 官方客户端：generate_content + google_search 内置工具 / Official Gemini client: generate_content + built-in google_search tool
from google import genai
from google.genai import types

# 系统/第三方依赖 / System & third-party deps
import os  # 系统路径/环境变量处理 / Env var handling
import sys
from pathlib import Path
from threading import Lock
from dotenv import load_dotenv, find_dotenv # 加载 .env 文件中的环境变量 / Load environment variables from .env

# 直接以脚本方式运行时（python tools/gemini_tool.py），sys.path 里只有 tools/ 目录，
# 需要手动把项目根目录加进去，否则 import api / agent 会失败。
# When run as a script (python tools/gemini_tool.py) only tools/ is on sys.path,
# so add the project root manually, otherwise importing api / agent fails.
_PROJECT_ROOT = str(Path(__file__).parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# 自定义模块：工具调用埋点监控 / Custom module: tool-call monitoring
from api.context import get_run_metrics  # noqa: E402
from api.monitor import monitor  # noqa: E402  (必须在 sys.path 设置之后导入 / must come after the sys.path setup)

# ======================== 初始化配置 ========================
# 加载项目根目录的 .env 文件，读取环境变量（如 GEMINI_API_KEY）/ Load .env from the project root (e.g. GEMINI_API_KEY)
_=load_dotenv(find_dotenv())

# 默认模型，可通过 .env 中的 GEMINI_MODEL 覆盖 / Default model, overridable via GEMINI_MODEL in .env
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

# 客户端延迟初始化：避免没有配置 API Key 时，导入模块就直接报错
# Lazily initialised client: importing this module must not fail when the API key is missing
_client: genai.Client | None = None
_client_lock = Lock()


def _get_client() -> genai.Client:
    """Return the process-wide Gemini client (created on first use)."""
    global _client
    # Concurrent tools must retain one client; replacing it can close an in-flight request.
    with _client_lock:
        if _client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
            _client = genai.Client(api_key=api_key)
        return _client



# ======================== 定义一个网络搜索工具 ========================
@tool
def internet_search(
        query: str,
        max_results: int = 5,
) -> dict[str, Any]:
    """
    Collect web information based on the user's question, using Google Search grounded Gemini.
    Note: This tool is for public web search only. Do not use it for database or RAG queries.
    :param query: The user's search query
    :param max_results: Maximum number of grounding sources to return
    :return: A dict with the grounded answer, the queries Gemini actually ran, and the source list
    """
    # 每次调用工具，都会向前端推送调用进度！/ Every call pushes progress to the frontend
    # 参数1： 工具的名字  参数2： 就是调用工具的参数信息
    monitor.report_tool(tool_name="Internet Search Tool (Gemini)",
                        args={"query": query, "max_results": max_results})

    response = _get_client().models.generate_content(
        model=DEFAULT_MODEL,
        contents=query,
        config=types.GenerateContentConfig(
            # 这一行才是开启联网搜索的关键 / THIS IS WHAT ENABLES WEB SEARCH
            tools=[{"google_search": {}}],
        ),
    )

    # 评估运行时记录 Gemini 用量（与协调器模型分开计费）/ Record Gemini usage for evaluation runs (billed separately)
    metrics = get_run_metrics()
    usage = getattr(response, "usage_metadata", None)
    if metrics is not None and usage is not None:
        metrics.add_gemini_usage(getattr(usage, "prompt_token_count", 0), getattr(usage, "candidates_token_count", 0))

    # 解析溯源信息（可能为空，例如模型判断无需检索）/ Parse grounding metadata (may be absent when the model skips search)
    search_queries: list[str] = []
    sources: list[dict[str, str]] = []

    candidates = response.candidates or []
    metadata = candidates[0].grounding_metadata if candidates else None
    if metadata:
        search_queries = list(metadata.web_search_queries or [])
        for chunk in (metadata.grounding_chunks or []):
            if chunk.web:
                sources.append({"title": chunk.web.title or "", "url": chunk.web.uri or ""})
            if len(sources) >= max_results:
                break

    # 评估运行时记录出站查询与来源，供治理与引用检查使用 / Record the outbound query and sources for evaluation graders
    if metrics is not None:
        metrics.add_event("internet_search", query=query, search_queries=search_queries, sources=sources,
                          answer=(response.text or "")[:8000])

    # 返回结构化结果，方便子智能体引用来源 / Structured result so the sub-agent can cite its sources
    return {
        "query": query,
        "answer": response.text or "",
        "search_queries": search_queries,
        "sources": sources,
    }
