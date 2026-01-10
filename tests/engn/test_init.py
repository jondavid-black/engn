import pytest
from unittest.mock import patch
from engn.main import main
import shutil


def test_engn_init_command_creates_files_and_directories(tmp_path, capsys):
    # Mock sys.argv to simulate running 'engn init'
    with patch("sys.argv", ["engn", "init"]):
        # Mock Path.cwd to return the temporary directory
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with patch("shutil.which", return_value="/usr/bin/bd"):
                with patch("subprocess.run") as mock_run:
                    with pytest.raises(SystemExit) as e:
                        main()
                    assert e.value.code == 0

                    # Verify beads initialization
                    mock_run.assert_called_with(
                        ["bd", "init"], cwd=tmp_path, check=True
                    )

    # Check if directories were created
    assert (tmp_path / "arch").is_dir()
    assert (tmp_path / "pm").is_dir()
    assert (tmp_path / "ux").is_dir()

    # Check if engn.toml was created
    config_file = tmp_path / "engn.toml"
    assert config_file.is_file()

    # Check content of engn.toml
    content = config_file.read_text()
    assert 'arch_path = "arch"' in content
    assert 'pm_path = "pm"' in content
    assert 'ux_path = "ux"' in content

    # Check output
    captured = capsys.readouterr()
    assert "Initialized engn project in" in captured.out


def test_engn_init_command_with_path(tmp_path, capsys):
    project_dir = tmp_path / "my_project"

    # Mock sys.argv to simulate running 'engn init my_project'
    with patch("sys.argv", ["engn", "init", str(project_dir)]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0

    # Check if directories were created inside project_dir
    assert (project_dir / "arch").is_dir()
    assert (project_dir / "pm").is_dir()
    assert (project_dir / "ux").is_dir()

    # Check if engn.toml was created
    config_file = project_dir / "engn.toml"
    assert config_file.is_file()

    # Check output
    captured = capsys.readouterr()
    assert f"Initialized engn project in {project_dir}" in captured.out


def test_engn_init_command_existing_directory(tmp_path, capsys):
    # Create directory beforehand
    (tmp_path / "arch").mkdir()

    with patch("sys.argv", ["engn", "init"]):
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == 0

    # Should still succeed and ensure other dirs exist
    assert (tmp_path / "pm").is_dir()

    captured = capsys.readouterr()
    assert "Initialized engn project in" in captured.out
