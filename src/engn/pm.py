import shutil
import subprocess
from pathlib import Path


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

        subprocess.run(
            ["git", "clone", repo_url, str(target_dir)],
            check=True,
            capture_output=True,
            text=True,
        )

    def delete_project(self, project_name: str) -> None:
        """
        Delete a project from the working directory.
        """
        if not self.working_directory.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        project_path = self.working_directory / project_name

        if not project_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        # Verify it's actually a directory before deleting
        if not project_path.is_dir():
            raise NotADirectoryError(f"'{project_name}' is not a directory")

        shutil.rmtree(project_path)
