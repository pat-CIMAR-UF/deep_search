"""Regression tests for local file tools and the RAGFlow knowledge-base tools."""
import ast
import io
from pathlib import Path
import re
import sys
import tempfile
import tokenize
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

_PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from api.context import set_session_context, reset_session_context
from tools import markdown_tools, pdf_tools, ragflow_tools, upload_file_read_tool


class FileToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.root = Path(self.temp.name).resolve()
        self.token = set_session_context(str(self.root))

    def tearDown(self):
        reset_session_context(self.token)
        self.temp.cleanup()

    def test_markdown_round_trip(self):
        result = markdown_tools.generate_markdown.invoke(
            {"content": "# Example\nHello", "filename": "report", "path": "nested"}
        )
        self.assertIn("generated and saved successfully", result)
        self.assertEqual(upload_file_read_tool.read_file_content.invoke(
            {"filename": "nested/report.md"}), "# Example\nHello")

    def test_missing_files(self):
        for tool, args in [
            (pdf_tools.convert_md_to_pdf, {"md_filename": "missing.md"}),
            (upload_file_read_tool.read_file_content, {"filename": "missing.md"}),
        ]:
            self.assertIn("does not exist", tool.invoke(args))

    def test_pdf_conversion_creates_output_directory(self):
        (self.root / "report.md").write_text("# Example\n\nA PDF report.", encoding="utf-8")
        result = pdf_tools.convert_md_to_pdf.invoke(
            {"md_filename": "report.md", "pdf_filename": "nested/report.pdf"}
        )
        self.assertIn("Converted successfully", result)
        self.assertTrue((self.root / "nested/report.pdf").read_bytes().startswith(b"%PDF-"))

    def test_missing_optional_reader_dependency(self):
        (self.root / "report.pdf").touch()
        with patch.object(upload_file_read_tool, "pypdf", None):
            self.assertIn("install 'pypdf'", upload_file_read_tool.read_file_content.invoke(
                {"filename": "report.pdf"}))


class RagflowToolsTests(unittest.TestCase):
    """Knowledge-base tools over an in-memory RAGFlow client (tests/ragflow_fakes.py)."""

    def setUp(self):
        from tests.ragflow_fakes import FakeChat, FakeClient, completion
        self.FakeChat, self.FakeClient, self.completion = FakeChat, FakeClient, completion
        self.handbook = {"id": "ds-handbook", "name": "handbook", "document_count": 4, "chunk_count": 103,
                         "embedding_model": "emb"}

    def test_sdk_network_calls_have_timeouts(self):
        from ragflow import service
        client = service.RAGFlowClient(api_key="test-key", base_url="http://ragflow.test")
        with patch.object(service.requests, "request") as request:
            client.get("/datasets")
            client.post("/chat/completions", json={"chat_id": "id"})
            client.delete("/chats/id/sessions", json={"ids": ["temporary"]})
            client.put("/datasets/id", json={"name": "x"})
            client.patch("/datasets/id/documents/d", json={"chunk_method": "naive"})
        self.assertEqual(request.call_count, 5)
        for call in request.call_args_list:
            self.assertEqual(call.kwargs["timeout"], (10, 120))

    def test_knowledge_base_listing_names_linked_assistants(self):
        client = self.FakeClient(datasets=[self.handbook], chats=[self.FakeChat("test", ["ds-handbook"])])
        with patch.object(ragflow_tools, "ragflow_client", client):
            result = ragflow_tools.list_knowledge_bases.invoke({})
        self.assertIn("knowledge base: handbook;", result)
        self.assertIn("assistants: test", result)
        self.assertNotIn("Failed", result)

    def test_missing_configuration_is_reported_on_use(self):
        with patch.object(ragflow_tools, "ragflow_client", None), patch.dict(
            "os.environ", {"RAGFLOW_API_KEY": ""}
        ):
            self.assertIn("RAGFLOW_API_KEY is not set", ragflow_tools.list_knowledge_bases.invoke({}))

    def test_unknown_knowledge_base(self):
        client = self.FakeClient(datasets=[self.handbook])
        with patch.object(ragflow_tools, "ragflow_client", client):
            self.assertEqual(ragflow_tools.ask_knowledge_base.invoke(
                {"knowledge_bases": "missing", "question": "Hello"}),
                "Question failed: Knowledge base not found: missing. Available: handbook")

    def test_session_cleanup_on_success_and_completion_failure(self):
        for fail in [False, True]:
            with self.subTest(fail=fail):
                chat = self.FakeChat("test", ["ds-handbook"])
                payload = RuntimeError("completion interrupted") if fail else self.completion("First and final", [])
                client = self.FakeClient(datasets=[self.handbook], chats=[chat], completion=payload)
                with patch.object(ragflow_tools, "ragflow_client", client):
                    result = ragflow_tools.ask_knowledge_base.invoke(
                        {"knowledge_bases": "handbook", "question": "Hello"})
                self.assertEqual(chat.deleted, [["session-1"]])
                self.assertIn("completion interrupted" if fail else "First and final", result)

    def test_cited_sources_follow_id_markers(self):
        chunks = [{"id": "c1", "document_name": "Midea U AC Installation Guide.pdf", "content": "MAW08V1QWT"},
                  {"id": "c1", "document_name": "Midea U AC Installation Guide.pdf", "content": "MAW08V1QWT"}]
        chat = self.FakeChat("test", ["ds-handbook"])
        client = self.FakeClient(datasets=[self.handbook], chats=[chat], completion=self.completion("MAW08V1QWT [ID:0]", chunks))
        with patch.object(ragflow_tools, "ragflow_client", client):
            result = ragflow_tools.ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Models?"})
        self.assertEqual(result, 'MAW08V1QWT [ID:0]\n\nSources:\n[ID:0] Midea U AC Installation Guide.pdf — "MAW08V1QWT"')
        self.assertEqual(chat.deleted, [["session-1"]])

    def test_empty_answer_reports_failure_and_cleans_up(self):
        chat = self.FakeChat("test", ["ds-handbook"])
        client = self.FakeClient(datasets=[self.handbook], chats=[chat], completion=self.completion("", []))
        with patch.object(ragflow_tools, "ragflow_client", client):
            result = ragflow_tools.ask_knowledge_base.invoke({"knowledge_bases": "handbook", "question": "Models?"})
        self.assertEqual(result, "Question failed: RAGFlow returned an empty answer.")
        self.assertEqual(chat.deleted, [["session-1"]])


class SourceTests(unittest.TestCase):
    def test_no_chinese_outside_comments(self):
        for path in Path(__file__).parent.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(path))
            for token in tokenize.generate_tokens(io.StringIO(source).readline):
                if token.type != tokenize.COMMENT:
                    self.assertIsNone(re.search(r"[\u3400-\u9fff]", token.string),
                                      f"{path}:{token.start[0]}")


class DocumentReaderTests(unittest.TestCase):
    def test_word_pdf_and_excel_content(self):
        from docx import Document
        import pandas as pd
        from api.context import set_session_context, reset_session_context
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            token = set_session_context(temporary)
            try:
                doc = Document()
                doc.add_paragraph("A document reference")
                doc.save(root / "input.docx")
                pd.DataFrame({"region": ["East", "West"], "sales": [42, 18]}).to_excel(root / "input.xlsx", index=False)
                (root / "input.md").write_text("# PDF reference", encoding="utf-8")
                pdf_tools.convert_md_to_pdf.invoke({"md_filename": "input.md"})
                for name, expected in [("input.docx", "document reference"), ("input.xlsx", "East"), ("input.pdf", "PDF reference")]:
                    with self.subTest(name=name):
                        self.assertIn(expected, upload_file_read_tool.read_file_content.invoke({"filename": name}))
            finally:
                reset_session_context(token)

    def test_session_path_rejects_other_sessions_and_hidden_state(self):
        from tools.session_paths import resolve_path
        with tempfile.TemporaryDirectory() as temporary:
            for name in ["../other/report.txt", ".state.json", "/etc/passwd"]:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    resolve_path(name, temporary)


if __name__ == "__main__":
    unittest.main()
