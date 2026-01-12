"""Toolbar component for Flet applications.

This module provides a reusable toolbar/app bar that can be used across
sysengn, projengn, and other engn applications.
"""

from pathlib import Path
from typing import Callable, Optional

import flet as ft
from engn.pm import ProjectManager
from engn.core.auth import Role, User, update_user_theme_preference


class Toolbar(ft.Container):
    """The main application bar component.

    This component provides navigation tabs, user profile access, project selection,
    and global actions like theme toggling and search.
    """

    def __init__(
        self,
        page: ft.Page,
        user: User,
        logo_path: str,
        on_tab_change: Callable[[int], None],
        tabs: list[str],
        on_logout: Callable[[], None],
        on_profile: Callable[[], None],
        working_directory: Optional[Path] = None,
        on_admin: Optional[Callable[[], None]] = None,
        on_toggle_terminal: Optional[Callable[[], None]] = None,
        show_project_dropdown: bool = True,
        show_branch_dropdown: bool = True,
        show_search: bool = True,
    ):
        """Initialize the application bar.

        Args:
            page: Reference to the main Flet page.
            user: The current authenticated user.
            logo_path: Path to the logo image asset.
            on_tab_change: Callback when navigation tab changes.
            tabs: List of tab labels.
            on_logout: Callback when user logs out.
            on_profile: Callback when user opens profile.
            working_directory: Working directory for project management.
            on_admin: Optional callback for admin panel access.
            on_toggle_terminal: Optional callback to toggle terminal.
            show_project_dropdown: Whether to show project dropdown.
            show_branch_dropdown: Whether to show branch dropdown.
            show_search: Whether to show search box.
        """
        super().__init__()
        self.page_ref = page
        self.user = user
        self.on_tab_change = on_tab_change
        self.tabs_list = tabs
        self.on_logout = on_logout
        self.on_profile = on_profile
        self.on_admin = on_admin
        self.logo_path = logo_path
        self.on_toggle_terminal = on_toggle_terminal
        self.working_directory = working_directory or Path.cwd()
        self.show_project_dropdown = show_project_dropdown
        self.show_branch_dropdown = show_branch_dropdown
        self.show_search = show_search

        # Exposed controls
        self.tabs_control = self._build_tabs()
        self.avatar_control = self._build_avatar()

        # Build the UI
        self._build_content()

    def select_tab(self, index: int):
        """Programmatically select a tab by index."""
        print(f"Selecting tab index: {index}")
        self.tabs_control.selected_index = index
        try:
            self.tabs_control.update()
        except Exception:
            print(f"Failed to update tabs_control for index {index}")
            pass
        self.on_tab_change(index)

    def _build_tabs(self) -> ft.Tabs:
        def on_tab_click(e):
            index = int(e.data)
            self.select_tab(index)

        tab_bar = ft.TabBar(
            tabs=[ft.Tab(label=name) for name in self.tabs_list],
            indicator_color=ft.Colors.BLUE_200,
            label_color=ft.Colors.BLUE_200,
            unselected_label_color=ft.Colors.GREY_400,
            divider_color="transparent",
            on_click=on_tab_click,
        )

        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            length=len(self.tabs_list),
            content=tab_bar,
        )

    def _build_avatar(self) -> ft.CircleAvatar:
        user_initials = (
            self.user.name[0].upper() if self.user.name else self.user.email[0].upper()
        )

        # If user has first and last name, show those initials
        if self.user.first_name and self.user.last_name:
            user_initials = (
                f"{self.user.first_name[0].upper()}{self.user.last_name[0].upper()}"
            )

        return ft.CircleAvatar(
            content=ft.Text(user_initials, color=ft.Colors.WHITE),
            bgcolor=self.user.preferred_color
            if self.user.preferred_color
            else ft.Colors.BLUE,
            tooltip=f"{self.user.name or self.user.email}",
        )

    def _build_project_dropdown(self) -> ft.Dropdown:
        # Initialize ProjectManager with working directory
        pm = ProjectManager(self.working_directory)
        projects = pm.get_all_projects()

        project_options = [ft.dropdown.Option(key=p.id, text=p.name) for p in projects]

        # Set default active project to first available, or empty if none
        initial_project_id = projects[0].id if projects else None

        # Only override session if not already set or invalid
        session = getattr(self.page_ref, "session", None)

        active_project_id = initial_project_id
        if session:
            # Modern Flet session access via .store
            store = getattr(session, "store", session)
            current_session_project = store.get("current_project_id")
            if not current_session_project and initial_project_id:
                store.set("current_project_id", initial_project_id)
            elif current_session_project:
                # Validate it still exists
                if not any(p.id == current_session_project for p in projects):
                    store.set("current_project_id", initial_project_id)
            active_project_id = store.get("current_project_id")

        def on_project_change(e):
            selected_id = e.control.value
            if selected_id and session:
                store = getattr(session, "store", session)
                store.set("current_project_id", selected_id)
                # Refresh current view if it depends on project
                project_dropdown.update()

                # Refresh branches
                self.refresh_branches()

                # If currently on MBSE screen (index 1), we might want to refresh content area
                current_tab_idx = self.tabs_control.selected_index or 0

                # Assuming standard tabs: Home, MBSE, UX, Docs
                # If "MBSE" is in tabs list and selected
                if (
                    current_tab_idx < len(self.tabs_list)
                    and self.tabs_list[current_tab_idx] == "MBSE"
                ):
                    self.on_tab_change(current_tab_idx)

        project_dropdown = ft.Dropdown(
            width=200,
            text_size=14,
            content_padding=ft.Padding(10, 0, 10, 0),
            # Default to active project
            value=active_project_id,
            options=project_options,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            border_radius=5,
            leading_icon=ft.Icons.FOLDER_OPEN,
            tooltip="Select Active Project",
        )
        project_dropdown.on_select = on_project_change
        return project_dropdown

    def _build_branch_dropdown(self) -> ft.Dropdown:
        pm = ProjectManager(self.working_directory)

        session = getattr(self.page_ref, "session", None)
        active_project_id = None
        if session:
            store = getattr(session, "store", session)
            active_project_id = store.get("current_project_id")

        branches = []
        if active_project_id:
            try:
                branches = pm.list_branches(active_project_id)
            except Exception:
                pass

        branch_options = [ft.dropdown.Option(b) for b in branches]

        def on_branch_change(e):
            selected_branch = e.control.value
            if selected_branch and active_project_id:
                try:
                    pm.checkout_branch(active_project_id, selected_branch)
                    self.page_ref.overlay.append(
                        ft.SnackBar(
                            ft.Text(f"Switched to branch: {selected_branch}"), open=True
                        )
                    )
                    self.page_ref.update()
                except Exception as ex:
                    self.page_ref.overlay.append(
                        ft.SnackBar(ft.Text(f"Error switching branch: {ex}"), open=True)
                    )
                    self.page_ref.update()

        branch_dropdown = ft.Dropdown(
            width=200,
            text_size=14,
            content_padding=ft.Padding(10, 0, 10, 0),
            options=branch_options,
            value=branches[0] if branches else None,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            border_radius=5,
            leading_icon=ft.Icons.ACCOUNT_TREE_OUTLINED,
            tooltip="Select Branch",
        )
        branch_dropdown.on_select = on_branch_change
        return branch_dropdown

    def refresh_branches(self):
        """Refresh the branch list in the dropdown."""
        if not self.show_branch_dropdown:
            return

        pm = ProjectManager(self.working_directory)
        session = getattr(self.page_ref, "session", None)
        active_project_id = None
        if session:
            store = getattr(session, "store", session)
            active_project_id = store.get("current_project_id")

        branches = []
        if active_project_id:
            try:
                branches = pm.list_branches(active_project_id)
            except Exception:
                pass

        self.branch_dropdown.options = [ft.dropdown.Option(b) for b in branches]
        self.branch_dropdown.value = branches[0] if branches else None
        self.branch_dropdown.update()

    def _toggle_theme(self, e):
        new_mode = (
            ft.ThemeMode.LIGHT
            if self.page_ref.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        self.page_ref.theme_mode = new_mode
        e.control.icon = (
            ft.Icons.DARK_MODE
            if self.page_ref.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE
        )
        self.page_ref.update()

        # Update preference in DB and session
        self.user.theme_preference = (
            "LIGHT" if new_mode == ft.ThemeMode.LIGHT else "DARK"
        )
        update_user_theme_preference(self.user.id, self.user.theme_preference)

    def _open_terminal(self, e):
        if self.on_toggle_terminal:
            self.on_toggle_terminal()
        else:
            # Fallback for now if not provided
            print("Terminal toggle callback not provided")

    def refresh_projects(self):
        """Refresh the project list in the dropdown."""
        if not self.show_project_dropdown:
            return

        pm = ProjectManager(self.working_directory)
        projects = pm.get_all_projects()
        self.project_dropdown.options = [
            ft.dropdown.Option(key=p.id, text=p.name) for p in projects
        ]

        # Check if current value is still valid
        if self.project_dropdown.value and not any(
            p.id == self.project_dropdown.value for p in projects
        ):
            self.project_dropdown.value = projects[0].id if projects else None

        self.project_dropdown.update()

    def refresh_avatar(self):
        """Refresh the avatar display after profile changes."""
        user_initials = (
            self.user.name[0].upper() if self.user.name else self.user.email[0].upper()
        )

        # If user has first and last name, show those initials
        if self.user.first_name and self.user.last_name:
            user_initials = (
                f"{self.user.first_name[0].upper()}{self.user.last_name[0].upper()}"
            )

        self.avatar_control.content = ft.Text(user_initials, color=ft.Colors.WHITE)
        self.avatar_control.bgcolor = (
            self.user.preferred_color if self.user.preferred_color else ft.Colors.BLUE
        )
        self.avatar_control.tooltip = f"{self.user.name or self.user.email}"
        self.avatar_control.update()

    def _build_content(self):
        # Left section controls
        left_controls: list[ft.Control] = [
            ft.Container(
                content=ft.Image(
                    src=self.logo_path,
                    width=55,
                    height=45,
                    tooltip="Go to Home",
                ),
                on_click=lambda _: self.select_tab(0),
            ),
            ft.Container(width=10),
        ]

        if self.show_project_dropdown:
            self.project_dropdown = self._build_project_dropdown()
            left_controls.append(self.project_dropdown)
            left_controls.append(ft.Container(width=10))

        if self.show_branch_dropdown:
            self.branch_dropdown = self._build_branch_dropdown()
            left_controls.append(self.branch_dropdown)

        left_section = ft.Row(
            controls=left_controls,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Right section controls
        right_controls: list[ft.Control] = []

        if self.show_search:
            search_box = ft.TextField(
                hint_text="Search...",
                height=40,
                text_size=14,
                content_padding=ft.Padding(10, 0, 0, 10),
                width=200,
                border_radius=20,
                prefix_icon=ft.Icons.SEARCH,
                bgcolor=ft.Colors.GREY_800,
                border_color=ft.Colors.TRANSPARENT,
                color=ft.Colors.WHITE,
                hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
            )
            right_controls.append(search_box)
            right_controls.append(ft.Container(width=10))

        if self.on_toggle_terminal:
            terminal_icon = ft.IconButton(
                ft.Icons.TERMINAL,
                on_click=self._open_terminal,
                tooltip="Open Terminal",
                icon_color=ft.Colors.GREY_400,
            )
            right_controls.append(terminal_icon)
            right_controls.append(ft.Container(width=5))

        theme_icon = ft.IconButton(
            ft.Icons.DARK_MODE
            if self.page_ref.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE,
            on_click=self._toggle_theme,
            tooltip="Toggle Dark Mode",
            icon_color=ft.Colors.GREY_400,
        )
        right_controls.append(theme_icon)
        right_controls.append(ft.Container(width=10))

        # Avatar Menu (Logout, Admin)
        menu_items = [
            ft.PopupMenuItem(
                content=ft.Text("Profile"),
                icon=ft.Icons.PERSON,
                on_click=lambda e: self.on_profile(),
            )
        ]

        if self.user.has_role(Role.ADMIN) and self.on_admin is not None:
            # Local capture for type safety in lambda
            on_admin_func = self.on_admin
            menu_items.append(
                ft.PopupMenuItem(
                    content=ft.Text("Admin Panel"),
                    icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                    on_click=lambda e: on_admin_func(),
                )
            )

        menu_items.append(
            ft.PopupMenuItem(
                content=ft.Text("Logout"),
                icon=ft.Icons.LOGOUT,
                on_click=lambda e: self.on_logout(),
            )
        )

        avatar_menu = ft.PopupMenuButton(
            content=self.avatar_control,
            items=menu_items,
        )
        right_controls.append(avatar_menu)

        right_section = ft.Row(
            controls=right_controls,
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        center_section = ft.Row(
            controls=[
                ft.Container(width=10),
                self.tabs_control,
                ft.Container(width=10),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        banner_row = ft.Row(
            controls=[
                ft.Container(content=left_section),
                ft.Container(content=center_section),
                ft.Container(content=right_section),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.content = banner_row
        self.padding = ft.Padding(20, 10, 20, 10)
        self.bgcolor = "#36454F"  # Charcoal
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.Colors.BLACK_12,
            offset=ft.Offset(0, 2),
        )
