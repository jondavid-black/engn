import flet as ft
import pytest
from unittest.mock import MagicMock, Mock, patch
from pathlib import Path
from typing import cast

from engn.ui.plan_view import PlanView


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.overlay = []
    page.session = MagicMock()
    return page


@pytest.fixture
def mock_it_patcher():
    with patch("engn.ui.plan_view.IssueTracker") as mock:
        mock_it = mock.return_value
        mock_it.list_issues.return_value = [
            {
                "id": "I1",
                "title": "T1",
                "status": "open",
                "issue_type": "task",
                "priority": 2,
            },
            {
                "id": "I2",
                "title": "T2",
                "status": "in_progress",
                "issue_type": "bug",
                "priority": 1,
            },
            {
                "id": "I3",
                "title": "T3",
                "status": "closed",
                "issue_type": "feature",
                "priority": 0,
            },
        ]
        yield mock


def test_plan_view_init(mock_page, mock_it_patcher):
    view = PlanView(mock_page, "proj1", Path("/tmp"))
    assert len(view.controls) == 3  # Header, Divider, Content
    assert isinstance(view.controls[0], ft.Row)
    header = cast(ft.Row, view.controls[0])
    assert (
        "Plan: proj1"
        in cast(ft.Text, cast(ft.Column, header.controls[0]).controls[0]).value
    )


def test_plan_view_toggle_backlog(mock_page, mock_it_patcher):
    view = PlanView(mock_page, "proj1", Path("/tmp"))
    view.update = MagicMock()
    header = cast(ft.Row, view.controls[0])
    seg_button = cast(ft.SegmentedButton, header.controls[2])

    # Toggle to backlog
    seg_button.selected = ["backlog"]
    if seg_button.on_change:
        seg_button.on_change(Mock(control=seg_button))  # type: ignore

    assert view.view_type == "backlog"
    # Content should be a Column for backlog
    assert isinstance(view.controls[2], ft.Column)


def test_plan_view_toggle_board(mock_page, mock_it_patcher):
    view = PlanView(mock_page, "proj1", Path("/tmp"))
    view.update = MagicMock()
    view.view_type = "backlog"
    view.controls = view._build_view()

    header = cast(ft.Row, view.controls[0])
    seg_button = cast(ft.SegmentedButton, header.controls[2])

    # Toggle back to board
    seg_button.selected = ["board"]
    if seg_button.on_change:
        seg_button.on_change(Mock(control=seg_button))  # type: ignore

    assert view.view_type == "board"
    # Content should be a Row for board
    assert isinstance(view.controls[2], ft.Row)


def test_plan_view_status_update(mock_page, mock_it_patcher):
    view = PlanView(mock_page, "proj1", Path("/tmp"))
    kanban_row = cast(ft.Row, view.controls[2])
    todo_col = cast(ft.Container, kanban_row.controls[0])

    # Find card action
    lv = cast(ft.ListView, cast(ft.Column, todo_col.content).controls[2])
    card = cast(ft.Card, lv.controls[0])
    action_row = cast(
        ft.Row, cast(ft.Column, cast(ft.Container, card.content).content).controls[2]
    )
    play_button = cast(ft.IconButton, action_row.controls[0])

    if play_button.on_click:
        play_button.on_click(Mock())  # type: ignore

    mock_it_patcher.return_value.update_status.assert_called_with("I1", "in_progress")


def test_plan_view_create_issue_click(mock_page, mock_it_patcher):
    view = PlanView(mock_page, "proj1", Path("/tmp"))
    header = cast(ft.Row, view.controls[0])
    create_button = cast(ft.FilledButton, header.controls[4])

    if create_button.on_click:
        create_button.on_click(Mock())  # type: ignore

    assert any(
        isinstance(o, ft.AlertDialog)
        and "Create New Issue" in str(cast(ft.Text, o.title).value)
        for o in mock_page.overlay
    )


def test_plan_view_refresh_click(mock_page, mock_it_patcher):
    view = PlanView(mock_page, "proj1", Path("/tmp"))
    header = cast(ft.Row, view.controls[0])
    refresh_button = cast(ft.IconButton, header.controls[5])

    with patch.object(view, "refresh") as mock_refresh:
        if refresh_button.on_click:
            refresh_button.on_click(Mock())  # type: ignore
        mock_refresh.assert_called()


def test_plan_view_no_project(mock_page):
    view = PlanView(mock_page, None, Path("/tmp"))
    assert (
        "No active project selected"
        in cast(ft.Text, cast(ft.Container, view.controls[0]).content).value
    )
