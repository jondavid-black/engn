"""UI component for project management view."""

import flet as ft
from typing import Any, Optional, Callable

from engn.pm import ProjectManager
from engn.core.auth import update_user_default_project, User


class ProjectView(ft.Column):
    """Component for listing and managing projects."""

    def __init__(
        self,
        page: ft.Page,
        user: User,
        pm: ProjectManager,
        on_project_selected: Callable[[str], None],
        on_projects_changed: Optional[Callable[[], None]] = None,
    ):
        super().__init__(expand=True)
        self.page_ref = page
        self.user = user
        self.pm = pm
        self.on_project_selected = on_project_selected
        self.on_projects_changed = on_projects_changed
        self.controls = self._build_view()

    def _build_view(self) -> list[ft.Control]:
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
                                            ft.Row(
                                                [
                                                    ft.Icon(
                                                        ft.Icons.CHECK_CIRCLE_OUTLINE
                                                        if p.git_status == "clean"
                                                        else ft.Icons.ERROR_OUTLINE,
                                                        size=14,
                                                        color=ft.Colors.GREEN
                                                        if p.git_status == "clean"
                                                        else ft.Colors.AMBER,
                                                    )
                                                    if p.is_git
                                                    else ft.Container(),
                                                    ft.Text(
                                                        "Clean"
                                                        if p.git_status == "clean"
                                                        else f"{p.git_modified} modified, {p.git_untracked} untracked"
                                                        if p.is_git
                                                        else "Not a git repo",
                                                        size=10,
                                                        color=ft.Colors.GREEN
                                                        if p.git_status == "clean"
                                                        else ft.Colors.AMBER
                                                        if p.is_git
                                                        else ft.Colors.GREY_400,
                                                    ),
                                                    ft.Container(width=15)
                                                    if p.is_beads
                                                    else ft.Container(),
                                                    ft.Icon(
                                                        ft.Icons.BUG_REPORT_OUTLINED,
                                                        size=14,
                                                        color=ft.Colors.RED_300,
                                                    )
                                                    if p.is_beads and p.beads_bugs > 0
                                                    else ft.Container(),
                                                    ft.Text(
                                                        f"{p.beads_bugs}",
                                                        size=10,
                                                        color=ft.Colors.RED_300,
                                                    )
                                                    if p.is_beads and p.beads_bugs > 0
                                                    else ft.Container(),
                                                    ft.Icon(
                                                        ft.Icons.LIGHTBULB_OUTLINED,
                                                        size=14,
                                                        color=ft.Colors.BLUE_300,
                                                    )
                                                    if p.is_beads
                                                    and p.beads_features > 0
                                                    else ft.Container(),
                                                    ft.Text(
                                                        f"{p.beads_features}",
                                                        size=10,
                                                        color=ft.Colors.BLUE_300,
                                                    )
                                                    if p.is_beads
                                                    and p.beads_features > 0
                                                    else ft.Container(),
                                                    ft.Icon(
                                                        ft.Icons.TASK_OUTLINED,
                                                        size=14,
                                                        color=ft.Colors.GREEN_300,
                                                    )
                                                    if p.is_beads and p.beads_tasks > 0
                                                    else ft.Container(),
                                                    ft.Text(
                                                        f"{p.beads_tasks}",
                                                        size=10,
                                                        color=ft.Colors.GREEN_300,
                                                    )
                                                    if p.is_beads and p.beads_tasks > 0
                                                    else ft.Container(),
                                                ],
                                                spacing=5,
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

        return [
            ft.Row(
                [
                    ft.Text("Projects", size=30, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh projects",
                        on_click=lambda _: self.refresh(),
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
        ]

    def _set_default_project(self, project_name: Optional[str]):
        update_user_default_project(self.user.id, project_name)
        self.user.default_project = project_name
        if project_name:
            self.on_project_selected(project_name)

        if self.page_ref:
            store: Any = getattr(self.page_ref.session, "store", self.page_ref.session)
            store.set("user", self.user)

        self.refresh()

    def _delete_project(self, project_name: str):
        def confirm_delete(e):
            try:
                self.pm.delete_project(project_name)
                if self.user.default_project == project_name:
                    self._set_default_project(None)
                if self.on_projects_changed:
                    self.on_projects_changed()
                self.refresh()
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
            self.refresh()
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
                if self.on_projects_changed:
                    self.on_projects_changed()
                self.refresh()
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
                if self.on_projects_changed:
                    self.on_projects_changed()
                self.refresh()
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

    def refresh(self):
        self.controls = self._build_view()
        self.update()
