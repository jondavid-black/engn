"""Workspace management for engn projects.

A workspace is a directory that serves as the root for engn configuration
and projects. The workspace directory should be a git repository.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

GITIGNORE_FILE = ".gitignore"
GITIGNORE_HEADER = "# engn managed project directories"
GITIGNORE_FOOTER = "# end engn managed"


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

    # Search up the directory tree for engn.jsonl
    while current != current.parent:
        if (current / "engn.jsonl").exists():
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


def _read_gitignore(workspace_path: Path) -> list[str]:
    """Read the .gitignore file contents.

    Args:
        workspace_path: Path to the workspace root.

    Returns:
        List of lines in the .gitignore file.
    """
    gitignore_path = workspace_path / GITIGNORE_FILE
    if not gitignore_path.exists():
        return []

    with gitignore_path.open("r", encoding="utf-8") as f:
        return f.readlines()


def _write_gitignore(workspace_path: Path, lines: list[str]) -> None:
    """Write the .gitignore file contents.

    Args:
        workspace_path: Path to the workspace root.
        lines: Lines to write to the file.
    """
    gitignore_path = workspace_path / GITIGNORE_FILE
    with gitignore_path.open("w", encoding="utf-8") as f:
        f.writelines(lines)


def _get_managed_section_indices(lines: list[str]) -> tuple[int, int] | None:
    """Find the start and end indices of the engn-managed section.

    Args:
        lines: Lines from the .gitignore file.

    Returns:
        Tuple of (start_index, end_index) or None if section not found.
    """
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == GITIGNORE_HEADER:
            start_idx = i
        elif stripped == GITIGNORE_FOOTER and start_idx is not None:
            end_idx = i
            break

    if start_idx is not None and end_idx is not None:
        return (start_idx, end_idx)
    return None


def get_managed_project_dirs(workspace_path: Path) -> list[str]:
    """Get the list of project directories managed by engn in .gitignore.

    Args:
        workspace_path: Path to the workspace root.

    Returns:
        List of project directory paths (relative to workspace).
    """
    lines = _read_gitignore(workspace_path)
    indices = _get_managed_section_indices(lines)

    if indices is None:
        return []

    start_idx, end_idx = indices
    project_dirs = []

    for i in range(start_idx + 1, end_idx):
        line = lines[i].strip()
        if line and not line.startswith("#"):
            # Remove trailing slash if present
            project_dirs.append(line.rstrip("/"))

    return project_dirs


def add_project_to_gitignore(workspace_path: Path, project_dir: str) -> bool:
    """Add a project directory to the .gitignore managed section.

    Args:
        workspace_path: Path to the workspace root.
        project_dir: Relative path to the project directory.

    Returns:
        True if the directory was added, False if already present.
    """
    # Normalize the path
    project_dir = project_dir.strip().rstrip("/")
    if not project_dir:
        return False

    lines = _read_gitignore(workspace_path)
    indices = _get_managed_section_indices(lines)

    # Get current managed dirs
    current_dirs = get_managed_project_dirs(workspace_path)
    if project_dir in current_dirs:
        logger.debug(f"Project directory '{project_dir}' already in .gitignore")
        return False

    if indices is None:
        # Create the managed section
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        if lines:
            lines.append("\n")
        lines.append(f"{GITIGNORE_HEADER}\n")
        lines.append(f"{project_dir}/\n")
        lines.append(f"{GITIGNORE_FOOTER}\n")
    else:
        # Insert before the footer
        start_idx, end_idx = indices
        lines.insert(end_idx, f"{project_dir}/\n")

    _write_gitignore(workspace_path, lines)
    logger.info(f"Added '{project_dir}' to .gitignore")
    return True


def remove_project_from_gitignore(workspace_path: Path, project_dir: str) -> bool:
    """Remove a project directory from the .gitignore managed section.

    Args:
        workspace_path: Path to the workspace root.
        project_dir: Relative path to the project directory.

    Returns:
        True if the directory was removed, False if not found.
    """
    project_dir = project_dir.strip().rstrip("/")
    if not project_dir:
        return False

    lines = _read_gitignore(workspace_path)
    indices = _get_managed_section_indices(lines)

    if indices is None:
        return False

    start_idx, end_idx = indices
    removed = False
    new_lines = []

    for i, line in enumerate(lines):
        if start_idx < i < end_idx:
            stripped = line.strip().rstrip("/")
            if stripped == project_dir:
                removed = True
                continue
        new_lines.append(line)

    if removed:
        _write_gitignore(workspace_path, new_lines)
        logger.info(f"Removed '{project_dir}' from .gitignore")

    return removed


def sync_projects_to_gitignore(workspace_path: Path, project_dirs: list[str]) -> None:
    """Sync the list of project directories to the .gitignore managed section.

    This replaces the entire managed section with the provided list.

    Args:
        workspace_path: Path to the workspace root.
        project_dirs: List of project directory paths (relative to workspace).
    """
    lines = _read_gitignore(workspace_path)
    indices = _get_managed_section_indices(lines)

    # Build new managed section
    managed_lines = [f"{GITIGNORE_HEADER}\n"]
    for project_dir in sorted(set(project_dirs)):
        project_dir = project_dir.strip().rstrip("/")
        if project_dir:
            managed_lines.append(f"{project_dir}/\n")
    managed_lines.append(f"{GITIGNORE_FOOTER}\n")

    if indices is None:
        # Append new section
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
        if lines:
            lines.append("\n")
        lines.extend(managed_lines)
    else:
        # Replace existing section
        start_idx, end_idx = indices
        lines = lines[:start_idx] + managed_lines + lines[end_idx + 1 :]

    _write_gitignore(workspace_path, lines)
    logger.info(f"Synced {len(project_dirs)} project directories to .gitignore")


def ensure_project_ignored(workspace_path: Path, project_path: Path) -> None:
    """Ensure a project directory is added to .gitignore.

    This is a convenience function to be called when a project is created
    or discovered in the workspace.

    Args:
        workspace_path: Path to the workspace root.
        project_path: Absolute or relative path to the project directory.
    """
    # Convert to relative path if absolute
    if project_path.is_absolute():
        try:
            project_dir = str(project_path.relative_to(workspace_path))
        except ValueError:
            # Project is outside workspace, don't add to gitignore
            logger.warning(
                f"Project '{project_path}' is outside workspace, not adding to .gitignore"
            )
            return
    else:
        project_dir = str(project_path)

    add_project_to_gitignore(workspace_path, project_dir)
