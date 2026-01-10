import subprocess
from pathlib import Path
from engn.pm import ProjectManager
import pytest


def test_list_projects_empty(tmp_path: Path):
    """Test listing when no projects exist."""
    pm = ProjectManager(tmp_path)
    assert pm.list_projects() == []


def test_list_projects_with_repos(tmp_path: Path):
    """Test listing only git repositories as projects."""
    # Create a git project
    repo1 = tmp_path / "project-a"
    repo1.mkdir()
    (repo1 / ".git").mkdir()

    # Create another git project
    repo2 = tmp_path / "project-b"
    repo2.mkdir()
    (repo2 / ".git").mkdir()

    # Create a non-git directory (should be ignored)
    not_repo = tmp_path / "not-a-repo"
    not_repo.mkdir()

    pm = ProjectManager(tmp_path)
    projects = pm.list_projects()

    assert "project-a" in projects
    assert "project-b" in projects
    assert "not-a-repo" not in projects
    assert len(projects) == 2


def test_list_projects_nonexistent_workdir():
    """Test listing when working directory doesn't exist."""
    pm = ProjectManager("/path/does/not/exist/hopefully")
    assert pm.list_projects() == []


def test_create_project(tmp_path: Path):
    """Test cloning a project."""
    # We need a dummy remote repo to clone from.
    # Let's create a local bare repo to act as remote.
    remote_dir = tmp_path / "remote_repo.git"
    remote_dir.mkdir()
    subprocess.run(
        ["git", "init", "--bare", str(remote_dir)], check=True, capture_output=True
    )

    work_dir = tmp_path / "work"
    pm = ProjectManager(work_dir)

    # Clone the "remote" repo
    pm.create_project(str(remote_dir))

    assert (work_dir / "remote_repo").exists()
    assert (work_dir / "remote_repo" / ".git").exists()
    assert "remote_repo" in pm.list_projects()


def test_create_project_exists(tmp_path: Path):
    """Test error when cloning into existing directory."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / "existing").mkdir()

    pm = ProjectManager(work_dir)

    with pytest.raises(FileExistsError):
        # Using a fake URL since it should fail before cloning
        pm.create_project("https://example.com/existing.git")


def test_delete_project(tmp_path: Path):
    """Test deleting an existing project."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    project_dir = work_dir / "my-project"
    project_dir.mkdir()
    (project_dir / "some-file.txt").write_text("content")

    pm = ProjectManager(work_dir)
    pm.delete_project("my-project")

    assert not project_dir.exists()


def test_delete_nonexistent_project(tmp_path: Path):
    """Test deleting a project that doesn't exist."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()

    pm = ProjectManager(work_dir)

    with pytest.raises(FileNotFoundError):
        pm.delete_project("ghost-project")


def test_delete_not_a_directory(tmp_path: Path):
    """Test deleting something that isn't a directory (should fail safety check)."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    file_path = work_dir / "just-a-file"
    file_path.write_text("content")

    pm = ProjectManager(work_dir)

    with pytest.raises(NotADirectoryError):
        pm.delete_project("just-a-file")
