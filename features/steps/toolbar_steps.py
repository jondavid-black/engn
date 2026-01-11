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

    # Mock update() on tab containers to prevent "Control must be added to page" error
    # since these BDD tests run in a mock environment without a real page hierarchy
    if hasattr(context.toolbar, "_tab_containers"):
        for container in context.toolbar._tab_containers:
            container.update = MagicMock()


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
    tabs_component = context.toolbar.tabs
    assert tabs_component is not None, "Toolbar should have tabs attribute"

    # Custom Row of containers, SegmentedButton uses segments, TabBar uses tabs
    if hasattr(tabs_component, "controls"):
        actual_count = len(tabs_component.controls)
    elif hasattr(tabs_component, "segments"):
        actual_count = len(tabs_component.segments)
    elif hasattr(tabs_component, "tabs"):
        actual_count = len(tabs_component.tabs)
    else:
        raise AssertionError(
            f"Tabs component {type(tabs_component).__name__} has no controls, segments or tabs"
        )

    assert actual_count == count, f"Expected {count} tabs, got {actual_count}"


@then('the tabs should be labeled "{labels}"')  # type: ignore
def step_tabs_have_labels(context, labels):
    """Verify tabs have the expected labels."""
    expected_labels = [label.strip() for label in labels.split(",")]
    tabs_component = context.toolbar.tabs

    # Custom Row: containers with Text content
    # SegmentedButton: segments have value attribute
    # TabBar: tabs have label attribute
    if hasattr(tabs_component, "controls"):
        actual_labels = []
        for container in tabs_component.controls:
            if hasattr(container, "content") and hasattr(container.content, "value"):
                actual_labels.append(container.content.value)
    elif hasattr(tabs_component, "segments"):
        actual_labels = [seg.value for seg in tabs_component.segments]
    elif hasattr(tabs_component, "tabs"):
        actual_labels = [tab.label for tab in tabs_component.tabs]
    else:
        actual_labels = []

    assert actual_labels == expected_labels, (
        f"Expected tabs {expected_labels}, got {actual_labels}"
    )


@when("I simulate selecting tab index {index:d}")  # type: ignore
def step_select_tab(context, index):
    """Simulate a tab selection event."""
    # For custom tabs, directly call the click handler
    context.toolbar._handle_tab_click(index)


@then("the tab change callback should be invoked with index {index:d}")  # type: ignore
def step_callback_invoked(context, index):
    """Verify the callback was invoked with the correct index."""
    assert context.tab_change_callback_invoked, "Tab change callback should be invoked"
    assert context.tab_change_index == index, (
        f"Expected callback index {index}, got {context.tab_change_index}"
    )


# Controls that require a parent container to function
CONTROLS_REQUIRING_PARENT = (ft.TabBar, ft.Tab)


@then("the navigation tabs should be a standalone flet control")  # type: ignore
def step_tabs_standalone(context):
    """Verify navigation tabs use a standalone control, not one requiring a parent."""
    tabs_component = context.toolbar.tabs
    tabs_type = type(tabs_component)

    # TabBar requires a Tabs parent - it's not standalone
    assert not isinstance(tabs_component, CONTROLS_REQUIRING_PARENT), (
        f"Navigation tabs use {tabs_type.__name__} which requires a parent container. "
        f"Use a standalone control like SegmentedButton instead."
    )


@then("the navigation tabs should not require a parent container")  # type: ignore
def step_tabs_no_parent_required(context):
    """Verify the tabs component can render without a special parent."""
    tabs_component = context.toolbar.tabs

    # Check it's not TabBar (which requires Tabs parent)
    if isinstance(tabs_component, ft.TabBar):
        raise AssertionError(
            "TabBar cannot be used standalone - it must be inside a Tabs control. "
            "The error 'TabBar must be used within a Tabs control' will appear at runtime."
        )
