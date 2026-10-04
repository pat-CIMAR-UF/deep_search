import logging
import sys
from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
_PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from api.monitor import monitor
from api.context import get_session_context
from tools.session_paths import resolve_path


# Markdown生成工具
@tool
def generate_markdown(
        content: Annotated[str, "Text content to write to the Markdown document"],
        filename: Annotated[str, "Markdown filename, with or without the .md extension"],
        path: Annotated[str, "Destination directory (absolute or relative to the session directory)"] = ""
):
    """Generate a Markdown (.md) file from the supplied text."""
    monitor.report_tool("Markdown generation tool", {"content": content})
    if not filename.endswith('.md'):
        filename += '.md'

    # 获取上下文中的会话目录
    session_dir = get_session_context()

    # --- 路径清洗与重定向逻辑 ---
    # 结合 path 和 filename
    if path and path != ".":
        # 使用 Path 拼接，再转为字符串传给 resolve_path
        full_input_path = str(Path(path) / filename)
    else:
        full_input_path = filename
    full_path_str = resolve_path(full_input_path, session_dir)
    file_path = Path(full_path_str)

    try:
        # 确保目录存在 / Make sure the directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # 使用 Path 直接写入文本
        file_path.write_text(content, encoding='utf-8')
        return f"Markdown file '{file_path}' generated and saved successfully."
    except Exception as e:
        logging.error(f"Markdown generation failed: {e}", exc_info=True)
        return f"Failed to generate Markdown file: {str(e)}"


# -------------------------- 测试代码（仅修改这里，给session_dir配置固定值） --------------------------
if __name__ == "__main__":
    # ========== 核心：覆盖get_session_context的返回值（仅测试时生效） ==========
    # 不用Mock，直接重新定义这个函数，给session_dir赋值！
    def get_session_context():
        """Return a fixed session directory for the demo."""
        return "./test_session_123"  # 你要的session_dir初始化值，随便改

    # ========== 极简测试逻辑（只传path/filename，session_dir已初始化） ==========
    test_content = "# Test document\nTest content using a fixed session directory"
    test_filename = "test_file"  # 无.md后缀，测试自动补全
    test_path = "sub_dir"       # 相对路径

    # 调用生成函数
    print("===== Starting test (session directory: ./test_session_123) =====")
    result = generate_markdown.invoke({
        "content": test_content,
        "filename": test_filename,
        "path": test_path
    })

    # 验证结果
    print(f"\nTool result: {result}")
    if "generated and saved successfully" in result:
        file_path = Path(result.split("'")[1])
        print(f"File check: {file_path} {'exists' if file_path.exists() else 'missing'}")