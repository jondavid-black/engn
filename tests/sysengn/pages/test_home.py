import flet as ft
import pytest
from unittest.mock import MagicMock, Mock, patch
from pathlib import Path

from engn.core.auth import User as EngnUser
from engn.ui.home_page import HomeDomainPage, ProjectView, PlanView


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    page.session.store = MagicMock()
    page.overlay = []
    return page


@pytest.fixture
def mock_user():
    return EngnUser(
        id="user1", email="user@example.com", name="Test User", default_project=None
    )


@pytest.fixture
def home_page(mock_page, mock_user):
    mock_pm_patcher = patch("engn.ui.home_page.ProjectManager")
    # PlanView and ProjectView are now imported in home_page.py
    # We don't need to patch IssueTracker here anymore as it's not used in HomeDomainPage

    mock_pm_cls = mock_pm_patcher.start()

    try:
        mock_pm = mock_pm_cls.return_value
        mock_pm.list_projects.return_value = ["proj1", "proj2"]

        p1 = Mock()
        p1.name = "proj1"
        p1.path = Path("/tmp/proj1")
        p1.is_git = True
        p1.is_beads = True
        p1.is_initialized = True
        p1.git_status = "clean"
        p1.git_untracked = 0
        p1.git_modified = 0
        p1.beads_features = 1
        p1.beads_bugs = 2
        p1.beads_tasks = 3
        p1.branches = ["main", "dev"]

        p2 = Mock()
        p2.name = "proj2"
        p2.path = Path("/tmp/proj2")
        p2.is_git = False
        p2.is_beads = False
        p2.is_initialized = False
        p2.git_status = ""
        p2.git_untracked = 0
        p2.git_modified = 0
        p2.beads_features = 0
        p2.beads_bugs = 0
        p2.beads_tasks = 0
        p2.branches = []

        mock_pm.get_all_projects.return_value = [p1, p2]

        hp = HomeDomainPage(mock_page, mock_user, Path("/tmp"))
        hp.update = MagicMock()
        yield hp
    finally:
        mock_pm_patcher.stop()


def test_home_page_init(home_page):
    assert home_page.active_project_name == "proj1"
    assert len(home_page.rail.destinations) == 2
    assert home_page.rail.selected_index == 0
    assert isinstance(home_page.content_area.content, PlanView)


def test_on_rail_change(home_page):
    # Plan view
    home_page.rail.selected_index = 0
    home_page._on_rail_change(None)
    assert isinstance(home_page.content_area.content, PlanView)

    # Project view
    home_page.rail.selected_index = 1
    home_page._on_rail_change(None)
    assert isinstance(home_page.content_area.content, ProjectView)


def test_on_project_selected(home_page):
    home_page._on_project_selected("proj2")
    assert home_page.active_project_name == "proj2"
    assert home_page.update.called


def test_home_page_refresh(home_page):
    view_mock = MagicMock()
    home_page.content_area.content = view_mock
    home_page.refresh()
    view_mock.refresh.assert_called_once()
    assert home_page.update.called
