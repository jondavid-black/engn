"""Home/Project page component for Flet applications.

This module provides a reusable home page with project management
and planning views that can be used across sysengn, projengn,
and other engn applications.
"""

import flet as ft
from pathlib import Path
from typing import Optional, Callable

from engn.pm import ProjectManager
from engn.core.auth import User
from engn.core.context import get_app_context
from engn.ui.project_view import ProjectView
from engn.ui.plan_view import PlanView


class HomeDomainPage(ft.Row):
    """Home domain page with Project and Plan views."""

    def __init__(
        self,
        page: ft.Page,
        user: User,
        working_directory: Path,
        on_projects_changed: Optional[Callable[[], None]] = None,
    ):
        """Initialize the home domain page.

        Args:
            page: Reference to the main Flet page.
            user: The current authenticated user.
            working_directory: Working directory for project management.
            on_projects_changed: Optional callback when projects list changes.
        """
        super().__init__()
        self.page_ref = page
        self.user = user
        self.working_directory = working_directory
        self.pm = ProjectManager(working_directory)
        self.on_projects_changed = on_projects_changed

        self.app_context = get_app_context(self.page_ref)
        self.app_context.subscribe(self._on_context_change)

        # Determine active project: either context, user's default or the first one found
        self.active_project_name = (
            self.app_context.active_project_id or self.user.default_project
        )
        projects = self.pm.list_projects()
        if not self.active_project_name and projects:
            self.active_project_name = projects[0]
            self.app_context.active_project_id = self.active_project_name

        # UI Components
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.ASSIGNMENT_OUTLINED,
                    selected_icon=ft.Icons.ASSIGNMENT,
                    label="Plan",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER_OPEN_OUTLINED,
                    selected_icon=ft.Icons.FOLDER_OPEN,
                    label="Project",
                ),
            ],
            on_change=self._on_rail_change,
        )

        self.content_area = ft.Container(expand=True, padding=20)

        self.controls = [
            self.rail,
            ft.VerticalDivider(width=1),
            self.content_area,
        ]
        self.expand = True

        self._update_view()

    def _on_rail_change(self, e):
        self._update_view()
        self.update()

    def _on_context_change(self, context):
        """Handle context changes."""
        if self.active_project_name != context.active_project_id:
            self.active_project_name = context.active_project_id
            self._update_view()
            self.update()

    def _on_project_selected(self, project_name: str):
        self.app_context.active_project_id = project_name

    def _update_view(self):
        if self.rail.selected_index == 0:
            self.content_area.content = PlanView(
                page=self.page_ref,
                project_name=self.active_project_name,
                working_directory=self.working_directory,
            )
        else:
            self.content_area.content = ProjectView(
                page=self.page_ref,
                user=self.user,
                pm=self.pm,
                on_project_selected=self._on_project_selected,
                on_projects_changed=self.on_projects_changed,
            )

    def refresh(self):
        """Refresh the current view."""
        if hasattr(self.content_area.content, "refresh"):
            self.content_area.content.refresh()  # type: ignore
        self.update()
