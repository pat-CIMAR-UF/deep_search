# 定义一个网络搜索的工具！
# ======================== 导入核心依赖 ========================
# 类型注解：增强代码提示和静态检查能力
from typing import  Literal
# LangChain 工具装饰器：将普通函数转为 Agent 可调用的工具
from langchain_core.tools import tool
# Tavily 官方客户端：实现网络搜索核心功能
from tavily import TavilyClient

# 系统/第三方依赖
import os  # 系统路径/环境变量处理
import sys
from pathlib import Path
from dotenv import load_dotenv  # 加载 .env 文件中的环境变量

# 直接以脚本方式运行时（python tools/tavily_tool.py），sys.path 里只有 tools/ 目录，
# 需要手动把项目根目录加进去，否则 import api / agent 会失败。
_PROJECT_ROOT = str(Path(__file__).parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# 自定义模块：工具调用埋点监控
from api.monitor import monitor  # noqa: E402  (必须在 sys.path 设置之后导入)

# ======================== 初始化配置 ========================
# 加载项目根目录的 .env 文件，读取环境变量（如 TAVILY_API_KEY）
load_dotenv()


# 步骤1： 定义一个TavilyClient对象
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# 步骤2： 定义一个网络搜索工具
@tool
def internet_search(
        query: str,
        topic: Literal[ "news",  "finance",  "general"] = "general",
        max_results: int = 5,
        include_raw_content: bool = False
):
    """
    Collect web information based on the user's question.
    Note: This tool is for public web search only. Do not use it for database or RAG queries.
    :param query: The user's search query
    :param topic: The type of search
    :param max_results: Maximum number of results to return
    :param include_raw_content: Whether to return raw content. False = concise, True = detailed
    :return:
    """
    # 每次调用工具，都都会向前端推进调用进度！
    # 参数1： 工具的名字  参数2： 就是调用工具的参数信息
    monitor.report_tool(tool_name="Internet Search Tool",
                        args={"query": query, "topic": topic, "max_results": max_results,
                              "include_raw_content": include_raw_content})

    return tavily_client.search(query = query, topic =  topic,
                                max_results = max_results, include_raw_content = include_raw_content)
