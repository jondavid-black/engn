import pytest
from unittest.mock import patch, MagicMock
from sysengn.main import main, flet_main
from engn.utils import get_version
import flet as ft


def test_sysengn_version_flag(capsys):
    with patch("sys.argv", ["sysengn", "--version"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out or get_version() in captured.out


def test_sysengn_flet_startup():
    with patch("sys.argv", ["sysengn"]):
        with patch("flet.app") as mock_app:
            main()
            mock_app.assert_called_once()


def test_flet_main():
    mock_page = MagicMock(spec=ft.Page)
    flet_main(mock_page)
    assert mock_page.title == "SysEngn"
    mock_page.add.assert_called()
