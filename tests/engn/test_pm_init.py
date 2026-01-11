import pytest
from pathlib import Path
import shutil
from engn.pm import ProjectManager


def test_initialize_project(tmp_path):
    # Setup a dummy project directory (without engn.toml)
    project_name = "test-project"
    project_path = tmp_path / project_name
    project_path.mkdir()
    (project_path / ".git").mkdir()  # Make it look like a git repo

    pm = ProjectManager(tmp_path)

    # Verify not initialized
    projects = pm.get_all_projects()
    assert len(projects) == 1
    assert projects[0].name == project_name
    assert not projects[0].is_initialized

    # Initialize
    pm.initialize_project(project_name)

    # Verify initialized
    assert (project_path / "engn.toml").exists()
    assert (project_path / "arch").exists()
    assert (project_path / "pm").exists()
    assert (project_path / "ux").exists()

    projects = pm.get_all_projects()
    assert projects[0].is_initialized


def test_initialize_workspace(tmp_path):
    pm = ProjectManager(tmp_path)

    # Initialize workspace
    pm.initialize_workspace()

    # Verify initialized
    assert (tmp_path / "engn.toml").exists()
    assert (tmp_path / "arch").exists()
    assert (tmp_path / "pm").exists()
    assert (tmp_path / "ux").exists()
