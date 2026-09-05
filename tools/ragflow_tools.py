from pathlib import Path
import sys
_PROJECT_ROOT = str(Path(__file__).parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from api.monitor import monitor

#  get_assistant_list 获取聊天助手和知识库信息
#  create_ask_delete  创建提问和删除会话获取rag查询结果
from langchain_core.tools import tool
# 导入依赖
from ragflow_sdk import RAGFlow #链接rag服务的客户端
from ragflow.rag_config import _load_ragflow_env

# 创建一个ragflow的客户端
ragflow_client = None


def _get_client():
    """Initialize RAGFlow on first use so imports do not require credentials."""
    global ragflow_client
    if ragflow_client is None:
        api_key, base_url = _load_ragflow_env()
        if not api_key or not base_url:
            raise ValueError("Set RAGFLOW_API_KEY and RAGFLOW_API_URL before using RAGFlow tools.")
        ragflow_client = RAGFlow(api_key=api_key, base_url=base_url)
    return ragflow_client

# 1. 查询现在知识库中有哪些聊天助手和对应知识库的信息 （方便我们知道rag可以给我们提供哪些数据）
@tool
def get_assistant_list() -> str:
    """
    Query RAGFlow for available chat assistants and the knowledge bases bound to each one.
    The model should use this to decide which assistant can answer a given internal-document question.
    Important: before asking an assistant a question, call this tool first to get assistant names and details.
    Returns:
        assistants found — name, description, and associated knowledge bases
        none — No available assistants
        error — Failed to query assistant information; no assistants available
    :return:
    """

    # 埋点,调用工具了告诉前端哪个工具被调用了！！
    monitor.report_tool(tool_name="RAGFlow assistant list tool: get_assistant_list")

    # 1. 创建ragflow客户端
    try:
        # 2. ragflow客户端查询所有的聊天助手 page: int = 1, page_size: int = 30
        chat_list = _get_client().list_chats()
        if not chat_list:
            return "No available assistants"
        # 3. 查询聊天助手的知识库信息
        count_chat_info = "" #存储所有会话信息
        for chat in chat_list:
            dataset_names = []
            dataset_list = chat.datasets #当前聊天助手关联的知识库
            if dataset_list and isinstance(dataset_list,list):
                # 知识库的name
                for dataset in dataset_list:
                    # print(dataset)
                    dataset_names.append(dataset['name']) # 将一个助手的知识库的名字加入到列表中

            # 拼接下当前助手的信息 + 知识库信息
            # 法律资源小助手  xxxxxx  关联知识库：xx、xxx、xxx
            count_chat_info += f"assistant name:{chat.name}; description:{chat.description}; associated knowledge bases: {', '.join(dataset_names)} \n"
        return count_chat_info
    except Exception as e:
        return f"Failed to query assistant information; no assistants available. Error: {str(e)}"

# 2. 对某个助手进行提问（创建会话 -》 提问 -》 删除会话）
@tool
def create_ask_delete(chat_name: str, question: str) -> str:
    """
    Create a one-off session with an assistant, ask a question, then close the session.
    Use this to retrieve information from RAGFlow.
    Note: call get_assistant_list first to confirm the assistant name and the question to ask.
    :param chat_name: assistant name (get_assistant_list only exposes names to the LLM)
    :param question: the question to ask
    :return: the answer
    """
    # 埋点,调用工具了告诉前端哪个工具被调用了！！
    monitor.report_tool(tool_name="RAGFlow ask-assistant tool: create_ask_delete", args={"chat_name": chat_name, "question": question})
    # 1. 创建ragflow客户端
    # 2. 查询对应name的chat
    try:
        chats = _get_client().list_chats(name=chat_name)
        if not chats:
            return f"No assistant found with name: {chat_name}"
        use_chat = chats[0] #选中我们要使用的助手
        # 3. chat上创建一个会话
        session = use_chat.create_session(name="temp_session_ask")
        try:
            # 4. 使用会话进行提问
            # 返回的提问结果是流式
            response = session.ask(question = question,stream=True)
            # 接收总结果
            result = ""
            # 流的每一部分的对象 part
            for part in response:
                # 数据存在对象中content上！！
                # print(part.content)
                result = part.content
            # 5. 关闭提问的会话
            # chat -> 关闭 -》  session
        finally:
            use_chat.delete_sessions(ids=[session.id])
        # 6. 返回结果
        return result
    except Exception as e:
        return f"Question failed. Error: {str(e)}"

# if __name__ == '__main__':
#     # print(get_assistant_list())
#     print(create_ask_delete("空调安装助手", "空调的绝热工作怎么做！"))