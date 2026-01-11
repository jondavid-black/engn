import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


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

    # Create engn.toml if it doesn't exist
    config_path = target_path / "engn.toml"
    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("[paths]\n")
            f.write('pm = "pm"\n')
            f.write('sysengn = "arch"\n')
            f.write('ux = "ux"\n')

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
    subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)

    # Initialize engn and beads
    init_project_structure(project_path)

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

    return project_path


def delete_project(name: str, working_dir: Path) -> bool:
    """Delete a project directory."""
    project_path = working_dir / name
    if not project_path.exists() or not project_path.is_dir():
        return False

    shutil.rmtree(project_path)
    return True


def list_projects(working_dir: Path) -> List[str]:
    """List all projects in the working directory that have an engn.toml."""
    if not working_dir.exists() or not working_dir.is_dir():
        return []

    projects = []
    for item in working_dir.iterdir():
        if item.is_dir() and (item / "engn.toml").exists():
            projects.append(item.name)

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
        "is_engn": (project_path / "engn.toml").exists(),
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
            status["git_status"] = result.stdout.strip() or "clean"
        except Exception:
            status["git_status"] = "unknown"

    return status
