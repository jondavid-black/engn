import argparse
import sys
from pathlib import Path
from typing import cast

import flet as ft
from engn.utils import get_version


from engn.pm import ProjectManager


class ProjEngnApp:
    def __init__(self, page: ft.Page, working_directory: str | Path):
        self.page = page
        self.pm = ProjectManager(working_directory)
        self.projects = []
        self.projects_view = ft.Column(spacing=10)

    def scan_projects(self):
        """Scan for projects and update the UI."""
        self.projects = self.pm.get_all_projects()
        self.projects_view.controls.clear()

        if not self.projects:
            self.projects_view.controls.append(
                ft.Text("No projects found in the working directory.", italic=True)
            )
        else:
            for proj in self.projects:
                self.projects_view.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.FOLDER),
                                        title=ft.Text(proj.name),
                                        subtitle=ft.Text(str(proj.path)),
                                        trailing=ft.Icon(
                                            ft.Icons.CHECK_CIRCLE
                                            if proj.is_initialized
                                            else ft.Icons.RADIO_BUTTON_UNCHECKED,
                                            color=ft.Colors.GREEN
                                            if proj.is_initialized
                                            else ft.Colors.GREY,
                                        ),
                                    ),
                                ]
                            ),
                            padding=10,
                        )
                    )
                )
        self.page.update()

    def build(self):
        """Build the main UI layout."""
        self.page.title = "ProjEngn"
        self.page.theme_mode = ft.ThemeMode.DARK

        layout = ft.Column(
            controls=cast(
                list[ft.Control],
                [
                    ft.Text(
                        "Welcome to ProjEngn - Program Management Tool",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.Row(
                        controls=cast(
                            list[ft.Control],
                            [
                                ft.Text(
                                    "Projects", size=20, weight=ft.FontWeight.W_500
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    on_click=lambda _: self.scan_projects(),
                                ),
                            ],
                        ),
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.projects_view,
                ],
            ),
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
        )

        self.page.add(layout)
        self.scan_projects()


def flet_main(page: ft.Page, working_directory: str | Path):
    app = ProjEngnApp(page, working_directory)
    app.build()


def main() -> None:
    parser = argparse.ArgumentParser(description="ProjEngn - Program Management Tool")
    parser.add_argument(
        "--version", action="store_true", help="Show the version and exit"
    )
    parser.add_argument(
        "-w",
        "--working-directory",
        default=".",
        help="The working directory for projects (default: current directory)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    subparsers.add_parser("serve", help="Serve the application as a web app")

    args = parser.parse_args()

    if args.version:
        print(get_version())
        sys.exit(0)

    working_dir = Path(args.working_directory).resolve()

    def start_flet(page: ft.Page):
        flet_main(page, working_dir)

    if args.command == "serve":
        ft.app(
            target=start_flet,
            view=ft.AppView.WEB_BROWSER,
            assets_dir=str(Path(__file__).parent.parent / "engn" / "assets"),
        )
    else:
        ft.app(
            target=start_flet,
            assets_dir=str(Path(__file__).parent.parent / "engn" / "assets"),
        )


if __name__ == "__main__":
    main()
