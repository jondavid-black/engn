"""Workspace management for engn projects.

A workspace is a directory that contains an engn project (engn.jsonl).
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_workspace_root(start_path: Path | None = None) -> Path:
    """Get the workspace root directory.

    Args:
        start_path: Starting path to search from. Defaults to current directory.

    Returns:
        The workspace root path (directory containing engn.jsonl).
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # If the provided path itself is a workspace, return it
    if is_workspace(current):
        return current

    # Search up the directory tree for engn.jsonl
    while current != current.parent:
        if is_workspace(current):
            return current
        current = current.parent

    # If not found, return the start path as default
    return start_path.resolve()


def is_workspace(path: Path) -> bool:
    """Check if a directory is an engn workspace.

    Args:
        path: Path to check.

    Returns:
        True if the directory contains engn.jsonl.
    """
    return (path / "engn.jsonl").exists()


def is_git_repo(path: Path) -> bool:
    """Check if a directory is a git repository.

    Args:
        path: Path to check.

    Returns:
        True if the directory contains a .git folder.
    """
    return (path / ".git").exists() or (path / ".git").is_file()
