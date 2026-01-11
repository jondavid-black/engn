from pathlib import Path
from engn.pm import ProjectManager


def test_project_manager_scans_existing_projects(tmp_path: Path):
    """Verify that ProjectManager finds git repositories in the working directory."""
    # Create some mock projects (directories with .git)
    project1 = tmp_path / "proj1"
    project1.mkdir()
    (project1 / ".git").mkdir()

    project2 = tmp_path / "proj2"
    project2.mkdir()
    (project2 / ".git").mkdir()

    # Create a non-project directory
    not_project = tmp_path / "random_dir"
    not_project.mkdir()

    pm = ProjectManager(tmp_path)
    projects = pm.list_projects()

    assert len(projects) == 2
    assert "proj1" in projects
    assert "proj2" in projects
    assert "random_dir" not in projects


def test_project_manager_get_all_projects(tmp_path: Path):
    """Verify that get_all_projects returns Project objects with correct info."""
    project_path = tmp_path / "my_project"
    project_path.mkdir()
    (project_path / ".git").mkdir()
    (project_path / "engn.toml").write_text("arch_path = 'arch'")

    pm = ProjectManager(tmp_path)
    projects = pm.get_all_projects()

    assert len(projects) == 1
    project = projects[0]
    assert project.name == "my_project"
    assert project.is_initialized is True
    assert project.path == project_path
