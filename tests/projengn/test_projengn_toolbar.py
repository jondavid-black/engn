from pathlib import Path
from unittest.mock import MagicMock
import flet as ft
from projengn.main import ProjEngnApp
from engn.config import ProjectConfig
from engn.core.auth import User


def test_projengn_app_toolbar_config():
    mock_page = MagicMock(spec=ft.Page)
    mock_page.session = MagicMock()
    mock_page.session.store = MagicMock()

    mock_config = MagicMock(spec=ProjectConfig)
    mock_user = MagicMock(spec=User)
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.preferred_color = None
    mock_user.has_role.return_value = False

    working_dir = Path(".")

    app = ProjEngnApp(
        page=mock_page,
        config=mock_config,
        user=mock_user,
        working_directory=working_dir,
    )

    assert app.toolbar.show_branch_dropdown is True
    assert app.toolbar.show_search is True
