"""Core engn functionality."""

from engn.core.workspace import (
    get_workspace_root,
    is_workspace,
    is_git_repo,
    get_managed_project_dirs,
    add_project_to_gitignore,
    remove_project_from_gitignore,
    sync_projects_to_gitignore,
    ensure_project_ignored,
)
from engn.core.context import AppContext, get_app_context

__all__ = [
    "get_workspace_root",
    "is_workspace",
    "is_git_repo",
    "get_managed_project_dirs",
    "add_project_to_gitignore",
    "remove_project_from_gitignore",
    "sync_projects_to_gitignore",
    "ensure_project_ignored",
    "AppContext",
    "get_app_context",
]
