import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import git
from git import exc

from engn import project


@dataclass
class Project:
    id: str
    name: str
    path: Path
    is_initialized: bool = False
    is_git: bool = False
    is_beads: bool = False
    git_status: str = ""
    git_untracked: int = 0
    git_modified: int = 0
    beads_features: int = 0
    beads_bugs: int = 0
    beads_tasks: int = 0
    branches: list[str] | None = None

    def __post_init__(self):
        if self.branches is None:
            self.branches = []


class ProjectManager:
    def __init__(self, working_directory: str | Path):
        self.working_directory = Path(working_directory)

    def list_projects(self) -> list[str]:
        """
        List all projects in the working directory.
        """
        return project.list_projects(self.working_directory)

    def get_all_projects(self) -> list[Project]:
        """
        Get all projects as Project objects with status information.
        """
        names = self.list_projects()
        projects = []
        for name in names:
            status = project.get_project_status(name, self.working_directory)
            branches = []
            if status["is_git"]:
                try:
                    branches = self.list_branches(name)
                except Exception:
                    pass

            beads_features = 0
            beads_bugs = 0
            beads_tasks = 0
            if status["is_beads"]:
                try:
                    beads_features, beads_bugs, beads_tasks = self._get_beads_counts(
                        name
                    )
                except Exception:
                    pass

            projects.append(
                Project(
                    id=name,
                    name=name,
                    path=Path(status["path"]),
                    is_initialized=status["is_engn"],
                    is_git=status["is_git"],
                    is_beads=status["is_beads"],
                    git_status=status.get("git_status", ""),
                    git_untracked=status.get("git_untracked", 0),
                    git_modified=status.get("git_modified", 0),
                    beads_features=beads_features,
                    beads_bugs=beads_bugs,
                    beads_tasks=beads_tasks,
                    branches=branches,
                )
            )
        return projects

    def initialize_project(self, project_name: str) -> None:
        """
        Initialize an existing project with engn structure.
        """
        project_path = self.working_directory / project_name
        project.init_project_structure(project_path)

    def create_project(self, repo_url: str) -> None:
        """
        Create a new project by cloning a git repository.
        """
        project.clone_project(repo_url, self.working_directory)

    def new_project(self, name: str) -> None:
        """
        Create a new project from scratch.
        """
        project.create_new_project(name, self.working_directory)

    def delete_project(self, project_name: str) -> None:
        """
        Delete a project from the working directory.
        """
        project_path = self.working_directory / project_name
        if project_path.exists() and not project_path.is_dir():
            raise NotADirectoryError(f"'{project_name}' is not a directory")

        if not project.delete_project(project_name, self.working_directory):
            raise FileNotFoundError(f"Project '{project_name}' not found")

    def list_branches(self, project_name: str) -> list[str]:
        """List all branches in a project."""
        repo = self._get_repo(project_name)
        return [head.name for head in repo.heads]

    def create_branch(self, project_name: str, branch_name: str) -> None:
        """Create a new branch and checkout to it."""
        repo = self._get_repo(project_name)
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

    def checkout_branch(self, project_name: str, branch_name: str) -> None:
        """Checkout an existing branch."""
        repo = self._get_repo(project_name)

        if branch_name not in [h.name for h in repo.heads]:
            raise ValueError(f"Branch '{branch_name}' not found")

        repo.heads[branch_name].checkout()

    def delete_branch(self, project_name: str, branch_name: str) -> None:
        """Delete a branch."""
        repo = self._get_repo(project_name)

        if branch_name not in [h.name for h in repo.heads]:
            raise ValueError(f"Branch '{branch_name}' not found")

        if repo.active_branch.name == branch_name:
            raise ValueError(f"Cannot delete active branch '{branch_name}'")

        repo.delete_head(branch_name)

    def merge_branch(self, project_name: str, branch_name: str) -> None:
        """Merge a branch into the current active branch."""
        repo = self._get_repo(project_name)

        if branch_name not in [h.name for h in repo.heads]:
            raise ValueError(f"Branch '{branch_name}' not found")

        repo.git.merge(branch_name)

    def _get_repo(self, project_name: str) -> git.Repo:
        """Helper to get and validate git repository."""
        project_path = self.working_directory / project_name
        if not project_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        try:
            return git.Repo(project_path)
        except exc.InvalidGitRepositoryError:
            raise ValueError(f"Project '{project_name}' is not a git repository")

    def _get_beads_counts(self, project_name: str) -> tuple[int, int, int]:
        """Get counts of open beads issues by type (features, bugs, tasks)."""
        project_path = self.working_directory / project_name
        result = subprocess.run(
            ["bd", "list", "--status=open", "--json"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return 0, 0, 0

        issues = json.loads(result.stdout)
        features = sum(1 for i in issues if i.get("issue_type") == "feature")
        bugs = sum(1 for i in issues if i.get("issue_type") == "bug")
        tasks = sum(1 for i in issues if i.get("issue_type") == "task")
        return features, bugs, tasks
