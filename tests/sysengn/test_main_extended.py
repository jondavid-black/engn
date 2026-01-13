"""Extended unit tests for SysEngn main application."""

from unittest.mock import MagicMock, patch

import flet as ft
import pytest

from sysengn.main import MainApp
from engn.config import ProjectConfig


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    return page


@pytest.fixture
def mock_config():
    config = MagicMock(spec=ProjectConfig)
    return config


class TestMainAppExtended:
    """Extended tests for MainApp."""

    def test_on_logout(self, mock_page, mock_config) -> None:
        """Test _on_logout callback."""
        with (
            patch("engn.ui.home_page.ProjectManager"),
            patch("engn.ui.home_page.ProjectView"),
            patch("engn.ui.home_page.PlanView"),
        ):
            app = MainApp(mock_page, mock_config)
            app._on_logout()
            # Just verify it doesn't crash (it only prints currently)

    def test_on_profile(self, mock_page, mock_config) -> None:
        """Test _on_profile callback."""
        with (
            patch("engn.ui.home_page.ProjectManager"),
            patch("engn.ui.home_page.ProjectView"),
            patch("engn.ui.home_page.PlanView"),
        ):
            app = MainApp(mock_page, mock_config)
            app._on_profile()

    def test_on_admin(self, mock_page, mock_config) -> None:
        """Test _on_admin callback."""
        with (
            patch("engn.ui.home_page.ProjectManager"),
            patch("engn.ui.home_page.ProjectView"),
            patch("engn.ui.home_page.PlanView"),
        ):
            app = MainApp(mock_page, mock_config)
            app._on_admin()

    def test_on_toggle_terminal(self, mock_page, mock_config) -> None:
        """Test _on_toggle_terminal callback."""
        with (
            patch("engn.ui.home_page.ProjectManager"),
            patch("engn.ui.home_page.ProjectView"),
            patch("engn.ui.home_page.PlanView"),
        ):
            app = MainApp(mock_page, mock_config)
            app._on_toggle_terminal()

    def test_on_tab_change(self, mock_page, mock_config) -> None:
        """Test _on_tab_change logic."""
        with (
            patch("engn.ui.home_page.ProjectManager"),
            patch("engn.ui.home_page.ProjectView"),
            patch("engn.ui.home_page.PlanView"),
        ):
            app = MainApp(mock_page, mock_config)
            app._on_tab_change(1)
            assert app.current_view_index == 1
            assert app.content_area.content == app.views[1]
            mock_page.update.assert_called_once()
