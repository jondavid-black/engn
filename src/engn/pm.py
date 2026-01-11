import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Any, Dict

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


class ProjectManager:
    def __init__(self, working_directory: str | Path):
        self.working_directory = Path(working_directory)

    def list_projects(self) -> List[str]:
        """
        List all projects in the working directory.
        """
        return project.list_projects(self.working_directory)

    def get_all_projects(self) -> List[Project]:
        """
        Get all projects as Project objects with status information.
        """
        names = self.list_projects()
        projects = []
        for name in names:
            status = project.get_project_status(name, self.working_directory)
            projects.append(
                Project(
                    id=name,
                    name=name,
                    path=Path(status["path"]),
                    is_initialized=status["is_engn"],
                    is_git=status["is_git"],
                    is_beads=status["is_beads"],
                    git_status=status.get("git_status", ""),
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

    def list_branches(self, project_name: str) -> List[str]:
        """List all branches in a project."""
        import git

        project_path = self.working_directory / project_name
        repo = git.Repo(project_path)
        return [head.name for head in repo.heads]

    def create_branch(self, project_name: str, branch_name: str) -> None:
        """Create a new branch and checkout to it."""
        import git

        project_path = self.working_directory / project_name
        repo = git.Repo(project_path)
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

    def checkout_branch(self, project_name: str, branch_name: str) -> None:
        """Checkout an existing branch."""
        import git

        project_path = self.working_directory / project_name
        repo = git.Repo(project_path)

        if branch_name not in [h.name for h in repo.heads]:
            raise ValueError(f"Branch '{branch_name}' not found")

        repo.heads[branch_name].checkout()

    def delete_branch(self, project_name: str, branch_name: str) -> None:
        """Delete a branch."""
        import git

        project_path = self.working_directory / project_name
        repo = git.Repo(project_path)

        if branch_name not in [h.name for h in repo.heads]:
            raise ValueError(f"Branch '{branch_name}' not found")

        if repo.active_branch.name == branch_name:
            raise ValueError(f"Cannot delete active branch '{branch_name}'")

        repo.delete_head(branch_name)

    def merge_branch(self, project_name: str, branch_name: str) -> None:
        """Merge a branch into the current active branch."""
        import git

        project_path = self.working_directory / project_name
        repo = git.Repo(project_path)

        if branch_name not in [h.name for h in repo.heads]:
            raise ValueError(f"Branch '{branch_name}' not found")

        repo.git.merge(branch_name)
