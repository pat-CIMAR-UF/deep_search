"""Regression tests for local file tools and RAGFlow session lifecycle."""
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
    def test_sdk_network_calls_have_timeouts(self):
        client = ragflow_tools._RAGFlowClient(api_key="test-key", base_url="http://ragflow.test")
        with patch.object(ragflow_tools.requests, "request") as request:
            client.get("/chats")
            client.post("/chats/id/sessions", json={"name": "temporary"})
            client.delete("/chats/id/sessions", json={"ids": ["temporary"]})
        self.assertEqual(request.call_count, 3)
        for call in request.call_args_list:
            self.assertEqual(call.kwargs["timeout"], (10, 120))

    def test_assistant_discovery_supports_current_and_legacy_metadata(self):
        from ragflow_sdk.modules.chat import Chat
        client = Mock()
        client.list_chats.return_value = [
            Chat(client, {"name": "Drug Labels Assistant", "dataset_ids": ["drug-id"],
                          "kb_names": ["Drug Labels"], "description": "Drug documents"}),
            Chat(client, {"name": "Crib Assembly Assistant", "datasets": [{"name": "Crib Assembly"}]}),
        ]
        with patch.object(ragflow_tools, "ragflow_client", client):
            result = ragflow_tools.get_assistant_list.invoke({})
        self.assertIn("assistant name:Drug Labels Assistant", result)
        self.assertIn("associated knowledge bases: Drug Labels", result)
        self.assertIn("associated knowledge bases: Crib Assembly", result)
        self.assertNotIn("Failed", result)

    def test_missing_configuration_is_reported_on_use(self):
        with patch.object(ragflow_tools, "ragflow_client", None), patch.object(
            ragflow_tools, "_load_ragflow_env", return_value=(None, None)
        ):
            self.assertIn("Set RAGFLOW_API_KEY", ragflow_tools.get_assistant_list.invoke({}))

    def test_unknown_assistant(self):
        client = Mock()
        client.list_chats.return_value = []
        with patch.object(ragflow_tools, "ragflow_client", client):
            self.assertEqual(ragflow_tools.create_ask_delete.invoke(
                {"chat_name": "missing", "question": "Hello"}),
                "No assistant found with name: missing")

    def test_session_cleanup_on_success_and_stream_failure(self):
        for fail in [False, True]:
            with self.subTest(fail=fail):
                session = Mock(id="session-id")
                def response():
                    yield SimpleNamespace(content="First")
                    if fail:
                        raise RuntimeError("stream interrupted")
                    yield SimpleNamespace(content=" and final")
                session.ask.return_value = response()
                chat = Mock()
                chat.create_session.return_value = session
                client = Mock()
                client.list_chats.return_value = [chat]
                with patch.object(ragflow_tools, "ragflow_client", client):
                    result = ragflow_tools.create_ask_delete.invoke(
                        {"chat_name": "Example", "question": "Hello"})
                chat.delete_sessions.assert_called_once_with(ids=["session-id"])
                self.assertIn("stream interrupted" if fail else "First and final", result)

    def test_delta_stream_retains_answer_when_final_event_only_has_sources(self):
        from ragflow_sdk.modules.session import Message
        client = Mock()
        session = Mock(id="delta-session")
        session.ask.return_value = iter([
            Message(client, {"content": "MAW08"}),
            Message(client, {"content": "V1QWT"}),
            Message(client, {"content": "", "reference": [
                {"document_name": "Midea U AC Installation Guide.pdf"},
                {"document_name": "Midea U AC Installation Guide.pdf"},
            ]}),
        ])
        chat = Mock()
        chat.create_session.return_value = session
        client.list_chats.return_value = [chat]
        with patch.object(ragflow_tools, "ragflow_client", client):
            result = ragflow_tools.create_ask_delete.invoke({"chat_name": "AC", "question": "Models?"})
        self.assertEqual(result, "MAW08V1QWT\n\nSources:\n- Midea U AC Installation Guide.pdf")
        chat.delete_sessions.assert_called_once_with(ids=["delta-session"])

    def test_empty_stream_reports_failure_and_cleans_up(self):
        client = Mock()
        session = Mock(id="empty-session")
        session.ask.return_value = iter([])
        chat = Mock()
        chat.create_session.return_value = session
        client.list_chats.return_value = [chat]
        with patch.object(ragflow_tools, "ragflow_client", client):
            result = ragflow_tools.create_ask_delete.invoke({"chat_name": "AC", "question": "Models?"})
        self.assertIn("Question failed", result)
        chat.delete_sessions.assert_called_once_with(ids=["empty-session"])


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
