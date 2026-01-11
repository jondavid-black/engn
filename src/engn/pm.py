import shutil
from dataclasses import dataclass
from pathlib import Path

import git


@dataclass
class Project:
    id: str
    name: str
    path: Path
    is_initialized: bool = False


class ProjectManager:
    def __init__(self, working_directory: str | Path):
        self.working_directory = Path(working_directory)

    def list_projects(self) -> list[str]:
        """
        List all projects in the working directory.
        A project is considered to be any directory that is a git repository.
        """
        if not self.working_directory.exists():
            return []

        projects = []
        for item in self.working_directory.iterdir():
            if item.is_dir() and (item / ".git").exists():
                projects.append(item.name)

        return sorted(projects)

    def get_all_projects(self) -> list[Project]:
        """
        Get all projects as Project objects.
        """
        names = self.list_projects()
        projects = []
        for name in names:
            path = self.working_directory / name
            is_initialized = (path / "engn.toml").exists()
            projects.append(
                Project(
                    id=name,  # Use name as ID for now
                    name=name,
                    path=path,
                    is_initialized=is_initialized,
                )
            )
        return projects

    def initialize_project(self, project_name: str) -> None:
        """
        Initialize an existing project with engn structure.
        """
        project_path = self._get_project_path(project_name)

        # Create directories
        for dir_name in ["arch", "pm", "ux"]:
            (project_path / dir_name).mkdir(exist_ok=True)

        # Create engn.toml
        config_path = project_path / "engn.toml"
        if not config_path.exists():
            with open(config_path, "w") as f:
                f.write('arch_path = "arch"\n')
                f.write('pm_path = "pm"\n')
                f.write('ux_path = "ux"\n')

        # Initialize beads if installed
        import subprocess

        if shutil.which("bd"):
            try:
                subprocess.run(["bd", "init"], cwd=project_path, check=True)
            except subprocess.CalledProcessError:
                # Beads might already be initialized or other error
                pass

    def initialize_workspace(self) -> None:
        """
        Initialize the working directory with engn structure.
        """
        # Create directories
        for dir_name in ["arch", "pm", "ux"]:
            (self.working_directory / dir_name).mkdir(exist_ok=True)

        # Create engn.toml
        config_path = self.working_directory / "engn.toml"
        if not config_path.exists():
            with open(config_path, "w") as f:
                f.write('arch_path = "arch"\n')
                f.write('pm_path = "pm"\n')
                f.write('ux_path = "ux"\n')

        # Initialize beads if installed
        import subprocess

        if shutil.which("bd"):
            try:
                subprocess.run(["bd", "init"], cwd=self.working_directory, check=True)
            except subprocess.CalledProcessError:
                # Beads might already be initialized or other error
                pass

    def create_project(self, repo_url: str) -> None:
        """
        Create a new project by cloning a git repository.
        """
        if not self.working_directory.exists():
            self.working_directory.mkdir(parents=True, exist_ok=True)

        # Extract repo name from URL for directory name
        # Basic parsing: ends with .git or just take the last part
        name = repo_url.rstrip("/").split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]

        target_dir = self.working_directory / name

        if target_dir.exists():
            raise FileExistsError(f"Project '{name}' already exists")

        git.Repo.clone_from(repo_url, target_dir)

    def _get_project_path(self, project_name: str) -> Path:
        """Helper to get and validate project path."""
        if not self.working_directory.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        project_path = self.working_directory / project_name

        if not project_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        return project_path

    def delete_project(self, project_name: str) -> None:
        """
        Delete a project from the working directory.
        """
        project_path = self._get_project_path(project_name)

        # Verify it's actually a directory before deleting
        if not project_path.is_dir():
            raise NotADirectoryError(f"'{project_name}' is not a directory")

        shutil.rmtree(project_path)

    def list_branches(self, project_name: str) -> list[str]:
        """List all branches in a project."""
        project_path = self._get_project_path(project_name)
        repo = git.Repo(project_path)
        return [head.name for head in repo.heads]

    def create_branch(self, project_name: str, branch_name: str) -> None:
        """Create a new branch and checkout to it."""
        project_path = self._get_project_path(project_name)
        repo = git.Repo(project_path)
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

    def checkout_branch(self, project_name: str, branch_name: str) -> None:
        """Checkout an existing branch."""
        project_path = self._get_project_path(project_name)
        repo = git.Repo(project_path)

        if branch_name not in repo.heads:
            raise ValueError(f"Branch '{branch_name}' not found")

        repo.heads[branch_name].checkout()

    def delete_branch(self, project_name: str, branch_name: str) -> None:
        """Delete a branch."""
        project_path = self._get_project_path(project_name)
        repo = git.Repo(project_path)

        if branch_name not in repo.heads:
            raise ValueError(f"Branch '{branch_name}' not found")

        if repo.active_branch.name == branch_name:
            raise ValueError(f"Cannot delete active branch '{branch_name}'")

        repo.delete_head(branch_name)

    def merge_branch(self, project_name: str, branch_name: str) -> None:
        """Merge a branch into the current active branch."""
        project_path = self._get_project_path(project_name)
        repo = git.Repo(project_path)

        if branch_name not in repo.heads:
            raise ValueError(f"Branch '{branch_name}' not found")

        # This is a simplified merge that assumes no conflicts for now
        repo.git.merge(branch_name)
