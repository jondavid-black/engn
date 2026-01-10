import pytest
from unittest.mock import patch
from engn.main import main


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


def test_engn_init_command_without_beads_installed(tmp_path, capsys):
    # Mock sys.argv to simulate running 'engn init'
    with patch("sys.argv", ["engn", "init"]):
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            # Mock shutil.which to return None, simulating 'bd' not found
            with patch("shutil.which", return_value=None):
                with patch("subprocess.run") as mock_run:
                    with pytest.raises(SystemExit) as e:
                        main()
                    assert e.value.code == 0

                    # Verify subprocess.run was NOT called for beads init
                    mock_run.assert_not_called()

    # Check output for warning
    captured = capsys.readouterr()
    assert "Warning: 'bd' (beads) not found" in captured.out
    assert "Initialized engn project in" in captured.out
