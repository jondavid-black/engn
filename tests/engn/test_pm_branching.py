from pathlib import Path

import git
import pytest

from engn.pm import ProjectManager


@pytest.fixture
def repo_with_commits(tmp_path: Path) -> Path:
    """Create a repo with an initial commit."""
    repo_dir = tmp_path / "test-repo"
    repo = git.Repo.init(repo_dir)

    # Create a file and commit it so we have a master/main branch
    (repo_dir / "README.md").write_text("# Test Repo")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    return repo_dir


def test_create_branch(tmp_path: Path, repo_with_commits: Path):
    """Test creating a new branch."""
    # Move repo to ProjectManager's working directory
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    project_path = work_dir / "my-project"

    # We can just clone the repo_with_commits to the work dir
    git.Repo.clone_from(str(repo_with_commits), project_path)

    pm = ProjectManager(work_dir)
    pm.create_branch("my-project", "feature-branch")

    repo = git.Repo(project_path)
    assert "feature-branch" in repo.heads
    assert repo.active_branch.name == "feature-branch"


def test_create_branch_project_not_found(tmp_path: Path):
    """Test creating a branch for a non-existent project."""
    pm = ProjectManager(tmp_path)
    with pytest.raises(FileNotFoundError):
        pm.create_branch("ghost-project", "feature-branch")


def test_list_branches(tmp_path: Path, repo_with_commits: Path):
    """Test listing branches."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    project_path = work_dir / "my-project"
    git.Repo.clone_from(str(repo_with_commits), project_path)

    pm = ProjectManager(work_dir)

    # Initially should have main/master
    branches = pm.list_branches("my-project")
    assert len(branches) >= 1

    pm.create_branch("my-project", "feature-1")
    branches = pm.list_branches("my-project")
    assert "feature-1" in branches


def test_checkout_branch(tmp_path: Path, repo_with_commits: Path):
    """Test checking out an existing branch."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    project_path = work_dir / "my-project"
    git.Repo.clone_from(str(repo_with_commits), project_path)

    pm = ProjectManager(work_dir)
    pm.create_branch("my-project", "feature-1")

    # Switch back to main (assuming default is main or master)
    default_branch = "main" if "main" in pm.list_branches("my-project") else "master"
    pm.checkout_branch("my-project", default_branch)

    repo = git.Repo(project_path)
    assert repo.active_branch.name == default_branch


def test_checkout_nonexistent_branch(tmp_path: Path, repo_with_commits: Path):
    """Test checking out a branch that doesn't exist."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    project_path = work_dir / "my-project"
    git.Repo.clone_from(str(repo_with_commits), project_path)

    pm = ProjectManager(work_dir)
    with pytest.raises(ValueError, match="Branch 'fake-branch' not found"):
        pm.checkout_branch("my-project", "fake-branch")


def test_delete_branch(tmp_path: Path, repo_with_commits: Path):
    """Test deleting a branch."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    project_path = work_dir / "my-project"
    git.Repo.clone_from(str(repo_with_commits), project_path)

    pm = ProjectManager(work_dir)
    pm.create_branch("my-project", "feature-to-delete")

    # Must switch off the branch to delete it
    default_branch = "main" if "main" in pm.list_branches("my-project") else "master"
    pm.checkout_branch("my-project", default_branch)

    pm.delete_branch("my-project", "feature-to-delete")

    assert "feature-to-delete" not in pm.list_branches("my-project")


def test_merge_branch(tmp_path: Path, repo_with_commits: Path):
    """Test merging a branch."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    project_path = work_dir / "my-project"
    git.Repo.clone_from(str(repo_with_commits), project_path)

    pm = ProjectManager(work_dir)
    pm.create_branch("my-project", "feature-merge")

    # Make a change in the feature branch
    (project_path / "new_file.txt").write_text("content")
    repo = git.Repo(project_path)
    repo.index.add(["new_file.txt"])
    repo.index.commit("Add new file")

    # Switch back to main
    default_branch = "main" if "main" in pm.list_branches("my-project") else "master"
    pm.checkout_branch("my-project", default_branch)

    # Merge
    pm.merge_branch("my-project", "feature-merge")

    # Verify file exists in main
    assert (project_path / "new_file.txt").exists()
