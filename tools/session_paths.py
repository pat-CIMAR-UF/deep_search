"""Resolve tool paths while keeping API requests inside their session directory."""
from pathlib import Path

from utils.path_utils import resolve_path as _resolve_path


def resolve_path(filename: str, session_dir: str | None = None) -> str:
    resolved = Path(_resolve_path(filename, session_dir)).resolve()
    if session_dir:
        root = Path(session_dir).resolve()
        if not resolved.is_relative_to(root) or any(
            part.startswith('.') for part in resolved.relative_to(root).parts
        ):
            raise ValueError("Only this conversation's non-hidden files are accessible.")
    return str(resolved)
