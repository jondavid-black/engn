import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from engn.core.workspace import (
    get_workspace_root,
    ensure_project_ignored,
    remove_project_from_gitignore,
)


def init_project_structure(target_path: Path) -> None:
    """
    Initialize an existing directory with engn and beads structures.
    This is reusable by 'new', 'clone', and 'init' commands.
    """
    if not target_path.exists():
        target_path.mkdir(parents=True)

    # Create standard engn directories
    for dir_name in ["arch", "pm", "ux"]:
        (target_path / dir_name).mkdir(exist_ok=True)

    # Create engn.jsonl if it doesn't exist
    config_path = target_path / "engn.jsonl"
    if not config_path.exists():
        import json

        with open(config_path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "engn_type": "type_def",
                        "name": "ProjectConfig",
                        "properties": [
                            {"name": "pm_path", "type": "str", "default": "pm"},
                            {"name": "sysengn_path", "type": "str", "default": "arch"},
                            {"name": "ux_path", "type": "str", "default": "ux"},
                        ],
                    }
                )
                + "\n"
            )
            f.write(
                json.dumps(
                    {
                        "engn_type": "ProjectConfig",
                        "pm_path": "pm",
                        "sysengn_path": "arch",
                        "ux_path": "ux",
                    }
                )
                + "\n"
            )

    # Initialize beads (bd) if installed and not already present
    if shutil.which("bd"):
        if not (target_path / ".beads").exists():
            try:
                subprocess.run(["bd", "init"], cwd=target_path, check=True)
                print("Initialized beads for issue tracking")
            except subprocess.CalledProcessError:
                # If bd init fails (e.g. already initialized but .beads missing or other issues)
                # we just continue as it's a "best effort" in this function
                pass
    else:
        print("Warning: 'bd' (beads) not found. Issue tracking not initialized.")


def create_new_project(name: str, working_dir: Path) -> Path:
    """Create a new project from scratch."""
    project_path = working_dir / name
    if project_path.exists():
        raise FileExistsError(
            f"Project directory '{name}' already exists at {project_path}"
        )

    project_path.mkdir(parents=True)

    # Initialize git
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=project_path, check=True, capture_output=True
    )

    # Initialize engn and beads
    init_project_structure(project_path)

    # Ensure project is ignored in workspace
    workspace_root = get_workspace_root(working_dir)
    ensure_project_ignored(workspace_root, project_path)

    # Establish initial commit
    subprocess.run(
        ["git", "add", "."],
        cwd=project_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )

    return project_path


def clone_project(url: str, working_dir: Path, name: Optional[str] = None) -> Path:
    """Clone an existing project from a git URL."""
    if not name:
        # Simple name extraction from URL
        name = url.rstrip("/").split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]

    project_path = working_dir / name
    if project_path.exists():
        raise FileExistsError(f"Directory '{name}' already exists at {project_path}")

    # Clone the repository
    subprocess.run(["git", "clone", url, str(project_path)], check=True)

    # Initialize engn and beads if missing
    init_project_structure(project_path)

    # Ensure project is ignored in workspace
    workspace_root = get_workspace_root(working_dir)
    ensure_project_ignored(workspace_root, project_path)

    return project_path


def delete_project(name: str, working_dir: Path) -> bool:
    """Delete a project directory."""
    project_path = working_dir / name
    if not project_path.exists() or not project_path.is_dir():
        return False

    # Remove from workspace .gitignore
    workspace_root = get_workspace_root(working_dir)
    remove_project_from_gitignore(workspace_root, name)

    # Delete with retries to handle locked files (e.g., beads daemon)
    for _ in range(3):
        shutil.rmtree(project_path, ignore_errors=True)
        if not project_path.exists():
            return True
        time.sleep(0.1)  # Brief delay for file handles to release

    return not project_path.exists()


def list_projects(working_dir: Path) -> List[str]:
    """List all projects in the working directory (git repos or engn projects)."""
    if not working_dir.exists() or not working_dir.is_dir():
        return []

    workspace_root = get_workspace_root(working_dir)
    projects = []
    for item in working_dir.iterdir():
        if item.is_dir() and (
            (item / "engn.jsonl").exists()
            or (item / "engn.toml").exists()
            or (item / ".git").exists()
        ):
            projects.append(item.name)
            # Ensure discovered projects are ignored
            ensure_project_ignored(workspace_root, item)

    return sorted(projects)


def get_project_status(name: str, working_dir: Path) -> Dict[str, Any]:
    """Get the status of a specific project."""
    project_path = working_dir / name
    if not project_path.exists():
        return {"name": name, "exists": False}

    status = {
        "name": name,
        "exists": True,
        "path": str(project_path),
        "is_git": (project_path / ".git").exists(),
        "is_beads": (project_path / ".beads").exists(),
        "is_engn": (project_path / "engn.jsonl").exists()
        or (project_path / "engn.toml").exists(),
    }

    if status["is_git"]:
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout.strip()
            if not output:
                status["git_status"] = "clean"
                status["git_untracked"] = 0
                status["git_modified"] = 0
            else:
                lines = output.split("\n")
                untracked = sum(1 for line in lines if line.startswith("??"))
                modified = len(lines) - untracked
                status["git_status"] = "changes"
                status["git_untracked"] = untracked
                status["git_modified"] = modified
        except Exception:
            status["git_status"] = "unknown"
            status["git_untracked"] = 0
            status["git_modified"] = 0

    return status
