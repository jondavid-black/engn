"""Toolbar component for SysEngn application."""

from pathlib import Path
from typing import Any, Callable

import flet as ft
from flet.controls.box import BoxFit
from flet.controls.padding import Padding


class Toolbar(ft.Container):
    """Main application toolbar with logo and navigation tabs."""

    TAB_LABELS = ["Home", "MBSE", "UX", "Docs"]

    def __init__(
        self,
        page: ft.Page,
        on_tab_change: Callable[[int], None],
    ):
        super().__init__()
        self.page_ref = page
        self.on_tab_change = on_tab_change
        self._selected_tab = 0

        # Build logo
        logo = self._build_logo()

        # Build navigation using SegmentedButton (standalone, doesn't require parent)
        self.nav_tabs = ft.SegmentedButton(
            selected=[self.TAB_LABELS[0]],
            segments=[
                ft.Segment(value=label, label=ft.Text(label))
                for label in self.TAB_LABELS
            ],
            on_change=self._handle_tab_change,
        )

        self.content = ft.Row(
            controls=[
                logo,
                ft.Container(expand=True),  # Spacer to push tabs to center
                self.nav_tabs,
                ft.Container(expand=True),  # Spacer for balance
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.padding = Padding.symmetric(horizontal=16, vertical=8)
        self.height = 60

    def _build_logo(self) -> ft.Image:
        """Build the application logo."""
        logo_path = Path(__file__).parent.parent.parent / "engn" / "assets" / "images"
        return ft.Image(
            src=str(logo_path / "engn_logo_core_tiny_transparent.png"),
            width=40,
            height=40,
            fit=BoxFit.CONTAIN,
        )

    def _handle_tab_change(self, e: Any) -> None:
        """Handle tab selection change."""
        if hasattr(e, "control") and hasattr(e.control, "selected"):
            selected = e.control.selected
            if selected:
                # Get the first selected value
                selected_label = list(selected)[0]
                if selected_label in self.TAB_LABELS:
                    self._selected_tab = self.TAB_LABELS.index(selected_label)
        self.on_tab_change(self._selected_tab)

    @property
    def selected_index(self) -> int:
        """Get the currently selected tab index."""
        return self._selected_tab

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        """Set the selected tab index."""
        self._selected_tab = value
        self.nav_tabs.selected = [self.TAB_LABELS[value]]

    @property
    def tabs(self) -> ft.SegmentedButton:
        """Get the tabs component for testing."""
        return self.nav_tabs

    @property
    def tab_labels(self) -> list[str]:
        """Get the list of tab labels."""
        return self.TAB_LABELS
