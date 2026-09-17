"""Tests for utils/path_utils.py and the session-confining wrapper in tools/session_paths.py."""
from types import SimpleNamespace

import pytest

import utils.path_utils as path_utils
from tools.session_paths import resolve_path as safe_resolve_path
from utils.path_utils import resolve_path


@pytest.fixture
def session(tmp_path):
    directory = tmp_path / "output" / "session_abc"
    directory.mkdir(parents=True)
    return directory.resolve()


# ------------------------------------------------------- relative paths --
def test_relative_path_joins_session_dir(session):
    assert resolve_path("sub1/sub2/test.md", str(session)) == str(session / "sub1" / "sub2" / "test.md")
    assert resolve_path("report.md", str(session)) == str(session / "report.md")


def test_relative_path_containing_session_name_is_flattened(session):
    assert resolve_path("session_abc/report.md", str(session)) == str(session / "report.md")
    assert resolve_path("output/session_abc/sub/report.md", str(session)) == str(session / "report.md")


def test_relative_output_prefix_is_flattened(session):
    assert resolve_path("output/report.md", str(session)) == str(session / "report.md")


def test_without_session_dir_resolves_against_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    expected = str((tmp_path / "sub" / "test.md").resolve())
    assert resolve_path("sub/test.md") == expected
    assert resolve_path("sub/test.md", None) == expected


# -------------------------------------------------------- virtual paths --
@pytest.mark.parametrize("prefix", ["/workspace", "/mnt/data", "/home/user"])
def test_virtual_prefixes_are_stripped(session, prefix):
    assert resolve_path(f"{prefix}/report.md", str(session)) == str(session / "report.md")
    assert resolve_path(f"{prefix}/sub/report.md", str(session)) == str(session / "sub" / "report.md")


def test_windows_separators_are_normalized_before_prefix_matching(session):
    assert resolve_path("\\workspace\\report.md", str(session)) == str(session / "report.md")


def test_updated_paths_resolve_relative_to_cwd(session, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    expected = str((tmp_path / "updated" / "upload" / "file.pdf").resolve())
    assert resolve_path("abc/updated/upload/file.pdf", str(session)) == expected
    assert resolve_path("/mnt/data/updated/doc.md", str(session)) == str((tmp_path / "updated" / "doc.md").resolve())
    assert resolve_path("updated\\doc.md", str(session)) == str((tmp_path / "updated" / "doc.md").resolve())


# -------------------------------------------------------- absolute paths --
def test_absolute_path_inside_session_is_kept(session):
    target = session / "sub" / "report.md"
    assert resolve_path(str(target), str(session)) == str(target)
    assert resolve_path(str(session), str(session)) == str(session)


def test_absolute_path_outside_session_is_preserved(session, tmp_path):
    other = (tmp_path / "other" / "file.md").resolve()
    assert resolve_path(str(other), str(session)) == str(other)
    assert resolve_path("/etc/passwd", str(session)) == "/etc/passwd"


def test_nested_session_directory_is_collapsed(session):
    nested = session / "session_abc" / "report.md"
    assert resolve_path(str(nested), str(session)) == str(session / "report.md")


def test_unix_style_absolute_path_on_windows_joins_session(session, monkeypatch):
    """On Windows a leading slash without a drive letter is treated as session-relative."""
    monkeypatch.setattr(path_utils, "os", SimpleNamespace(name="nt"))
    assert resolve_path("/sub/test.md", str(session)) == str(session / "sub" / "test.md")


# ------------------------------------------------------ session_paths guard --
def test_safe_resolve_allows_files_inside_the_session(session):
    assert safe_resolve_path("sub/report.md", str(session)) == str(session / "sub" / "report.md")
    assert safe_resolve_path("./report.md", str(session)) == str(session / "report.md")
    assert safe_resolve_path("sub/../report.md", str(session)) == str(session / "report.md")
    assert safe_resolve_path(str(session / "report.md"), str(session)) == str(session / "report.md")
    assert safe_resolve_path("/workspace/report.md", str(session)) == str(session / "report.md")


@pytest.mark.parametrize("name", [
    "../other/report.txt",
    "../../secret.txt",
    ".state.json",
    "sub/.hidden/notes.md",
    "/etc/passwd",
    "updated/file.pdf",
])
def test_safe_resolve_rejects_escapes_and_hidden_files(session, name, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="Only this conversation's non-hidden files"):
        safe_resolve_path(name, str(session))


def test_safe_resolve_without_session_passes_through(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert safe_resolve_path("../anything.md", None) == str((tmp_path / ".." / "anything.md").resolve())
