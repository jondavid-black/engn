"""Toolbar component for SysEngn application."""

from pathlib import Path
from typing import Any, Callable

import flet as ft
from flet.controls.box import BoxFit
from flet.controls.padding import Padding


class Toolbar(ft.Container):
    """Main application toolbar with navigation and controls."""

    def __init__(
        self,
        page: ft.Page,
        on_tab_change: Callable[[int], None],
        on_terminal_toggle: Callable[[], None],
        on_logout: Callable[[], None],
        username: str = "User",
    ):
        super().__init__()
        self.page_ref = page
        self.on_tab_change = on_tab_change
        self.on_terminal_toggle = on_terminal_toggle
        self.on_logout = on_logout
        self.username = username
        self._selected_tab = 0

        # Build toolbar sections
        left_section = self._build_left_section()
        center_section = self._build_center_section()
        right_section = self._build_right_section()

        self.content = ft.Row(
            controls=[
                left_section,
                center_section,
                right_section,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.padding = Padding.symmetric(horizontal=16, vertical=8)
        self.height = 60

    def _build_left_section(self) -> ft.Row:
        """Build the left section with logo and dropdowns."""
        # Application icon
        logo_path = Path(__file__).parent.parent.parent / "engn" / "assets" / "images"
        logo = ft.Image(
            src=str(logo_path / "engn_logo_core_tiny_transparent.png"),
            width=36,
            height=36,
            fit=BoxFit.CONTAIN,
        )

        # Project/repo dropdown
        self.project_dropdown = ft.Dropdown(
            label="Project",
            width=180,
            height=48,
            options=[
                ft.dropdown.Option(key="engn", text="engn"),
                ft.dropdown.Option(key="project-alpha", text="project-alpha"),
                ft.dropdown.Option(key="project-beta", text="project-beta"),
            ],
            value="engn",
            dense=True,
            content_padding=Padding.symmetric(horizontal=10, vertical=5),
        )

        # Workspace/branch dropdown
        self.branch_dropdown = ft.Dropdown(
            label="Branch",
            width=150,
            height=48,
            options=[
                ft.dropdown.Option(key="main", text="main"),
                ft.dropdown.Option(key="develop", text="develop"),
                ft.dropdown.Option(key="feature/toolbar", text="feature/toolbar"),
            ],
            value="main",
            dense=True,
            content_padding=Padding.symmetric(horizontal=10, vertical=5),
        )

        return ft.Row(
            controls=[
                logo,
                ft.Container(width=16),  # Spacer
                self.project_dropdown,
                ft.Container(width=8),
                self.branch_dropdown,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

    def _build_center_section(self) -> ft.NavigationBar:
        """Build the center section with domain tabs."""
        self.nav_bar = ft.NavigationBar(
            selected_index=0,
            on_change=self._handle_tab_change,
            destinations=[
                ft.NavigationBarDestination(label="Home", icon=ft.Icons.HOME),
                ft.NavigationBarDestination(label="MBSE", icon=ft.Icons.ACCOUNT_TREE),
                ft.NavigationBarDestination(label="UX", icon=ft.Icons.DESIGN_SERVICES),
                ft.NavigationBarDestination(label="Docs", icon=ft.Icons.DESCRIPTION),
            ],
            height=56,
            bgcolor=ft.Colors.TRANSPARENT,
        )
        return self.nav_bar

    def _build_right_section(self) -> ft.Row:
        """Build the right section with search and action icons."""
        # Search bar
        self.search_field = ft.TextField(
            hint_text="Search...",
            width=200,
            height=40,
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            border_radius=20,
            content_padding=Padding.symmetric(horizontal=12, vertical=8),
        )

        # Terminal toggle button
        self.terminal_button = ft.IconButton(
            icon=ft.Icons.TERMINAL,
            tooltip="Toggle Terminal",
            on_click=self._handle_terminal_toggle,
        )

        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE
            if self.page_ref.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE,
            tooltip="Toggle Theme",
            on_click=self._handle_theme_toggle,
        )

        # User avatar with popup menu
        initials = self._get_initials(self.username)
        self.user_avatar = ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Text(
                    initials,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                width=36,
                height=36,
                border_radius=18,
                bgcolor=ft.Colors.PRIMARY,
                alignment=ft.Alignment(0, 0),
            ),
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PERSON, size=18),
                            ft.Text("Profile"),
                        ],
                        spacing=8,
                    ),
                    on_click=self._handle_profile,
                ),
                ft.PopupMenuItem(),  # Divider
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOGOUT, size=18),
                            ft.Text("Logout"),
                        ],
                        spacing=8,
                    ),
                    on_click=self._handle_logout,
                ),
            ],
            tooltip=self.username,
        )

        return ft.Row(
            controls=[
                self.search_field,
                ft.Container(width=8),
                self.terminal_button,
                self.theme_button,
                ft.Container(width=8),
                self.user_avatar,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

    def _get_initials(self, name: str) -> str:
        """Extract initials from a name."""
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        elif len(parts) == 1 and len(parts[0]) >= 2:
            return parts[0][:2].upper()
        return "U"

    def _handle_tab_change(self, e: Any) -> None:
        """Handle tab selection change."""
        self._selected_tab = e.control.selected_index
        self.on_tab_change(self._selected_tab)

    def _handle_terminal_toggle(self, e: Any) -> None:
        """Handle terminal toggle button click."""
        self.on_terminal_toggle()

    def _handle_theme_toggle(self, e: Any) -> None:
        """Handle theme toggle button click."""
        if self.page_ref.theme_mode == ft.ThemeMode.DARK:
            self.page_ref.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        else:
            self.page_ref.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        self.page_ref.update()

    def _handle_profile(self, e: Any) -> None:
        """Handle profile menu item click."""
        # Show a simple dialog for now
        dialog = ft.AlertDialog(
            title=ft.Text("Profile"),
            content=ft.Text(f"User: {self.username}\n\nProfile settings coming soon."),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self._close_dialog(dialog)),
            ],
        )
        self.page_ref.overlay.append(dialog)
        dialog.open = True
        self.page_ref.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        """Close a dialog."""
        dialog.open = False
        self.page_ref.update()

    def _handle_logout(self, e: Any) -> None:
        """Handle logout menu item click."""
        self.on_logout()
