import flet as ft
from unittest.mock import MagicMock
from engn.ui import RightDrawer
import pytest


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.theme_mode = ft.ThemeMode.DARK
    return page


def test_drawer_initialization(mock_page):
    drawer = RightDrawer(mock_page)
    assert drawer.width == 350
    assert drawer.visible is False
    assert isinstance(drawer.content, ft.Row)


def test_drawer_show_hide(mock_page):
    drawer = RightDrawer(mock_page)
    content = ft.Text("Test Content")
    drawer.show("Test Title", content)
    assert drawer.visible is True
    assert drawer.title_text.value == "Test Title"
    assert drawer.content_container.content == content

    drawer.hide()
    assert drawer.visible is False


def test_drawer_resize_logic(mock_page):
    drawer = RightDrawer(mock_page)
    initial_width = drawer.width if drawer.width is not None else 350

    # Simulate a drag event to the left (decreasing x, increasing width)
    # delta_x is positive when moving right, negative when moving left
    event = MagicMock()
    event.delta_x = -10
    event.data = '{"delta_x": -10}'
    drawer._handle_resize(event)

    # new_width = initial_width - (-10) = initial_width + 10
    assert drawer.width == initial_width + 10

    # Simulate a drag event to the right (increasing x, decreasing width)
    event.delta_x = 20
    event.data = '{"delta_x": 20}'
    drawer._handle_resize(event)
    assert drawer.width == initial_width + 10 - 20


def test_drawer_resize_limits(mock_page):
    drawer = RightDrawer(mock_page)

    # Try to resize below minimum (150)
    event = MagicMock()
    event.delta_x = 300  # 350 - 300 = 50 < 150
    event.data = '{"delta_x": 300}'
    drawer._handle_resize(event)
    assert drawer.width == 350  # Should not change

    # Try to resize above maximum (1200)
    event.delta_x = -1000  # 350 - (-1000) = 1350 > 1200
    event.data = '{"delta_x": -1000}'
    drawer._handle_resize(event)
    assert drawer.width == 350  # Should not change


def test_drawer_coloring_in_light_mode(mock_page):
    mock_page.theme_mode = ft.ThemeMode.LIGHT
    drawer = RightDrawer(mock_page)
    # Header should use SURFACE_CONTAINER
    row = drawer.content
    assert isinstance(row, ft.Row)
    col = row.controls[1]
    assert isinstance(col, ft.Column)
    header = col.controls[0]
    assert isinstance(header, ft.Container)
    assert header.bgcolor == ft.Colors.SURFACE_CONTAINER
    # Text color should be ON_SURFACE_VARIANT
    assert drawer.title_text.color == ft.Colors.ON_SURFACE_VARIANT


def test_drawer_resize_handle_visuals(mock_page):
    drawer = RightDrawer(mock_page)
    # Resize handle should be 10px wide with a VerticalDivider
    content = drawer.resize_handle.content
    assert isinstance(content, ft.Container)
    assert content.width == 10
    assert isinstance(content.content, ft.VerticalDivider)


def test_drawer_vertical_alignment(mock_page):
    drawer = RightDrawer(mock_page)
    row = drawer.content
    assert isinstance(row, ft.Row)
    assert row.vertical_alignment == ft.CrossAxisAlignment.STRETCH
