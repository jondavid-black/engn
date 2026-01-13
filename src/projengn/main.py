import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import flet as ft
from engn.utils import get_version
from engn.config import ProjectConfig
from engn.core.auth import get_oauth_providers, User as EngnUser
from engn.ui import (
    LoginView,
    Toolbar,
    HomeDomainPage,
    UserProfileView,
    AdminView,
    BaselineView,
    ActualView,
    AnalyzeView,
    DocsView,
    RightDrawer,
)


class ProjEngnApp:
    """Main application controller for ProjEngn."""

    def __init__(
        self,
        page: ft.Page,
        config: ProjectConfig,
        user: EngnUser,
        working_directory: Path,
    ):
        self.page = page
        self.config = config
        self.user = user
        self.working_directory = working_directory
        self.current_view_index = 0

        # Create domain views
        self.home_page = HomeDomainPage(
            self.page,
            self.user,
            self.working_directory,
            on_projects_changed=self._on_projects_changed,
        )
        self.baseline_view = BaselineView()
        self.actual_view = ActualView()
        self.analyze_view = AnalyzeView()
        self.docs_view = DocsView(app_name="ProjEngn")

        # Views list matching tab order
        self.views = [
            self.home_page,
            self.baseline_view,
            self.actual_view,
            self.analyze_view,
            self.docs_view,
        ]

        # Create toolbar with program management tabs
        logo_path = str("engn_logo_core_tiny_transparent.png")
        self.toolbar = Toolbar(
            page=page,
            user=self.user,
            logo_path=logo_path,
            on_tab_change=self._on_tab_change,
            tabs=["Home", "Baseline", "Actual", "Analyze", "Docs"],
            on_logout=self._on_logout,
            on_profile=self._on_profile,
            working_directory=self.working_directory,
            on_admin=self._on_admin,
            on_toggle_terminal=self._on_toggle_terminal,
            on_toggle_search=self._on_toggle_search,
            on_toggle_ai=self._on_toggle_ai,
            show_branch_dropdown=True,
            show_search=True,
        )

        # Create drawer
        self.right_drawer = RightDrawer(page)

        # Content area for views
        self.content_area = ft.Container(
            content=self.home_page,
            expand=True,
        )

        # Main layout
        self.layout = ft.Column(
            controls=[
                self.toolbar,
                ft.Divider(height=1, thickness=1, color=ft.Colors.GREY_700),
                ft.Row(
                    [
                        self.content_area,
                        self.right_drawer,
                    ],
                    expand=True,
                    spacing=0,
                ),
            ],
            spacing=0,
            expand=True,
        )

    def _on_projects_changed(self) -> None:
        """Handle projects list change."""
        self.toolbar.refresh_projects()

    def _on_logout(self) -> None:
        """Handle logout."""
        store: Any = getattr(self.page.session, "store", self.page.session)
        store.remove("user")
        self.page.clean()
        # Return to login
        flet_main(self.page, self.working_directory)

    def _on_profile(self) -> None:
        """Show user profile page."""
        profile_view = UserProfileView(
            page=self.page,
            user=self.user,
            on_back=self._return_from_profile,
            on_save=self._on_profile_saved,
        )
        self._previous_view = self.content_area.content
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
        self.content_area.content = admin_view
        self.page.update()

    def _return_from_admin(self) -> None:
        """Return from admin panel to previous view."""
        if hasattr(self, "_previous_view") and self._previous_view:
            self.content_area.content = self._previous_view
        else:
            self.content_area.content = self.views[0]
        self.page.update()

    def _on_tab_change(self, index: int) -> None:
        """Handle tab navigation change."""
        self.current_view_index = index
        if 0 <= index < len(self.views):
            self.content_area.content = self.views[index]
        else:
            self.content_area.content = self.views[0]
        self.page.update()

    def _on_toggle_terminal(self) -> None:
        content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Terminal Emulator Stub",
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_400,
                    ),
                    ft.Text(
                        "$ ls -l\ntotal 0\n$ ",
                        font_family="monospace",
                        color=ft.Colors.GREEN_200,
                    ),
                    ft.TextField(
                        label="Command",
                        height=40,
                        text_size=14,
                        border_color=ft.Colors.GREY_700,
                    ),
                ]
            ),
            bgcolor=ft.Colors.BLACK,
            padding=10,
            expand=True,
            border_radius=5,
        )
        self.right_drawer.toggle("Terminal", content)
        self.page.update()

    def _on_toggle_search(self) -> None:
        content = ft.Column(
            [
                ft.TextField(
                    label="Search Query",
                    prefix_icon=ft.Icons.SEARCH,
                    hint_text="Type to search...",
                ),
                ft.Text("Search results will appear here...", color=ft.Colors.GREY_500),
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FILE_COPY),
                    title=ft.Text("Sample Result 1"),
                    subtitle=ft.Text("Match found in src/main.py"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FILE_COPY),
                    title=ft.Text("Sample Result 2"),
                    subtitle=ft.Text("Match found in README.md"),
                ),
            ],
            spacing=10,
        )
        self.right_drawer.toggle("Search", content)
        self.page.update()

    def _on_toggle_ai(self) -> None:
        content = ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "Hello! I am your AI assistant. How can I help you today?",
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.BLUE_900,
                    padding=10,
                    border_radius=10,
                ),
                ft.Container(expand=True),
                ft.Row(
                    [
                        ft.TextField(
                            hint_text="Ask me anything...",
                            expand=True,
                            border_color=ft.Colors.GREY_700,
                        ),
                        ft.IconButton(
                            ft.Icons.SEND,
                            icon_color=ft.Colors.BLUE_400,
                        ),
                    ]
                ),
            ],
            expand=True,
        )
        self.right_drawer.toggle("AI Assistant", content)
        self.page.update()

    def build(self) -> ft.Column:
        """Return the main layout."""
        return self.layout


def flet_main(page: ft.Page, working_directory: Optional[Path] = None):
    """Initialize and show the ProjEngn application."""
    page.title = "ProjEngn"
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
        app = ProjEngnApp(page, config, user=user, working_directory=working_dir)
        page.add(app.build())
        page.update()

    def on_login(e):
        if e.error:
            page.overlay.append(
                ft.SnackBar(ft.Text(f"Login error: {e.error}"), open=True)
            )
        else:
            # Successful OAuth login
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
                app_name="ProjEngn",
                oauth_providers=providers,
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ProjEngn - Digital Engine Program Management Tool"
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
