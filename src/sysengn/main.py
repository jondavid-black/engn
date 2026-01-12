import argparse
import sys
from pathlib import Path

from typing import Any, Optional

import flet as ft
from engn.utils import get_version
from engn.config import ProjectConfig
from engn.core.auth import get_oauth_providers, User as EngnUser
from sysengn.auth import Authenticator, User as SysEngnUser
from engn.ui import LoginView, AdminView, UserProfileView, HomeDomainPage, Toolbar
from sysengn.components import (
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
        user: EngnUser | SysEngnUser | None = None,
        authenticator: Authenticator | None = None,
        working_directory: Optional[Path] = None,
    ):
        self.page = page
        self.config = config
        self.working_directory = working_directory or Path.cwd()
        if user:
            self.user = user
        else:
            self.authenticator = authenticator or Authenticator(config)
            self.user = self.authenticator.get_current_user()
        self.current_view_index = 0

        # Create toolbar
        logo_path = str("engn_logo_core_tiny_transparent.png")
        self.toolbar = Toolbar(
            page=page,
            user=self.user,  # type: ignore
            logo_path=logo_path,
            on_tab_change=self._on_tab_change,
            tabs=["Home", "MBSE", "UX", "Docs"],
            on_logout=self._on_logout,
            on_profile=self._on_profile,
            working_directory=self.working_directory,
            on_admin=self._on_admin,
            on_toggle_terminal=self._on_toggle_terminal,
        )

        # Create domain views
        self.views = [
            HomeDomainPage(
                self.page,
                self.user,
                self.working_directory,
                on_projects_changed=self.toolbar.refresh_projects,
            ),  # type: ignore
            MBSEView(),
            UXView(),
            DocsView(),
        ]

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
        """Show user profile page."""
        profile_view = UserProfileView(
            page=self.page,
            user=self.user,
            on_back=self._return_from_profile,
            on_save=self._on_profile_saved,
        )
        self._previous_view = self.content_area.content
        self._previous_view_index = self.current_view_index
        self.content_area.content = profile_view
        self.page.update()

    def _return_from_profile(self) -> None:
        """Return from profile page to previous view."""
        if hasattr(self, "_previous_view") and self._previous_view:
            self.content_area.content = self._previous_view
        else:
            self.content_area.content = self.views[0]
        self.page.update()

    def _on_profile_saved(self) -> None:
        """Handle profile save - refresh the toolbar avatar."""
        self.toolbar.refresh_avatar()

    def _on_admin(self) -> None:
        """Show admin panel."""
        admin_view = AdminView(
            page=self.page,
            user=self.user,
            on_back=self._return_from_admin,
        )
        self._previous_view = self.content_area.content
        self._previous_view_index = self.current_view_index
        self.content_area.content = admin_view
        self.page.update()

    def _return_from_admin(self) -> None:
        """Return from admin panel to previous view."""
        if hasattr(self, "_previous_view") and self._previous_view:
            self.content_area.content = self._previous_view
        else:
            self.content_area.content = self.views[0]
        self.page.update()

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


def flet_main(page: ft.Page, working_directory: Optional[Path] = None):
    page.title = "SysEngn"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    working_dir = working_directory or Path.cwd()

    # Initialize auth config path
    from engn.core.auth import set_config_path

    set_config_path(working_dir / "engn.jsonl")

    config = ProjectConfig.load(working_dir)

    def show_main_app():
        page.clean()
        store: Any = getattr(page.session, "store", page.session)
        user = store.get("user")
        app = MainApp(page, config, user=user, working_directory=working_dir)
        page.add(app.build())
        page.update()

    def on_login(e):
        if e.error:
            page.overlay.append(
                ft.SnackBar(ft.Text(f"Login error: {e.error}"), open=True)
            )
        else:
            # Successful OAuth login
            # Extract user info from page.auth
            auth: Any = getattr(page, "auth", None)
            user_data = getattr(auth, "user", {}) if auth else {}
            user = EngnUser(
                id=user_data.get("id") or user_data.get("sub") or "oauth",
                email=user_data.get("email") or "unknown",
                name=user_data.get("name") or "OAuth User",
            )
            store: Any = getattr(page.session, "store", page.session)
            store.set("user", user)
            show_main_app()
        page.update()

    page.on_login = on_login

    providers = get_oauth_providers()

    # If already logged in, show main app
    store: Any = getattr(page.session, "store", page.session)
    if store.get("user"):
        show_main_app()
    else:
        page.add(
            LoginView(
                page,
                on_login_success=show_main_app,
                icon="images/sysengn_logo.png",
                app_name="SysEngn",
                oauth_providers=providers,
            )
        )


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
