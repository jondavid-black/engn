"""Toolbar component for SysEngn application."""

from pathlib import Path
from typing import Any, Callable, cast

import flet as ft
from flet.controls.border import Border, BorderSide
from flet.controls.box import BoxFit
from flet.controls.padding import Padding


class Toolbar(ft.Container):
    """Main application toolbar with logo and navigation tabs."""

    TAB_LABELS = ["Home", "MBSE", "UX", "Docs"]
    TAB_WIDTH = 80

    def __init__(
        self,
        page: ft.Page,
        on_tab_change: Callable[[int], None],
    ):
        super().__init__()
        self.page_ref = page
        self.on_tab_change = on_tab_change
        self._selected_tab = 0
        self._tab_containers: list[ft.Container] = []
        self._tab_texts: list[ft.Text] = []

        # Build logo
        logo = self._build_logo()

        # Build custom navigation tabs
        self.nav_tabs = self._build_tabs()

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

    def _build_logo(self) -> ft.Container:
        """Build the application logo."""
        logo_path = Path(__file__).parent.parent.parent / "engn" / "assets" / "images"
        image = ft.Image(
            src=str(logo_path / "engn_logo_core_tiny_transparent.png"),
            width=40,
            height=40,
            fit=BoxFit.CONTAIN,
        )
        return ft.Container(
            content=image,
            on_click=lambda _: self._handle_tab_click(0),
            tooltip="Go to Home",
        )

    def _build_tabs(self) -> ft.Row:
        """Build custom navigation tabs with underline selection."""
        self._tab_containers = []
        self._tab_texts = []

        for i, label in enumerate(self.TAB_LABELS):
            is_selected = i == self._selected_tab
            text = ft.Text(
                label,
                color=ft.Colors.PRIMARY
                if is_selected
                else ft.Colors.ON_SURFACE_VARIANT,
                weight=ft.FontWeight.W_500,
            )
            self._tab_texts.append(text)

            container = ft.Container(
                content=text,
                width=self.TAB_WIDTH,
                padding=Padding.symmetric(vertical=8),
                alignment=ft.Alignment(0, 0),
                border=Border(bottom=BorderSide(2, ft.Colors.PRIMARY))
                if is_selected
                else None,
                on_click=lambda e, idx=i: self._handle_tab_click(idx),
            )
            self._tab_containers.append(container)

        return ft.Row(
            controls=cast(list[ft.Control], self._tab_containers),
            spacing=0,
        )

    def _update_tab_styles(self) -> None:
        """Update tab visual styles based on current selection."""
        for i, (container, text) in enumerate(
            zip(self._tab_containers, self._tab_texts)
        ):
            is_selected = i == self._selected_tab
            text.color = (
                ft.Colors.PRIMARY if is_selected else ft.Colors.ON_SURFACE_VARIANT
            )
            container.border = (
                Border(bottom=BorderSide(2, ft.Colors.PRIMARY)) if is_selected else None
            )
            container.update()

    def _handle_tab_click(self, index: int) -> None:
        """Handle tab click."""
        self._selected_tab = index
        self._update_tab_styles()
        self.on_tab_change(self._selected_tab)

    def _handle_tab_change(self, e: Any) -> None:
        """Handle tab selection change (for compatibility with tests)."""
        if hasattr(e, "control") and hasattr(e.control, "selected"):
            selected = e.control.selected
            if selected:
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
        self._update_tab_styles()

    @property
    def tabs(self) -> ft.Row:
        """Get the tabs component for testing."""
        return self.nav_tabs

    @property
    def tab_labels(self) -> list[str]:
        """Get the list of tab labels."""
        return self.TAB_LABELS
