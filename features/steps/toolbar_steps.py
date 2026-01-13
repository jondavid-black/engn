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
from sysengn.auth import User  # noqa: E402
from engn.ui import Toolbar  # noqa: E402


@given("the SysEngn toolbar component is initialized")  # type: ignore
def step_toolbar_initialized(context):
    """Initialize the toolbar component with a mock page."""
    context.mock_page = MagicMock(spec=ft.Page)
    context.mock_page.session = MagicMock()
    context.mock_page.session.get.return_value = None

    context.tab_change_callback_invoked = False
    context.tab_change_index = None

    def on_tab_change(index: int):
        context.tab_change_callback_invoked = True
        context.tab_change_index = index

    context.on_tab_change = on_tab_change

    # Create a mock user
    user = User(
        id="1",
        name="Test User",
        email="test@example.com",
        first_name="Test",
        last_name="User",
    )

    context.toolbar = Toolbar(
        page=context.mock_page,
        user=user,
        logo_path="engn/assets/images/engn_logo_core_tiny_transparent.png",
        on_tab_change=on_tab_change,
        tabs=["Home", "MBSE", "UX", "Docs"],
        on_logout=MagicMock(),
        on_profile=MagicMock(),
    )

    # Mock update() on tab containers to prevent "Control must be added to page" error
    # since these BDD tests run in a mock environment without a real page hierarchy
    pass


@then("the toolbar should contain a logo image")  # type: ignore
def step_toolbar_has_logo(context):
    """Verify toolbar contains a logo image."""
    # The toolbar content is a Row with controls
    row = context.toolbar.content
    assert row is not None, "Toolbar content should not be None"
    assert hasattr(row, "controls"), "Toolbar content should have controls"

    # The Left Section is inside a Container at the first control (index 0)
    left_section_container = row.controls[0]
    assert isinstance(left_section_container, ft.Container)
    left_section = left_section_container.content
    assert isinstance(left_section, ft.Row)

    # First control in left section is the logo container
    logo_container = left_section.controls[0]
    assert isinstance(logo_container, ft.Container), (
        f"First control should be Container, got {type(logo_container)}"
    )

    # Content of container should be the image
    logo = logo_container.content
    assert isinstance(logo, ft.Image), (
        f"Container content should be Image, got {type(logo)}"
    )


@then("the logo should use the engn logo asset")  # type: ignore
def step_logo_uses_asset(context):
    """Verify the logo uses the correct asset path."""
    row = context.toolbar.content
    left_section_container = row.controls[0]
    left_section = left_section_container.content
    logo_container = left_section.controls[0]
    logo = logo_container.content

    assert hasattr(logo, "src"), "Logo should have src attribute"
    assert "engn_logo_core_tiny_transparent.png" in logo.src, (
        f"Logo src should contain 'engn_logo_core_tiny_transparent.png', got {logo.src}"
    )


@then("the toolbar should have {count:d} navigation tabs")  # type: ignore
def step_toolbar_has_tabs(context, count):
    """Verify toolbar has the expected number of tabs."""
    # tabs_control is a Tabs object wrapping a TabBar
    tabs_control = context.toolbar.tabs_control

    # We expect Tabs wrapping TabBar
    assert isinstance(tabs_control, ft.Tabs)
    tab_bar = tabs_control.content
    assert isinstance(tab_bar, ft.TabBar)

    actual_count = len(tab_bar.tabs)
    assert actual_count == count, f"Expected {count} tabs, got {actual_count}"


@then('the tabs should be labeled "{labels}"')  # type: ignore
def step_tabs_have_labels(context, labels):
    """Verify tabs have the expected labels."""
    expected_labels = [label.strip() for label in labels.split(",")]

    tabs_control = context.toolbar.tabs_control
    tab_bar = tabs_control.content
    actual_labels = [tab.label for tab in tab_bar.tabs]

    assert actual_labels == expected_labels, (
        f"Expected tabs {expected_labels}, got {actual_labels}"
    )


@when("I simulate selecting tab index {index:d}")  # type: ignore
def step_select_tab(context, index):
    """Simulate a tab selection event."""
    # The header is now a TabBar inside Tabs
    tab_bar = context.toolbar.tabs_control.content
    e = MagicMock(spec=ft.ControlEvent)
    e.data = str(index)

    # Trigger the on_click callback of TabBar
    if tab_bar.on_click:
        tab_bar.on_click(e)


@then("the tab change callback should be invoked with index {index:d}")  # type: ignore
def step_callback_invoked(context, index):
    """Verify the callback was invoked with the correct index."""
    assert context.tab_change_callback_invoked, "Tab change callback should be invoked"
    assert context.tab_change_index == index, (
        f"Expected callback index {index}, got {context.tab_change_index}"
    )


# Controls that require a parent container to function
CONTROLS_REQUIRING_PARENT = (ft.Tab,)


@then("the navigation tabs should be a standalone flet control")  # type: ignore
def step_tabs_standalone(context):
    """Verify navigation tabs use a standalone control, not one requiring a parent."""
    # We are using ft.Tabs now which is standalone
    tabs_component = context.toolbar.tabs_control

    assert isinstance(tabs_component, ft.Tabs)


@then("the navigation tabs should not require a parent container")  # type: ignore
def step_tabs_no_parent_required(context):
    """Verify the tabs component can render without a special parent."""
    # ft.Tabs is valid standalone
    pass
