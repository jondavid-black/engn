"""Unit tests for SysEngn toolbar component using mocks."""

from typing import cast
from unittest.mock import MagicMock, Mock

import flet as ft
import pytest

from sysengn.components.toolbar import Toolbar


@pytest.fixture
def mock_page():
    """Create a mock Flet page."""
    page = MagicMock(spec=ft.Page)
    return page


@pytest.fixture
def toolbar(mock_page):
    """Create a Toolbar instance with a mock callback."""
    on_tab_change = Mock()
    tb = Toolbar(page=mock_page, on_tab_change=on_tab_change)

    # Mock update() on tab containers to prevent "Control must be added to page" error
    # The Toolbar code iterates over _tab_containers and calls update()
    # We need to do this because the controls aren't actually added to a page tree in the test
    for container in tb._tab_containers:
        container.update = Mock()

    return tb


class TestToolbarUnit:
    """Unit tests for the Toolbar component."""

    def test_initialization(self, toolbar):
        """Test that the toolbar initializes with correct controls."""
        assert isinstance(toolbar, ft.Container)
        assert isinstance(toolbar.content, ft.Row)

        # Verify Row structure: Logo, Spacer, Tabs, Spacer
        row = cast(ft.Row, toolbar.content)
        controls = row.controls
        assert len(controls) == 4
        assert isinstance(controls[0], ft.Image)  # Logo
        assert isinstance(controls[1], ft.Container)  # Spacer
        assert isinstance(controls[2], ft.Row)  # Tabs
        assert isinstance(controls[3], ft.Container)  # Spacer

    def test_logo_path(self, toolbar):
        """Test that the logo has a source path."""
        row = cast(ft.Row, toolbar.content)
        logo = cast(ft.Image, row.controls[0])
        assert "engn_logo_core_tiny_transparent.png" in str(logo.src)

    def test_tabs_created(self, toolbar):
        """Test that navigation tabs are created correctly."""
        tabs_row = toolbar.nav_tabs
        assert isinstance(tabs_row, ft.Row)
        assert len(tabs_row.controls) == 4  # 4 tabs

        # Verify labels
        expected_labels = ["Home", "MBSE", "UX", "Docs"]
        for i, control in enumerate(tabs_row.controls):
            container = cast(ft.Container, control)
            text = container.content
            assert isinstance(text, ft.Text)
            assert text.value == expected_labels[i]

    def test_default_selection(self, toolbar):
        """Test that the first tab is selected by default."""
        assert toolbar.selected_index == 0

        # Check visual state of first tab
        first_tab_container = cast(ft.Container, toolbar.nav_tabs.controls[0])
        first_tab_text = cast(ft.Text, first_tab_container.content)

        # Primary color indicates selection (checking against variable usage pattern)
        # Note: We can't easily check the exact color value equality if it's an object,
        # but we can check it's assigned the 'selected' style logic.
        assert first_tab_text.color == ft.Colors.PRIMARY
        assert first_tab_container.border is not None

        # Check visual state of second tab (unselected)
        second_tab_container = cast(ft.Container, toolbar.nav_tabs.controls[1])
        second_tab_text = cast(ft.Text, second_tab_container.content)
        assert second_tab_text.color == ft.Colors.ON_SURFACE_VARIANT
        assert second_tab_container.border is None

    def test_tab_selection_updates_state(self, toolbar):
        """Test that setting selected_index updates the internal state."""
        toolbar.selected_index = 2
        assert toolbar.selected_index == 2

        # Verify visual update
        tabs = toolbar.nav_tabs.controls
        # Index 2 should be selected
        tab2 = cast(ft.Container, tabs[2])
        tab2_text = cast(ft.Text, tab2.content)
        assert tab2_text.color == ft.Colors.PRIMARY
        assert tab2.border is not None

        # Index 0 should be unselected now
        tab0 = cast(ft.Container, tabs[0])
        tab0_text = cast(ft.Text, tab0.content)
        assert tab0_text.color == ft.Colors.ON_SURFACE_VARIANT
        assert tab0.border is None

    def test_tab_click_callback(self, toolbar):
        """Test that clicking a tab triggers the callback and updates selection."""
        # Get the click handler for the second tab (MBSE)
        # The handler is a lambda in the actual code, but we can simulate the effect
        # by calling _handle_tab_click directly which is what the lambda does.

        # Verify initial state
        assert toolbar.selected_index == 0

        # Simulate click on index 1
        toolbar._handle_tab_click(1)

        # Verify state change
        assert toolbar.selected_index == 1

        # Verify callback was called
        toolbar.on_tab_change.assert_called_once_with(1)

    def test_properties(self, toolbar):
        """Test public properties."""
        assert toolbar.tabs == toolbar.nav_tabs
        assert toolbar.tab_labels == Toolbar.TAB_LABELS

    def test_handle_tab_change_event(self, toolbar):
        """Test the _handle_tab_change compatibility method."""
        # Create a mock event with control.selected
        mock_event = MagicMock()
        mock_event.control.selected = {"UX"}  # Set, as typical in some Flet events

        toolbar._handle_tab_change(mock_event)

        assert toolbar.selected_index == 2  # "UX" is index 2
        toolbar.on_tab_change.assert_called_with(2)
