import pytest
from unittest.mock import patch, MagicMock
from sysengn.main import main, flet_main
from sysengn.views import LoginView
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


def test_flet_main_login_flow():
    mock_page = MagicMock(spec=ft.Page)
    mock_page.session = MagicMock()
    # Mock store
    mock_store = MagicMock()
    mock_page.session.store = mock_store
    mock_store.get.return_value = None  # Not logged in

    with patch("sysengn.main.ProjectConfig.load") as mock_load:
        mock_config = MagicMock()
        mock_load.return_value = mock_config

        flet_main(mock_page)

        # Should have added LoginView
        mock_page.add.assert_called()
        args, kwargs = mock_page.add.call_args
        assert isinstance(args[0], LoginView)


def test_flet_main_already_logged_in():
    mock_page = MagicMock(spec=ft.Page)
    mock_page.session = MagicMock()
    mock_store = MagicMock()
    mock_page.session.store = mock_store
    mock_store.get.return_value = MagicMock()  # Already logged in

    with patch("sysengn.main.ProjectConfig.load") as mock_load:
        mock_config = MagicMock()
        mock_load.return_value = mock_config

        with patch("sysengn.main.MainApp") as mock_app_cls:
            flet_main(mock_page)

            # Should show main app directly
            mock_app_cls.assert_called_once()
