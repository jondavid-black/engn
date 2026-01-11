"""Unit tests for SysEngn toolbar component using mocks."""

from typing import cast
from unittest.mock import MagicMock, Mock, patch

import flet as ft
import pytest

from sysengn.auth import User
from sysengn.components.toolbar import Toolbar


@pytest.fixture
def mock_page():
    """Create a mock Flet page."""
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    page.session.get.return_value = None
    page.theme_mode = ft.ThemeMode.DARK
    return page


@pytest.fixture
def mock_user():
    return User(
        id="1",
        name="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def toolbar(mock_page, mock_user):
    """Create a Toolbar instance with a mock callback."""
    # Mock ProjectManager
    with patch("sysengn.components.toolbar.ProjectManager") as mock_pm_cls:
        mock_pm = mock_pm_cls.return_value
        # Mock get_all_projects to return some dummy projects
        mock_project = Mock()
        mock_project.id = "p1"
        mock_project.name = "Project 1"
        mock_pm.get_all_projects.return_value = [mock_project]

        on_tab_change = Mock()
        on_logout = Mock()
        on_profile = Mock()

        tb = Toolbar(
            page=mock_page,
            user=mock_user,
            logo_path="logo.png",
            on_tab_change=on_tab_change,
            tabs=["Home", "MBSE", "UX", "Docs"],
            on_logout=on_logout,
            on_profile=on_profile,
        )
        return tb


class TestToolbarUnit:
    """Unit tests for the Toolbar component."""

    def test_initialization(self, toolbar):
        """Test that the toolbar initializes with correct controls."""
        assert isinstance(toolbar, ft.Container)
        assert isinstance(toolbar.content, ft.Row)

        # Verify main structure
        banner_row = cast(ft.Row, toolbar.content)
        assert len(banner_row.controls) == 3  # Left, Center (Tabs), Right

        # Left section
        assert isinstance(banner_row.controls[0], ft.Container)
        # Tabs
        assert isinstance(banner_row.controls[1], ft.Container)
        # Right section
        assert isinstance(banner_row.controls[2], ft.Container)

    def test_tabs_created(self, toolbar):
        """Test that navigation tabs are created correctly."""
        tabs_control = toolbar.tabs_control
        assert isinstance(tabs_control, ft.Tabs)

        # Access the TabBar within Tabs
        tab_bar = cast(ft.TabBar, tabs_control.content)
        assert isinstance(tab_bar, ft.TabBar)

        # Verify tabs in TabBar
        assert len(tab_bar.tabs) == 4
        tab0 = cast(ft.Tab, tab_bar.tabs[0])
        assert tab0.label == "Home"
        tab1 = cast(ft.Tab, tab_bar.tabs[1])
        assert tab1.label == "MBSE"

    def test_avatar_initials(self, toolbar):
        """Test that the avatar shows correct initials."""
        avatar = toolbar.avatar_control
        assert isinstance(avatar, ft.CircleAvatar)
        content = cast(ft.Text, avatar.content)
        assert content.value == "TU"  # Test User
