import argparse
import sys
from pathlib import Path

import flet as ft
from engn.utils import get_version
from engn.config import ProjectConfig
from sysengn.auth import Authenticator
from sysengn.views import LoginView
from sysengn.components import (
    Toolbar,
    HomeView,
    MBSEView,
    UXView,
    DocsView,
)


class MainApp:
    """Main application controller for SysEngn."""

    def __init__(
        self,
        page: ft.Page,
        config: ProjectConfig,
        authenticator: Authenticator | None = None,
    ):
        self.page = page
        self.config = config
        self.authenticator = authenticator or Authenticator(config)
        self.user = self.authenticator.get_current_user()
        self.current_view_index = 0

        # Create domain views
        self.views = [
            HomeView(),
            MBSEView(),
            UXView(),
            DocsView(),
        ]

        # Create toolbar
        logo_path = str("engn_logo_core_tiny_transparent.png")
        self.toolbar = Toolbar(
            page=page,
            user=self.user,
            logo_path=logo_path,
            on_tab_change=self._on_tab_change,
            tabs=["Home", "MBSE", "UX", "Docs"],
            on_logout=self._on_logout,
            on_profile=self._on_profile,
            on_admin=self._on_admin,
            on_toggle_terminal=self._on_toggle_terminal,
        )

        # Content area for domain views
        self.content_area = ft.Container(
            content=self.views[0],
            expand=True,
        )

        # Main layout
        self.layout = ft.Column(
            controls=[
                self.toolbar,
                ft.Divider(height=1),
                self.content_area,
            ],
            spacing=0,
            expand=True,
        )

    def _on_logout(self) -> None:
        print("Logout clicked")

    def _on_profile(self) -> None:
        print("Profile clicked")

    def _on_admin(self) -> None:
        print("Admin clicked")

    def _on_toggle_terminal(self) -> None:
        print("Terminal toggled")

    def _on_tab_change(self, index: int) -> None:
        """Handle tab navigation change."""
        self.current_view_index = index
        self.content_area.content = self.views[index]
        self.page.update()

    def build(self) -> ft.Column:
        """Return the main layout."""
        return self.layout


def flet_main(page: ft.Page):
    page.title = "SysEngn"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    config = ProjectConfig.load(Path.cwd())
    authenticator = Authenticator(config)

    def show_main_app():
        page.clean()
        app = MainApp(page, config, authenticator)
        page.add(app.build())
        page.update()

    # Check if auth is configured
    if config.auth and config.auth.username and config.auth.password_hash:
        page.add(LoginView(page, authenticator, show_main_app))
    else:
        # If no auth configured, go straight to main page
        app = MainApp(page, config, authenticator)
        page.add(app.build())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SysEngn - Model-Based System Engineering Tool"
    )
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

    if args.command == "serve":
        ft.app(
            target=flet_main,
            view=ft.AppView.WEB_BROWSER,
            assets_dir=str(Path(__file__).parent.parent / "engn" / "assets"),
        )
    else:
        ft.app(
            target=flet_main,
            assets_dir=str(Path(__file__).parent.parent / "engn" / "assets"),
        )


if __name__ == "__main__":
    main()
