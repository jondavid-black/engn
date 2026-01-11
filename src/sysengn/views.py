import flet as ft
from typing import Callable, Any
from engn.core.auth import authenticate_local_user


class LoginView(ft.Column):
    """A reusable login component handling both local and OAuth authentication.

    This component renders a login form with support for email/password authentication
    and OAuth providers like Google and GitHub.

    Attributes:
        page_ref (ft.Page): Reference to the main Flet page.
        on_login_success (Callable[[], None]): Callback triggered on successful login.
        icon (str): Path to the application icon.
        app_name (str): Name of the application displayed in the header.
        allow_passwords (bool): Whether to enable email/password login.
        oauth_providers (list[Any]): List of configured OAuth providers.
    """

    def __init__(
        self,
        page: ft.Page,
        on_login_success: Callable[[], None],
        icon: str,
        app_name: str,
        allow_passwords: bool = True,
        oauth_providers: list[Any] | None = None,
    ):
        """Initialize the login view.

        Args:
            page: Reference to the main Flet page.
            on_login_success: Function to call when login succeeds.
            icon: Path to the icon image asset.
            app_name: Name of the application to display.
            allow_passwords: If True, shows email/password fields. Defaults to True.
            oauth_providers: Optional list of OAuth provider objects.
        """
        super().__init__()
        self.page_ref = page
        self.on_login_success = on_login_success
        self.icon_path = icon
        self.app_name = app_name
        self.allow_passwords = allow_passwords
        self.oauth_providers = oauth_providers or []

        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.expand = True

        # Initialize fields
        self.email_field = ft.TextField(label="Email", width=300)
        self.password_field = ft.TextField(label="Password", password=True, width=300)

        # Bind on_submit
        self.email_field.on_submit = self.handle_local_login
        self.password_field.on_submit = self.handle_local_login

        self.controls = self._build_controls()

    def _build_controls(self) -> list[ft.Control]:
        login_buttons = []
        for provider in self.oauth_providers:
            # Check provider type or endpoint to determine name
            name = "OAuth Provider"
            if "google" in getattr(provider, "authorization_endpoint", "").lower():
                name = "Google"
            elif "github" in getattr(provider, "authorization_endpoint", "").lower():
                name = "GitHub"

            # Fallback using class name if endpoints are not reliable/available
            if name == "OAuth Provider":
                class_name = provider.__class__.__name__
                if "Google" in class_name:
                    name = "Google"
                elif "GitHub" in class_name:
                    name = "GitHub"

            login_buttons.append(
                ft.ElevatedButton(
                    content=ft.Text(f"Login with {name}"),
                    on_click=self._on_oauth_click(provider),
                    width=300,
                )
            )

        content: list[ft.Control] = [
            ft.Image(src=self.icon_path, width=200),
            ft.Text(f"Welcome to {self.app_name}", size=30, weight=ft.FontWeight.BOLD),
            ft.Text("Please sign in to continue", size=16),
            ft.Divider(),
        ]

        if login_buttons:
            content.extend(login_buttons)
            content.append(ft.Divider())

        if self.allow_passwords:
            content.extend(
                [
                    ft.Text("Sign in with email", size=14),
                    self.email_field,
                    self.password_field,
                    ft.ElevatedButton(
                        content=ft.Text("Sign In"),
                        on_click=self.handle_local_login,
                        width=300,
                    ),
                ]
            )

        return content

    def _on_oauth_click(self, provider):
        async def handler(e):
            await self.handle_oauth_login(provider)

        return handler

    async def handle_oauth_login(self, provider):
        """Initiates the OAuth login flow for the selected provider.

        Args:
            provider: The OAuth provider instance to authenticate with.
        """
        await self.page_ref.login(provider)

    def handle_local_login(self, e):
        """Handles the local email/password login submission.

        Validates the input fields and attempts to authenticate the user against
        the local database.

        Args:
            e: The event object that triggered the login (e.g., button click or enter key).
        """
        if not self.email_field.value or not self.password_field.value:
            self.page_ref.overlay.append(
                ft.SnackBar(ft.Text("Please enter email and password"), open=True)
            )
            self.page_ref.update()
            return

        user = authenticate_local_user(
            self.email_field.value, self.password_field.value
        )
        if user:
            store: Any = getattr(self.page_ref.session, "store", self.page_ref.session)
            store.set("user", user)
            self.page_ref.clean()
            self.on_login_success()
        else:
            self.page_ref.overlay.append(
                ft.SnackBar(ft.Text("Invalid credentials"), open=True)
            )
            self.page_ref.update()
