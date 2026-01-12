import pytest
import subprocess
from engn.project import (
    create_new_project,
    list_projects,
    delete_project,
    get_project_status,
    init_project_structure,
)


@pytest.fixture
def temp_working_dir(tmp_path):
    working_dir = tmp_path / "work"
    working_dir.mkdir()
    return working_dir


def test_create_new_project(temp_working_dir):
    name = "test_proj"
    project_path = create_new_project(name, temp_working_dir)

    assert project_path.exists()
    assert (project_path / ".git").exists()
    assert (project_path / "engn.jsonl").exists()
    assert (project_path / "arch").exists()
    assert (project_path / "pm").exists()
    assert (project_path / "ux").exists()

    # Check engn.jsonl content
    with open(project_path / "engn.jsonl", "r") as f:
        content = f.read()
        assert '"engn_type": "type_def"' in content
        assert '"name": "ProjectConfig"' in content

    # Check default branch is main
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "main"


def test_list_projects(temp_working_dir):
    create_new_project("proj1", temp_working_dir)
    create_new_project("proj2", temp_working_dir)
    (temp_working_dir / "not_a_proj").mkdir()

    projects = list_projects(temp_working_dir)
    assert "proj1" in projects
    assert "proj2" in projects
    assert "not_a_proj" not in projects


def test_delete_project(temp_working_dir):
    create_new_project("to_delete", temp_working_dir)
    assert (temp_working_dir / "to_delete").exists()

    assert delete_project("to_delete", temp_working_dir)
    assert not (temp_working_dir / "to_delete").exists()


def test_get_project_status(temp_working_dir):
    create_new_project("status_proj", temp_working_dir)
    status = get_project_status("status_proj", temp_working_dir)

    assert status["exists"]
    assert status["name"] == "status_proj"
    assert status["is_git"]
    assert status["is_engn"]


def test_init_project_structure(temp_working_dir):
    path = temp_working_dir / "existing"
    path.mkdir()
    init_project_structure(path)

    assert (path / "engn.jsonl").exists()
    assert (path / "arch").exists()
