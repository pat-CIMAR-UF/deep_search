import logging
from pathlib import Path

import markdown
from weasyprint import HTML


def convert_md_to_pdf(md_abs_path: Path, pdf_abs_path: Path) -> str:
    """
    使用 WeasyPrint 将 Markdown 转换为 PDF(跨平台,无需 Microsoft Word)。
    Convert Markdown to PDF via WeasyPrint (cross-platform, no Microsoft Word needed).
    依赖:weasyprint, markdown
    Dependencies: weasyprint, markdown
    """
    try:
        # 1. MD 转 HTML / Markdown → HTML
        md_content = md_abs_path.read_text(encoding='utf-8')

        html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: "Noto Sans CJK SC", "Microsoft YaHei", "SimHei", sans-serif; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid black; padding: 8px; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; white-space: pre-wrap; }}
                code {{ font-family: "Consolas", "Monaco", monospace; }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        # 2. HTML 转 PDF / HTML → PDF
        HTML(string=html_content).write_pdf(str(pdf_abs_path.resolve()))

        if pdf_abs_path.exists():
            return f"Converted successfully: {pdf_abs_path} (WeasyPrint engine)"
        else:
            return f"Conversion finished but file was not created: {pdf_abs_path}"

    except Exception as e:
        logging.error(f"Markdown-to-PDF conversion failed: {e}", exc_info=True)
        return f"Conversion failed: {str(e)}"
