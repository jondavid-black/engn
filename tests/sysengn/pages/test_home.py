import flet as ft
import pytest
from unittest.mock import MagicMock, Mock, patch
from pathlib import Path
from typing import cast

from engn.core.auth import User as EngnUser
from sysengn.pages.home import HomeDomainPage


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
    mock_pm_patcher = patch("sysengn.pages.home.ProjectManager")
    mock_it_patcher = patch("sysengn.pages.home.IssueTracker")

    mock_pm_cls = mock_pm_patcher.start()
    mock_it_cls = mock_it_patcher.start()

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

        mock_it = mock_it_cls.return_value
        mock_issue = {
            "id": "ISSUE-1",
            "title": "Test Issue",
            "issue_type": "task",
            "priority": 2,
        }
        mock_it.list_issues.return_value = [mock_issue]

        hp = HomeDomainPage(mock_page, mock_user, Path("/tmp"))
        hp.update = MagicMock()
        yield hp
    finally:
        mock_pm_patcher.stop()
        mock_it_patcher.stop()


def test_home_page_init(home_page):
    assert home_page.active_project_name == "proj1"
    assert len(home_page.rail.destinations) == 2
    assert home_page.rail.selected_index == 0


def test_on_rail_change(home_page):
    # Project view
    home_page.rail.selected_index = 0
    home_page._on_rail_change(None)
    assert home_page.content_area.content is not None
    # The content is a Column, its first control is a Row, its first control is a Text
    content_column = cast(ft.Column, home_page.content_area.content)
    title_row = cast(ft.Row, content_column.controls[0])
    project_title = cast(ft.Text, title_row.controls[0])
    assert project_title.value == "Projects"

    # Plan view
    home_page.rail.selected_index = 1
    home_page._on_rail_change(None)
    # Plan view should be built
    assert home_page.content_area.content is not None
    plan_content_column = cast(ft.Column, home_page.content_area.content)
    # First control is a Text "Plan: proj1"
    plan_title = cast(ft.Text, plan_content_column.controls[0])
    assert plan_title.value and "Plan:" in plan_title.value


def test_set_default_project(home_page, mock_user):
    with patch("sysengn.pages.home.update_user_default_project") as mock_update:
        home_page._set_default_project("proj2")
        mock_update.assert_called_with("user1", "proj2")
        assert home_page.user.default_project == "proj2"
        assert home_page.active_project_name == "proj2"


def test_set_default_project_no_page(home_page):
    # Temporarily remove page_ref
    original_page = home_page.page_ref
    home_page.page_ref = None  # type: ignore
    with patch("sysengn.pages.home.update_user_default_project"):
        home_page._set_default_project("proj1")
    home_page.page_ref = original_page


def test_show_new_project_dialog(home_page, mock_page):
    home_page._show_new_project_dialog(None)
    assert len(mock_page.overlay) > 0
    assert isinstance(mock_page.overlay[0], ft.AlertDialog)


def test_show_clone_project_dialog(home_page, mock_page):
    home_page._show_clone_project_dialog(None)
    assert len(mock_page.overlay) > 0
    assert isinstance(mock_page.overlay[0], ft.AlertDialog)


def test_delete_project_flow(home_page, mock_page):
    home_page._delete_project("proj1")
    assert len(mock_page.overlay) > 0
    dialog = cast(ft.AlertDialog, mock_page.overlay[-1])
    assert isinstance(dialog, ft.AlertDialog)

    # Find the "Delete" button and call its on_click
    delete_button = cast(ft.TextButton, dialog.actions[1])
    assert delete_button.content == "Delete"

    with patch.object(home_page.pm, "delete_project") as mock_del:
        if delete_button.on_click:
            delete_button.on_click(None)  # type: ignore
        mock_del.assert_called_with("proj1")


def test_new_project_flow(home_page, mock_page):
    home_page._show_new_project_dialog(None)
    dialog = cast(ft.AlertDialog, mock_page.overlay[-1])

    # Fill in the Name
    dialog_content = cast(ft.Column, dialog.content)
    name_field = cast(ft.TextField, dialog_content.controls[1])
    name_field.value = "my-new-proj"

    # Find the "Create" button and call its on_click
    create_button = cast(ft.TextButton, dialog.actions[1])
    assert create_button.content == "Create"

    with patch.object(home_page.pm, "new_project") as mock_new:
        if create_button.on_click:
            create_button.on_click(None)  # type: ignore
        mock_new.assert_called_with("my-new-proj")


def test_clone_project_flow(home_page, mock_page):
    home_page._show_clone_project_dialog(None)
    dialog = cast(ft.AlertDialog, mock_page.overlay[-1])

    # Fill in the URL
    dialog_content = cast(ft.Column, dialog.content)
    repo_url_field = cast(ft.TextField, dialog_content.controls[1])
    repo_url_field.value = "https://github.com/test/repo.git"

    # Find the "Clone" button and call its on_click
    clone_button = cast(ft.TextButton, dialog.actions[1])
    assert clone_button.content == "Clone"

    with patch.object(home_page.pm, "create_project") as mock_clone:
        if clone_button.on_click:
            clone_button.on_click(None)  # type: ignore
        mock_clone.assert_called_with("https://github.com/test/repo.git")


def test_on_rail_change_no_project(mock_page, mock_user):
    mock_pm_patcher = patch("sysengn.pages.home.ProjectManager")
    mock_it_patcher = patch("sysengn.pages.home.IssueTracker")
    mock_pm_cls = mock_pm_patcher.start()
    mock_it_patcher.start()
    try:
        mock_pm = mock_pm_cls.return_value
        mock_pm.list_projects.return_value = []
        mock_pm.get_all_projects.return_value = []

        user_no_proj = EngnUser(
            id="u2", email="u@e.com", name="U", default_project=None
        )
        hp = HomeDomainPage(mock_page, user_no_proj, Path("/tmp"))
        hp.update = MagicMock()

        hp.rail.selected_index = 1
        hp._on_rail_change(None)
        content_container = cast(ft.Container, hp.content_area.content)
        assert (
            "No active project selected"
            in cast(ft.Text, content_container.content).value
        )
    finally:
        mock_pm_patcher.stop()
        mock_it_patcher.stop()


def test_build_plan_view_error(home_page):
    with patch.object(home_page, "active_project_name", "some-proj"):
        with patch("sysengn.pages.home.IssueTracker") as mock_it_cls:
            mock_it = mock_it_cls.return_value
            mock_it.list_issues.side_effect = Exception("Tracker error")

            home_page.rail.selected_index = 1
            home_page._on_rail_change(None)
            content_container = cast(ft.Container, home_page.content_area.content)
            assert (
                "Error loading issues: Tracker error"
                in cast(ft.Text, content_container.content).value
            )
