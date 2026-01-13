"""UI component for project planning view (board and backlog)."""

import flet as ft
from pathlib import Path
from typing import Optional

from engn.issue_tracker import IssueTracker
from engn.core.context import get_app_context


class PlanView(ft.Column):
    """Component for project planning (board and backlog)."""

    def __init__(
        self,
        page: ft.Page,
        project_name: Optional[str],
        working_directory: Path,
    ):
        super().__init__(expand=True)
        self.page_ref = page
        self.working_directory = working_directory
        self.view_type = "board"  # "board" or "backlog"

        self.app_context = get_app_context(self.page_ref)
        # Use context project name if provided name is None
        self.project_name = project_name or self.app_context.active_project_id

        self.app_context.subscribe(self._on_context_change)
        self.controls = self._build_view()

    def _on_context_change(self, context):
        """Handle context changes by updating the active project."""
        if self.project_name != context.active_project_id:
            self.project_name = context.active_project_id
            self.refresh()

    def _build_view(self) -> list[ft.Control]:
        if not self.project_name:
            return [
                ft.Container(
                    content=ft.Text("No active project selected. Go to Projects tab."),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                )
            ]

        project_path = self.working_directory / self.project_name
        tracker = IssueTracker(project_path)

        try:
            # Get all issues for the project
            all_issues = tracker.list_issues(status="all", limit=200)
            open_issues = [i for i in all_issues if i.get("status") == "open"]
            in_progress_issues = [
                i for i in all_issues if i.get("status") == "in_progress"
            ]
            closed_issues = [i for i in all_issues if i.get("status") == "closed"]
        except Exception as e:
            return [
                ft.Container(
                    content=ft.Text(f"Error loading issues: {e}"),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                )
            ]

        def on_view_change(e):
            # FIX: Ensure we use strings and check correctly
            selected = e.control.selected
            if isinstance(selected, (set, list)) and len(selected) > 0:
                val = list(selected)[0]
                self.view_type = str(val)
            self.refresh()

        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            f"Plan: {self.project_name}",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Manage project backlog and board",
                            size=14,
                            color=ft.Colors.GREY_500,
                        ),
                    ]
                ),
                ft.Container(expand=True),
                ft.SegmentedButton(
                    selected=[self.view_type],
                    allow_empty_selection=False,
                    allow_multiple_selection=False,
                    segments=[
                        ft.Segment(
                            value="board",
                            label=ft.Text("Board"),
                            icon=ft.Icon(ft.Icons.VIEW_KANBAN_OUTLINED),
                        ),
                        ft.Segment(
                            value="backlog",
                            label=ft.Text("Backlog"),
                            icon=ft.Icon(ft.Icons.LIST_ALT_OUTLINED),
                        ),
                    ],
                    on_change=on_view_change,
                ),
                ft.VerticalDivider(),
                ft.FilledButton(
                    "Create",
                    icon=ft.Icons.ADD,
                    on_click=self._show_new_issue_dialog,
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    on_click=lambda _: self.refresh(),
                    tooltip="Refresh",
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )

        content = (
            self._build_kanban_board(open_issues, in_progress_issues, closed_issues)
            if self.view_type == "board"
            else self._build_backlog_list(all_issues)
        )

        return [
            header,
            ft.Divider(),
            content,
        ]

    def _build_kanban_board(self, todo, in_progress, done) -> ft.Control:
        project_name = self.project_name or ""

        def update_issue_status(issue_id, new_status):
            project_path = self.working_directory / project_name
            tracker = IssueTracker(project_path)
            try:
                tracker.update_status(issue_id, new_status)
                self.refresh()
            except Exception as e:
                self.page_ref.overlay.append(
                    ft.SnackBar(ft.Text(f"Error updating status: {e}"), open=True)
                )
                self.page_ref.update()

        def create_column(title, issues, target_status):
            cards = []
            for issue in issues:
                # Type icon and color
                type_icon = ft.Icons.TASK_ALT
                type_color = ft.Colors.BLUE_400
                if issue.get("issue_type") == "bug":
                    type_icon = ft.Icons.BUG_REPORT
                    type_color = ft.Colors.RED_400
                elif issue.get("issue_type") == "feature":
                    type_icon = ft.Icons.LIGHTBULB
                    type_color = ft.Colors.GREEN_400

                # Status transition buttons
                actions = []
                if issue.get("status") != "open":
                    actions.append(
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_size=16,
                            tooltip="Move to To Do",
                            on_click=lambda e, id=issue["id"]: update_issue_status(
                                id, "open"
                            ),
                        )
                    )
                if issue.get("status") != "in_progress":
                    actions.append(
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            icon_size=16,
                            tooltip="Start Progress",
                            on_click=lambda e, id=issue["id"]: update_issue_status(
                                id, "in_progress"
                            ),
                        )
                    )
                if issue.get("status") != "closed":
                    actions.append(
                        ft.IconButton(
                            icon=ft.Icons.CHECK,
                            icon_size=16,
                            tooltip="Close Issue",
                            on_click=lambda e, id=issue["id"]: update_issue_status(
                                id, "closed"
                            ),
                        )
                    )

                cards.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(
                                                type_icon, color=type_color, size=16
                                            ),
                                            ft.Text(
                                                issue["id"],
                                                size=10,
                                                color=ft.Colors.GREY_500,
                                            ),
                                            ft.Container(expand=True),
                                            ft.Text(
                                                f"P{issue.get('priority', 2)}",
                                                size=10,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.AMBER_700
                                                if issue.get("priority", 2) <= 1
                                                else ft.Colors.GREY_500,
                                            ),
                                        ],
                                        spacing=5,
                                    ),
                                    ft.Text(
                                        issue.get("title", ""),
                                        weight=ft.FontWeight.W_500,
                                        size=14,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Row(
                                        actions,
                                        spacing=0,
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=10,
                        ),
                        elevation=1,
                    )
                )

            return ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                                ft.Container(
                                    content=ft.Text(
                                        str(len(issues)),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                                    padding=ft.Padding(8, 2, 8, 2),
                                    border_radius=10,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(height=1, thickness=1),
                        ft.ListView(
                            controls=cards,
                            spacing=10,
                            expand=True,
                            padding=ft.Padding(0, 10, 0, 0),
                        ),
                    ],
                    expand=True,
                ),
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                padding=10,
                border_radius=8,
                expand=True,
            )

        return ft.Row(
            [
                create_column("TO DO", todo, "open"),
                create_column("IN PROGRESS", in_progress, "in_progress"),
                create_column("DONE", done, "closed"),
            ],
            spacing=15,
            expand=True,
        )

    def _build_backlog_list(self, issues) -> ft.Control:
        # Sort issues: open first, then by priority
        sorted_issues = sorted(
            issues,
            key=lambda x: (0 if x.get("status") == "open" else 1, x.get("priority", 2)),
        )

        rows = []
        for issue in sorted_issues:
            type_icon = ft.Icons.TASK_ALT
            type_color = ft.Colors.BLUE_400
            if issue.get("issue_type") == "bug":
                type_icon = ft.Icons.BUG_REPORT
                type_color = ft.Colors.RED_400
            elif issue.get("issue_type") == "feature":
                type_icon = ft.Icons.LIGHTBULB
                type_color = ft.Colors.GREEN_400

            status_color = ft.Colors.GREY_500
            if issue.get("status") == "in_progress":
                status_color = ft.Colors.BLUE_400
            elif issue.get("status") == "closed":
                status_color = ft.Colors.GREEN_400

            rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(type_icon, color=type_color, size=20),
                            ft.Text(
                                issue.get("id", ""),
                                width=80,
                                size=12,
                                color=ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                issue.get("title", ""),
                                expand=True,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.GREY_200
                                if issue.get("status") == "closed"
                                else None,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(issue.get("status", ""))
                                    .upper()
                                    .replace("_", " "),
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=status_color,
                                ),
                                border=ft.Border.all(1, status_color),
                                border_radius=4,
                                padding=ft.Padding(8, 2, 8, 2),
                                width=100,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text(
                                f"P{issue.get('priority', 2)}",
                                width=40,
                                size=12,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        spacing=15,
                    ),
                    padding=ft.Padding(12, 8, 12, 8),
                    border=ft.Border.only(
                        bottom=ft.BorderSide(1, ft.Colors.SURFACE_CONTAINER_HIGHEST)
                    ),
                )
            )

        return ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=20),  # icon
                            ft.Text("ID", width=80, size=12, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                "SUMMARY",
                                expand=True,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "STATUS",
                                width=100,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "PRIO",
                                width=40,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        spacing=15,
                    ),
                    padding=ft.Padding(12, 8, 12, 8),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                ),
                ft.ListView(
                    controls=rows,
                    expand=True,
                    spacing=0,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _show_new_issue_dialog(self, e):
        if not self.project_name:
            return

        active_project = self.project_name
        title_field = ft.TextField(label="Title", autofocus=True)
        desc_field = ft.TextField(label="Description", multiline=True, min_lines=3)
        type_dropdown = ft.Dropdown(
            label="Type",
            options=[
                ft.dropdown.Option("task"),
                ft.dropdown.Option("bug"),
                ft.dropdown.Option("feature"),
            ],
            value="task",
        )
        priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option("0", "P0 - Critical"),
                ft.dropdown.Option("1", "P1 - High"),
                ft.dropdown.Option("2", "P2 - Medium"),
                ft.dropdown.Option("3", "P3 - Low"),
                ft.dropdown.Option("4", "P4 - Backlog"),
            ],
            value="2",
        )

        def create_issue(e):
            if not title_field.value:
                try:
                    setattr(title_field, "error_text", "Title is required")
                except Exception:
                    pass
                title_field.update()
                return

            project_path = self.working_directory / active_project
            tracker = IssueTracker(project_path)
            try:
                issue_type = str(type_dropdown.value) if type_dropdown.value else "task"
                priority = (
                    int(priority_dropdown.value) if priority_dropdown.value else 2
                )

                tracker.create_issue(
                    title=str(title_field.value),
                    description=str(desc_field.value) if desc_field.value else None,
                    issue_type=issue_type,
                    priority=priority,
                )
                dialog.open = False
                self.refresh()
            except Exception as ex:
                self.page_ref.overlay.append(
                    ft.SnackBar(ft.Text(f"Error creating issue: {ex}"), open=True)
                )
            self.page_ref.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Create New Issue"),
            content=ft.Column(
                [
                    title_field,
                    desc_field,
                    ft.Row([type_dropdown, priority_dropdown], spacing=10),
                ],
                tight=True,
                width=500,
            ),
            actions=[
                ft.TextButton(
                    "Cancel", on_click=lambda _: setattr(dialog, "open", False)
                ),
                ft.ElevatedButton("Create", on_click=create_issue),
            ],
        )

        self.page_ref.overlay.append(dialog)
        dialog.open = True
        self.page_ref.update()

    def refresh(self):
        self.controls = self._build_view()
        self.update()
