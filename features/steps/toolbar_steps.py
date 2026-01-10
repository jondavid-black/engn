"""Step definitions for SysEngn toolbar BDD tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

from behave import given, then, when

# Add src to sys.path to allow imports
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import flet as ft  # noqa: E402
from sysengn.components.toolbar import Toolbar  # noqa: E402


@given("the SysEngn toolbar component is initialized")  # type: ignore
def step_toolbar_initialized(context):
    """Initialize the toolbar component with a mock page."""
    context.mock_page = MagicMock(spec=ft.Page)
    context.tab_change_callback_invoked = False
    context.tab_change_index = None

    def on_tab_change(index: int):
        context.tab_change_callback_invoked = True
        context.tab_change_index = index

    context.on_tab_change = on_tab_change
    context.toolbar = Toolbar(
        page=context.mock_page,
        on_tab_change=on_tab_change,
    )


@then("the toolbar should contain a logo image")  # type: ignore
def step_toolbar_has_logo(context):
    """Verify toolbar contains a logo image."""
    # The toolbar content is a Row with controls
    row = context.toolbar.content
    assert row is not None, "Toolbar content should not be None"
    assert hasattr(row, "controls"), "Toolbar content should have controls"

    # First control should be the logo (ft.Image)
    logo = row.controls[0]
    assert isinstance(logo, ft.Image), (
        f"First control should be Image, got {type(logo)}"
    )


@then("the logo should use the engn logo asset")  # type: ignore
def step_logo_uses_asset(context):
    """Verify the logo uses the correct asset path."""
    row = context.toolbar.content
    logo = row.controls[0]

    assert hasattr(logo, "src"), "Logo should have src attribute"
    assert "engn_logo_core_tiny_transparent.png" in logo.src, (
        f"Logo src should contain 'engn_logo_core_tiny_transparent.png', got {logo.src}"
    )


@then("the toolbar should have {count:d} navigation tabs")  # type: ignore
def step_toolbar_has_tabs(context, count):
    """Verify toolbar has the expected number of tabs."""
    tabs = context.toolbar.tabs
    assert tabs is not None, "Toolbar should have tabs attribute"
    assert hasattr(tabs, "tabs"), "Tabs component should have tabs list"
    assert len(tabs.tabs) == count, f"Expected {count} tabs, got {len(tabs.tabs)}"


@then('the tabs should be labeled "{labels}"')  # type: ignore
def step_tabs_have_labels(context, labels):
    """Verify tabs have the expected labels."""
    expected_labels = [label.strip() for label in labels.split(",")]
    tab_bar = context.toolbar.tabs

    actual_labels = [tab.label for tab in tab_bar.tabs]
    assert actual_labels == expected_labels, (
        f"Expected tabs {expected_labels}, got {actual_labels}"
    )


@when("I simulate selecting tab index {index:d}")  # type: ignore
def step_select_tab(context, index):
    """Simulate a tab selection event."""
    # Create a mock event with the selected index
    mock_event = MagicMock()
    mock_event.control = context.toolbar.tabs
    mock_event.control.selected_index = index

    # Trigger the handler
    context.toolbar._handle_tab_change(mock_event)


@then("the tab change callback should be invoked with index {index:d}")  # type: ignore
def step_callback_invoked(context, index):
    """Verify the callback was invoked with the correct index."""
    assert context.tab_change_callback_invoked, "Tab change callback should be invoked"
    assert context.tab_change_index == index, (
        f"Expected callback index {index}, got {context.tab_change_index}"
    )
