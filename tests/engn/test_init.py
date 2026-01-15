import pytest
from unittest.mock import patch
from engn.main import main


def test_engn_init_command_creates_files_and_directories(tmp_path, capsys):
    # Mock sys.argv to simulate running 'engn init'
    with patch("sys.argv", ["engn", "init"]):
        # Mock Path.cwd to return the temporary directory
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with patch("shutil.which", return_value="/usr/bin/tool"):
                with patch(
                    "builtins.input",
                    side_effect=["Test Project", "SysML v2", "unified python"],
                ):
                    with patch("subprocess.run") as mock_run:
                        with pytest.raises(SystemExit) as e:
                            main()
                        assert e.value.code == 0

                        # Verify beads initialization
                        mock_run.assert_called_with(
                            ["bd", "init"], cwd=tmp_path, check=True
                        )

    # Check if directories were created
    assert (tmp_path / "mbse").is_dir()
    assert (tmp_path / "pm").is_dir()

    # Check if engn.jsonl was created
    config_file = tmp_path / "engn.jsonl"
    assert config_file.is_file()

    # Check content of engn.jsonl
    content = config_file.read_text()
    assert '"engn_type": "import"' in content
    assert '"modules": ["engn.project"]' in content
    assert '"sysengn_path": "mbse"' in content
    assert '"name": "Test Project"' in content

    # Check output
    captured = capsys.readouterr()
    assert "Successfully initialized engn project in" in captured.out


def test_engn_init_command_with_path(tmp_path, capsys):
    target_path = tmp_path / "subdir"
    # Mock sys.argv to simulate running 'engn init subdir'
    with patch("sys.argv", ["engn", "init", str(target_path)]):
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with patch("shutil.which", return_value="/usr/bin/tool"):
                with patch(
                    "builtins.input",
                    side_effect=["Test Project", "SysML v2", "unified python"],
                ):
                    with patch("subprocess.run") as mock_run:
                        with pytest.raises(SystemExit) as e:
                            main()
                        assert e.value.code == 0

                        # Verify beads initialization
                        mock_run.assert_called_with(
                            ["bd", "init"], cwd=target_path, check=True
                        )

    # Check if directories were created
    assert target_path.is_dir()
    assert (target_path / "mbse").is_dir()
    assert (target_path / "pm").is_dir()
    assert (target_path / "engn.jsonl").is_file()


def test_engn_init_command_with_flags(tmp_path, capsys):
    # Mock sys.argv to simulate running 'engn init' with flags
    with patch(
        "sys.argv",
        [
            "engn",
            "init",
            "--name",
            "Flag Project",
            "--language",
            "SysML v2",
            "--strategy",
            "unified python",
        ],
    ):
        # Mock Path.cwd to return the temporary directory
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with patch("shutil.which", return_value="/usr/bin/tool"):
                with patch("subprocess.run"):
                    with pytest.raises(SystemExit) as e:
                        main()
                    assert e.value.code == 0

    # Check if directories were created
    assert (tmp_path / "mbse").is_dir()
    assert (tmp_path / "pm").is_dir()

    # Check content of engn.jsonl
    config_file = tmp_path / "engn.jsonl"
    assert config_file.is_file()
    content = config_file.read_text()
    assert '"name": "Flag Project"' in content


def test_engn_init_command_missing_tools(tmp_path, capsys):
    # Mock sys.argv to simulate running 'engn init'
    with patch("sys.argv", ["engn", "init"]):
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            # Mock shutil.which to return None for one of the tools
            def side_effect(tool):
                if tool == "bd":
                    return None
                return f"/usr/bin/{tool}"

            with patch("shutil.which", side_effect=side_effect):
                with pytest.raises(SystemExit) as e:
                    main()
                assert e.value.code == 1

    # Check output for error
    captured = capsys.readouterr()
    assert "Error: Required core tools missing: bd" in captured.out
