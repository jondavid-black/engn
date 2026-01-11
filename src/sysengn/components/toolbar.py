"""Toolbar component for SysEngn application."""

from pathlib import Path
from typing import Callable, Optional

import flet as ft
from engn.pm import ProjectManager
from sysengn.auth import Role, User, update_user_theme_preference


class Toolbar(ft.Container):
    """The main application bar component for SysEngn.

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
    ):
        """Initialize the application bar."""
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
            # self.tabs_control.selected_index = index
            # try:
            #     self.tabs_control.update()
            # except Exception:
            #     pass
            # self.on_tab_change(index)

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
            on_select=on_project_change,
        )
        return project_dropdown

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

    def _build_content(self):
        # Left: Icon, Name, Project Dropdown, Workspace Dropdown
        self.project_dropdown = self._build_project_dropdown()

        workspace_dropdown = ft.Dropdown(
            width=200,
            text_size=14,
            content_padding=ft.Padding(10, 0, 10, 0),
            value="main",
            options=[
                ft.dropdown.Option("main"),
                ft.dropdown.Option("dev"),
                ft.dropdown.Option("test"),
                ft.dropdown.Option("+ Add New Workspace"),
            ],
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            border_radius=5,
        )

        left_section = ft.Row(
            controls=[
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
                self.project_dropdown,
                ft.Container(width=10),
                workspace_dropdown,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Right: Search, Theme Toggle, Avatar
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

        theme_icon = ft.IconButton(
            ft.Icons.DARK_MODE
            if self.page_ref.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE,
            on_click=self._toggle_theme,
            tooltip="Toggle Dark Mode",
            icon_color=ft.Colors.GREY_400,
        )

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

        terminal_icon = ft.IconButton(
            ft.Icons.TERMINAL,
            on_click=self._open_terminal,
            tooltip="Open Terminal",
            icon_color=ft.Colors.GREY_400,
        )

        avatar_menu = ft.PopupMenuButton(
            content=self.avatar_control,
            items=menu_items,
        )

        right_section = ft.Row(
            controls=[
                search_box,
                ft.Container(width=10),
                terminal_icon,
                ft.Container(width=5),
                theme_icon,
                ft.Container(width=10),
                avatar_menu,
            ],
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
