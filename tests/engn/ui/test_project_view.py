import flet as ft
import pytest
from unittest.mock import MagicMock, Mock, patch
from pathlib import Path
from typing import cast

from engn.core.auth import User
from engn.ui.project_view import ProjectView


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.overlay = []
    page.session = MagicMock()
    return page


@pytest.fixture
def mock_user():
    return User(id="u1", email="u@e.com", name="U", default_project=None)


@pytest.fixture
def mock_pm():
    pm = MagicMock()
    p1 = Mock()
    p1.name = "proj1"
    p1.path = Path("/tmp/proj1")
    p1.is_git = True
    p1.is_beads = True
    p1.is_initialized = True
    p1.git_status = "clean"
    p1.git_modified = 0
    p1.git_untracked = 0
    p1.beads_bugs = 0
    p1.beads_features = 0
    p1.beads_tasks = 0
    pm.get_all_projects.return_value = [p1]
    return pm


def test_project_view_init(mock_page, mock_user, mock_pm):
    on_selected = MagicMock()
    view = ProjectView(mock_page, mock_user, mock_pm, on_selected)
    assert len(view.controls) == 3  # Row (header), Divider, ListView (projects)
    assert isinstance(view.controls[0], ft.Row)
    assert isinstance(view.controls[2], ft.ListView)


def test_project_view_refresh(mock_page, mock_user, mock_pm):
    on_selected = MagicMock()
    view = ProjectView(mock_page, mock_user, mock_pm, on_selected)
    view.update = MagicMock()
    view.refresh()
    mock_pm.get_all_projects.assert_called()
    view.update.assert_called()


def test_project_view_set_default(mock_page, mock_user, mock_pm):
    on_selected = MagicMock()
    view = ProjectView(mock_page, mock_user, mock_pm, on_selected)
    view.update = MagicMock()

    # Find the star button in the first project card
    lv = cast(ft.ListView, view.controls[2])
    card = cast(ft.Card, lv.controls[0])
    list_tile = cast(
        ft.ListTile,
        cast(ft.Column, cast(ft.Container, card.content).content).controls[0],
    )
    trailing_row = cast(ft.Row, list_tile.trailing)
    star_button = cast(ft.IconButton, trailing_row.controls[0])

    with patch("engn.ui.project_view.update_user_default_project") as mock_update_auth:
        if star_button.on_click:
            star_button.on_click(Mock())  # type: ignore
        mock_update_auth.assert_called_with("u1", "proj1")
        on_selected.assert_called_with("proj1")


def test_project_view_delete_click(mock_page, mock_user, mock_pm):
    on_selected = MagicMock()
    view = ProjectView(mock_page, mock_user, mock_pm, on_selected)

    lv = cast(ft.ListView, view.controls[2])
    card = cast(ft.Card, lv.controls[0])
    list_tile = cast(
        ft.ListTile,
        cast(ft.Column, cast(ft.Container, card.content).content).controls[0],
    )
    trailing_row = cast(ft.Row, list_tile.trailing)
    delete_button = cast(ft.IconButton, trailing_row.controls[2])

    if delete_button.on_click:
        delete_button.on_click(Mock())  # type: ignore

    # Check if AlertDialog was added to overlay
    assert len(mock_page.overlay) > 0
    dialog = cast(ft.AlertDialog, mock_page.overlay[-1])
    assert isinstance(dialog, ft.AlertDialog)
    title_text = cast(ft.Text, dialog.title)
    assert "Delete" in str(title_text.value)


def test_project_view_initialize_click(mock_page, mock_user, mock_pm):
    # Make project not initialized to show button
    mock_pm.get_all_projects.return_value[0].is_initialized = False
    on_selected = MagicMock()
    view = ProjectView(mock_page, mock_user, mock_pm, on_selected)

    lv = cast(ft.ListView, view.controls[2])
    card = cast(ft.Card, lv.controls[0])
    list_tile = cast(
        ft.ListTile,
        cast(ft.Column, cast(ft.Container, card.content).content).controls[0],
    )
    trailing_row = cast(ft.Row, list_tile.trailing)
    init_button = cast(ft.IconButton, trailing_row.controls[1])

    assert init_button.visible is True

    if init_button.on_click:
        init_button.on_click(Mock())  # type: ignore

    mock_pm.initialize_project.assert_called_with("proj1")


def test_show_new_project_dialog(mock_page, mock_user, mock_pm):
    on_selected = MagicMock()
    view = ProjectView(mock_page, mock_user, mock_pm, on_selected)

    header_row = cast(ft.Row, view.controls[0])
    new_button = cast(ft.FilledButton, header_row.controls[3])

    if new_button.on_click:
        new_button.on_click(Mock())  # type: ignore

    assert any(
        isinstance(o, ft.AlertDialog)
        and "New Project" in str(cast(ft.Text, o.title).value)
        for o in mock_page.overlay
    )


def test_show_clone_project_dialog(mock_page, mock_user, mock_pm):
    on_selected = MagicMock()
    view = ProjectView(mock_page, mock_user, mock_pm, on_selected)

    header_row = cast(ft.Row, view.controls[0])
    clone_button = cast(ft.FilledButton, header_row.controls[4])

    if clone_button.on_click:
        clone_button.on_click(Mock())  # type: ignore

    assert any(
        isinstance(o, ft.AlertDialog)
        and "Clone Project" in str(cast(ft.Text, o.title).value)
        for o in mock_page.overlay
    )
