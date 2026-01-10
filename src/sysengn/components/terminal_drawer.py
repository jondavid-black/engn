"""Terminal drawer component for SysEngn application."""

from typing import Any

import flet as ft
from flet.controls.border import Border
from flet.controls.padding import Padding


class TerminalDrawer(ft.Container):
    """Right-side terminal drawer that can be toggled open/closed."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self._is_open = False

        # Terminal output area
        self.output_area = ft.ListView(
            controls=[
                ft.Text(
                    "SysEngn Terminal v1.0.0",
                    font_family="monospace",
                    color=ft.Colors.GREEN_400,
                ),
                ft.Text(
                    "Type 'help' for available commands.",
                    font_family="monospace",
                    color=ft.Colors.GREY_400,
                ),
                ft.Text("", font_family="monospace"),
                ft.Text(
                    "$ ",
                    font_family="monospace",
                    color=ft.Colors.GREEN_400,
                    spans=[
                        ft.TextSpan(
                            "Ready for input...",
                            style=ft.TextStyle(color=ft.Colors.GREY_500),
                        ),
                    ],
                ),
            ],
            spacing=2,
            padding=10,
            expand=True,
            auto_scroll=True,
        )

        # Command input
        self.command_input = ft.TextField(
            hint_text="Enter command...",
            prefix=ft.Text("$ ", font_family="monospace"),
            border=ft.InputBorder.NONE,
            filled=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            text_style=ft.TextStyle(font_family="monospace"),
            on_submit=self._handle_command,
            expand=True,
        )

        # Terminal header
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TERMINAL, size=18),
                    ft.Text("Terminal", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CLEAR_ALL,
                        tooltip="Clear",
                        icon_size=18,
                        on_click=self._clear_terminal,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        tooltip="Close",
                        icon_size=18,
                        on_click=self._close_drawer,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=Padding.symmetric(horizontal=12, vertical=8),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )

        # Input area container
        input_container = ft.Container(
            content=self.command_input,
            padding=Padding.symmetric(horizontal=10, vertical=5),
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        )

        self.content = ft.Column(
            controls=[
                header,
                ft.Divider(height=1),
                self.output_area,
                ft.Divider(height=1),
                input_container,
            ],
            spacing=0,
            expand=True,
        )

        self.width = 400
        self.bgcolor = ft.Colors.SURFACE_CONTAINER
        self.border = Border.only(left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT))
        self.visible = False
        self.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)

    @property
    def is_open(self) -> bool:
        """Return whether the drawer is open."""
        return self._is_open

    def toggle(self) -> None:
        """Toggle the drawer open/closed."""
        self._is_open = not self._is_open
        self.visible = self._is_open
        self.update()

    def open(self) -> None:
        """Open the drawer."""
        self._is_open = True
        self.visible = True
        self.update()

    def close(self) -> None:
        """Close the drawer."""
        self._is_open = False
        self.visible = False
        self.update()

    def _close_drawer(self, e: Any) -> None:
        """Handle close button click."""
        self.close()

    def _clear_terminal(self, e: Any) -> None:
        """Clear terminal output."""
        self.output_area.controls.clear()
        self._add_output("Terminal cleared.", ft.Colors.GREY_400)
        self.update()

    def _add_output(
        self,
        text: str,
        color: str = ft.Colors.WHITE,
        is_command: bool = False,
    ) -> None:
        """Add a line of output to the terminal."""
        if is_command:
            self.output_area.controls.append(
                ft.Text(
                    f"$ {text}",
                    font_family="monospace",
                    color=ft.Colors.GREEN_400,
                )
            )
        else:
            self.output_area.controls.append(
                ft.Text(text, font_family="monospace", color=color)
            )

    def _handle_command(self, e: Any) -> None:
        """Handle command submission."""
        command = self.command_input.value
        if not command or not command.strip():
            return

        command = command.strip()

        # Echo the command
        self._add_output(command, is_command=True)

        # Process command (mock implementation)
        response = self._process_command(command)
        self._add_output(response)

        # Clear input
        self.command_input.value = ""
        self.update()

    def _process_command(self, command: str) -> str:
        """Process a terminal command (mock implementation)."""
        cmd_lower = command.lower()

        if cmd_lower == "help":
            return (
                "Available commands:\n"
                "  help     - Show this help message\n"
                "  clear    - Clear the terminal\n"
                "  version  - Show version info\n"
                "  status   - Show project status\n"
                "  build    - Run build (mock)\n"
                "  test     - Run tests (mock)"
            )
        elif cmd_lower == "clear":
            self.output_area.controls.clear()
            return "Terminal cleared."
        elif cmd_lower == "version":
            return "SysEngn v0.1.0 - Model-Based System Engineering Tool"
        elif cmd_lower == "status":
            return (
                "Project: engn\n"
                "Branch: main\n"
                "Status: Clean working tree\n"
                "Last commit: Add toolbar and navigation"
            )
        elif cmd_lower == "build":
            return "Building project...\n[====] 100%\nBuild successful!"
        elif cmd_lower == "test":
            return (
                "Running tests...\n"
                "test_auth.py ... PASSED\n"
                "test_views.py ... PASSED\n"
                "All tests passed!"
            )
        else:
            return f"Unknown command: {command}\nType 'help' for available commands."
