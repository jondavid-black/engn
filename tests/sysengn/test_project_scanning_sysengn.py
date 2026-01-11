from pathlib import Path
from unittest.mock import MagicMock, patch
import flet as ft
from sysengn.main import MainApp
from sysengn.pages.home import HomeDomainPage


def test_main_app_passes_working_directory_to_home_page(tmp_path: Path):
    """Verify that MainApp passes the working directory to HomeDomainPage."""
    # Create a mock project
    project_dir = tmp_path / "my_proj"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()

    mock_page = MagicMock(spec=ft.Page)
    mock_page.session = MagicMock()
    mock_store = MagicMock()
    mock_page.session.store = mock_store

    mock_config = MagicMock()
    mock_user = MagicMock()
    mock_user.default_project = None

    # We need to mock Toolbar because it also tries to scan projects
    with (
        patch("sysengn.main.Toolbar"),
        patch("sysengn.main.HomeDomainPage", wraps=HomeDomainPage) as mock_home_cls,
    ):
        # We need to mock Path.cwd() to be different from tmp_path to ensure it uses passed dir
        with patch("pathlib.Path.cwd", return_value=Path("/some/other/path")):
            app = MainApp(
                mock_page, mock_config, user=mock_user, working_directory=tmp_path
            )

            # Check if HomeDomainPage was initialized with tmp_path
            # Find the HomeDomainPage call
            home_page_call = None
            for call in mock_home_cls.call_args_list:
                if call.args[2] == tmp_path:
                    home_page_call = call
                    break

            assert home_page_call is not None, (
                "HomeDomainPage should be initialized with tmp_path"
            )

            # Verify the view actually found the project
            home_page = app.views[0]
            assert isinstance(home_page, HomeDomainPage)
            assert "my_proj" in home_page.pm.list_projects()


def test_home_domain_page_scans_provided_directory(tmp_path: Path):
    """Verify that HomeDomainPage scans the provided working directory."""
    project_dir = tmp_path / "found_it"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()

    mock_page = MagicMock(spec=ft.Page)
    mock_user = MagicMock()
    mock_user.default_project = None

    page = HomeDomainPage(mock_page, mock_user, tmp_path)

    assert "found_it" in page.pm.list_projects()
    assert page.active_project_name == "found_it"
