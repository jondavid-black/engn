"""Core engn functionality."""

from engn.core.workspace import (
    get_workspace_root,
    is_workspace,
    is_git_repo,
)

__all__ = [
    "get_workspace_root",
    "is_workspace",
    "is_git_repo",
]
