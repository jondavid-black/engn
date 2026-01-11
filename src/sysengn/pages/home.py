import flet as ft
from pathlib import Path
from typing import Any, Optional, Callable

from engn.pm import ProjectManager
from engn.issue_tracker import IssueTracker
from engn.core.auth import update_user_default_project, User as EngnUser


class HomeDomainPage(ft.Row):
    """Home domain page with Project and Plan views."""

    def __init__(
        self,
        page: ft.Page,
        user: EngnUser,
        working_directory: Path,
        on_projects_changed: Optional[Callable[[], None]] = None,
    ):
        super().__init__()
        self.page_ref = page
        self.user = user
        self.working_directory = working_directory
        self.pm = ProjectManager(working_directory)
        self.on_projects_changed = on_projects_changed

        # Determine active project: either user's default or the first one found
        self.active_project_name = self.user.default_project
        projects = self.pm.list_projects()
        if not self.active_project_name and projects:
            self.active_project_name = projects[0]

        # UI Components
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER_OPEN_OUTLINED,
                    selected_icon=ft.Icons.FOLDER_OPEN,
                    label="Project",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ASSIGNMENT_OUTLINED,
                    selected_icon=ft.Icons.ASSIGNMENT,
                    label="Plan",
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

    def _update_view(self):
        if self.rail.selected_index == 0:
            self.content_area.content = self._build_project_view()
        else:
            self.content_area.content = self._build_plan_view()

    def _build_project_view(self):
        projects = self.pm.get_all_projects()

        project_cards = []
        for p in projects:
            is_default = self.user.default_project == p.name

            status_chips = []
            if p.is_git:
                status_chips.append(
                    ft.Chip(label=ft.Text("Git"), bgcolor=ft.Colors.BLUE_900)
                )
            if p.is_beads:
                status_chips.append(
                    ft.Chip(label=ft.Text("Beads"), bgcolor=ft.Colors.GREEN_900)
                )
            if p.is_initialized:
                status_chips.append(
                    ft.Chip(label=ft.Text("Engn"), bgcolor=ft.Colors.ORANGE_900)
                )

            project_cards.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.FOLDER),
                                    title=ft.Row(
                                        [
                                            ft.Text(p.name, weight=ft.FontWeight.BOLD),
                                            ft.Container(width=10),
                                            *status_chips,
                                        ]
                                    ),
                                    subtitle=ft.Column(
                                        [
                                            ft.Text(str(p.path), size=12),
                                            ft.Text(
                                                f"Git Status: {p.git_status}"
                                                if p.git_status
                                                else "No git status",
                                                size=10,
                                                italic=True,
                                            ),
                                        ]
                                    ),
                                    trailing=ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.Icons.STAR
                                                if is_default
                                                else ft.Icons.STAR_BORDER,
                                                icon_color=ft.Colors.YELLOW
                                                if is_default
                                                else None,
                                                tooltip="Set as default",
                                                on_click=lambda e,
                                                name=p.name: self._set_default_project(
                                                    name
                                                ),
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.PLAY_ARROW_OUTLINED,
                                                tooltip="Initialize project",
                                                visible=not p.is_initialized,
                                                on_click=lambda e,
                                                name=p.name: self._initialize_project(
                                                    name
                                                ),
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                tooltip="Delete project",
                                                on_click=lambda e,
                                                name=p.name: self._delete_project(name),
                                            ),
                                        ],
                                        tight=True,
                                    ),
                                )
                            ]
                        ),
                        padding=10,
                    )
                )
            )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Projects", size=30, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh projects",
                            on_click=lambda _: (
                                self._update_view(),
                                self.on_projects_changed()
                                if self.on_projects_changed
                                else None,
                                self.update(),
                            ),
                        ),
                        ft.Container(expand=True),
                        ft.FilledButton(
                            content="New Project",
                            icon=ft.Icons.ADD,
                            on_click=self._show_new_project_dialog,
                        ),
                        ft.FilledButton(
                            content="Clone Project",
                            icon=ft.Icons.DOWNLOAD,
                            on_click=self._show_clone_project_dialog,
                        ),
                    ]
                ),
                ft.Divider(),
                ft.ListView(controls=project_cards, expand=True, spacing=10),
            ],
            expand=True,
        )

    def _build_plan_view(self):
        if not self.active_project_name:
            return ft.Container(
                content=ft.Text("No active project selected. Go to Projects tab."),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )

        project_path = self.working_directory / self.active_project_name
        tracker = IssueTracker(project_path)

        try:
            open_issues = tracker.list_issues(status="open")
            in_progress_issues = tracker.list_issues(status="in_progress")
            closed_issues = tracker.list_issues(status="closed")
        except Exception as e:
            return ft.Container(
                content=ft.Text(f"Error loading issues: {e}"),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )

        def create_column(title, issues):
            cards = []
            for issue in issues:
                cards.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(issue["title"], weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"ID: {issue['id']}",
                                        size=12,
                                        color=ft.Colors.GREY_500,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Chip(
                                                label=ft.Text(issue["issue_type"]),
                                                height=20,
                                            ),
                                            ft.Container(expand=True),
                                            ft.Text(f"P{issue['priority']}", size=12),
                                        ]
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=10,
                        )
                    )
                )

            return ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            f"{title} ({len(issues)})",
                            weight=ft.FontWeight.BOLD,
                            size=18,
                        ),
                        ft.Divider(),
                        ft.ListView(controls=cards, spacing=10, expand=True),
                    ],
                    expand=True,
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                padding=10,
                border_radius=10,
                expand=True,
            )

        return ft.Column(
            [
                ft.Text(
                    f"Plan: {self.active_project_name}",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),
                ft.Row(
                    [
                        create_column("To Do", open_issues),
                        create_column("In Progress", in_progress_issues),
                        create_column("Done", closed_issues),
                    ],
                    spacing=20,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _set_default_project(self, project_name: Optional[str]):
        update_user_default_project(self.user.id, project_name)
        self.user.default_project = project_name
        if project_name:
            self.active_project_name = project_name

        # Update session store
        if self.page_ref:
            store: Any = getattr(self.page_ref.session, "store", self.page_ref.session)
            store.set("user", self.user)

        self._update_view()
        self.update()

    def _delete_project(self, project_name: str):
        def confirm_delete(e):
            try:
                self.pm.delete_project(project_name)
                if self.user.default_project == project_name:
                    self._set_default_project(None)
                if self.active_project_name == project_name:
                    projects = self.pm.list_projects()
                    self.active_project_name = projects[0] if projects else None
                self._update_view()
                if self.on_projects_changed:
                    self.on_projects_changed()
                self.update()
            except Exception as ex:
                self.page_ref.overlay.append(
                    ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
                )
                self.page_ref.update()
            finally:
                dialog.open = False
                self.page_ref.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(
                f"Are you sure you want to delete project '{project_name}'?"
            ),
            actions=[
                ft.TextButton(
                    content="Cancel", on_click=lambda e: setattr(dialog, "open", False)
                ),
                ft.TextButton(
                    content="Delete",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                ),
            ],
        )
        self.page_ref.overlay.append(dialog)
        dialog.open = True
        self.page_ref.update()

    def _initialize_project(self, project_name: str):
        try:
            self.pm.initialize_project(project_name)
            self.page_ref.overlay.append(
                ft.SnackBar(
                    ft.Text(f"Project '{project_name}' initialized successfully"),
                    open=True,
                )
            )
            self._update_view()
            self.update()
        except Exception as ex:
            self.page_ref.overlay.append(
                ft.SnackBar(ft.Text(f"Error initializing project: {ex}"), open=True)
            )
            self.page_ref.update()

    def _show_new_project_dialog(self, e):
        name_field = ft.TextField(label="Project Name", hint_text="my-new-project")

        def create_project(e):
            name = name_field.value
            if not name:
                return
            try:
                self.pm.new_project(name)
                self._update_view()
                if self.on_projects_changed:
                    self.on_projects_changed()
                self.update()
                dialog.open = False
            except Exception as ex:
                self.page_ref.overlay.append(
                    ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
                )
            self.page_ref.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Create New Project"),
            content=ft.Column(
                [
                    ft.Text("Create a new project from scratch."),
                    name_field,
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton(
                    content="Cancel", on_click=lambda e: setattr(dialog, "open", False)
                ),
                ft.TextButton(content="Create", on_click=create_project),
            ],
        )
        self.page_ref.overlay.append(dialog)
        dialog.open = True
        self.page_ref.update()

    def _show_clone_project_dialog(self, e):
        repo_url_field = ft.TextField(
            label="Git Repository URL", hint_text="https://github.com/user/repo.git"
        )

        def clone_project(e):
            url = repo_url_field.value
            if not url:
                return
            try:
                self.pm.create_project(url)
                self._update_view()
                if self.on_projects_changed:
                    self.on_projects_changed()
                self.update()
                dialog.open = False
            except Exception as ex:
                self.page_ref.overlay.append(
                    ft.SnackBar(ft.Text(f"Error: {ex}"), open=True)
                )
            self.page_ref.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Clone Project"),
            content=ft.Column(
                [
                    ft.Text("Clone a git repository to create a new project."),
                    repo_url_field,
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton(
                    content="Cancel", on_click=lambda e: setattr(dialog, "open", False)
                ),
                ft.TextButton(content="Clone", on_click=clone_project),
            ],
        )
        self.page_ref.overlay.append(dialog)
        dialog.open = True
        self.page_ref.update()
