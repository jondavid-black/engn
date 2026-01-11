import pytest
from unittest.mock import patch, MagicMock
from projengn.main import main, flet_main
from engn.utils import get_version
import flet as ft


def test_projengn_version_flag(capsys):
    with patch("sys.argv", ["projengn", "--version"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out or get_version() in captured.out


def test_projengn_flet_startup():
    with patch("sys.argv", ["projengn"]):
        with patch("flet.app") as mock_app:
            main()
            mock_app.assert_called_once()


def test_flet_main():
    mock_page = MagicMock(spec=ft.Page)
    flet_main(mock_page, working_directory=".")
    assert mock_page.title == "ProjEngn"
