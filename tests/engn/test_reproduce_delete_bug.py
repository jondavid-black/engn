import shutil
from pathlib import Path
import pytest
from engn.project import delete_project


def test_delete_project_with_beads(tmp_path):
    # Setup
    working_dir = tmp_path
    project_name = "buggy_project"
    project_path = working_dir / project_name
    project_path.mkdir()

    # Create standard content
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").touch()

    # Create .beads content
    beads_dir = project_path / ".beads"
    beads_dir.mkdir()
    (beads_dir / "config.json").touch()
    (beads_dir / "data").mkdir()
    (beads_dir / "data" / "issues.db").touch()

    # Ensure it exists
    assert project_path.exists()
    assert beads_dir.exists()

    # Action
    result = delete_project(project_name, working_dir)

    # Assert
    assert result is True
    assert not project_path.exists()
