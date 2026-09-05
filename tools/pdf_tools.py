import logging
import sys
from pathlib import Path

try:
    from typing import Annotated, Optional
except ImportError:
    from typing_extensions import Annotated, Optional

from langchain_core.tools import tool
_PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from api.monitor import monitor
from api.context import get_session_context
from utils.path_utils import resolve_path


@tool
def convert_md_to_pdf(
        md_filename: Annotated[str, "Path to the source Markdown document (including .md)"],
        pdf_filename: Annotated[Optional[str], "Output PDF path (optional; defaults to the source filename with .pdf)"] = None
) -> str:
    """
    Convert a Markdown document to PDF using WeasyPrint.
    Resolve session paths and delegate rendering to the PDF converter.
    """
    monitor.report_tool("Markdown-to-PDF tool")

    try:
        # 1. 路径预处理
        session_dir = get_session_context()
        md_path = Path(md_filename).with_suffix('.md')
        md_abs_path = Path(resolve_path(str(md_path), session_dir))

        # 2. 检查源文件
        if not md_abs_path.exists():
            return f"Error: file does not exist: {md_abs_path}"

        # 3. 确定输出路径
        if pdf_filename:
            pdf_path = Path(pdf_filename).with_suffix('.pdf')
            pdf_abs_path = Path(resolve_path(str(pdf_path), session_dir))
        else:
            pdf_abs_path = md_abs_path.with_suffix('.pdf')

        # 4. 调用核心转换逻辑
        from utils.word_converter import convert_md_to_pdf as render_pdf

        pdf_abs_path.parent.mkdir(parents=True, exist_ok=True)
        return render_pdf(md_abs_path, pdf_abs_path)

    except Exception as e:
        logging.error(f"Conversion failed: {e}", exc_info=True)
        return f"Conversion failed: {str(e)}"


if __name__ == '__main__':
    # 测试代码
    # 强制覆盖当前模块中的 get_session_context
    get_session_context = lambda: "./test_session_123"

    # 创建测试文件
    Path("./test_session_123/sub_dir").mkdir(parents=True, exist_ok=True)
    with open("./test_session_123/sub_dir/test_file.md", "w", encoding="utf-8") as f:
        f.write("# Heading\n\nTest content\n\n|A|B|\n|---|---|\n|1|2|")

    print(convert_md_to_pdf.invoke({"md_filename": "sub_dir/test_file.md"}))