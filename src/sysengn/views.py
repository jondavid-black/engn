import flet as ft
from typing import Callable, Any, Optional
from engn.core.auth import User, authenticate_local_user, update_user_profile


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
                ft.FilledButton(
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
                    ft.FilledButton(
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


class UserProfileView(ft.Column):
    """View for editing user profile."""

    def __init__(
        self,
        page: ft.Page,
        user: User,
        on_back: Callable[[], None],
        on_save: Optional[Callable[[], None]] = None,
    ):
        """Initialize the user profile view.

        Args:
            page: Reference to the main Flet page.
            user: The current user object.
            on_back: Function to call when back button is clicked.
            on_save: Optional function to call when profile is saved.
        """
        super().__init__()
        self.page_ref = page
        self.user = user
        self.on_back = on_back
        self.on_save = on_save

        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.expand = True

        self.first_name_field = ft.TextField(
            label="First Name",
            value=user.first_name or "",
            width=300,
            on_change=self.update_avatar_initials,
        )
        self.last_name_field = ft.TextField(
            label="Last Name",
            value=user.last_name or "",
            width=300,
            on_change=self.update_avatar_initials,
        )

        # Color options
        self.color_options = [
            ft.Colors.BLUE,
            ft.Colors.RED,
            ft.Colors.GREEN,
            ft.Colors.ORANGE,
            ft.Colors.PURPLE,
            ft.Colors.TEAL,
            ft.Colors.PINK,
            ft.Colors.CYAN,
        ]

        self.selected_color = user.preferred_color or ft.Colors.BLUE
        self.color_selection = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        self._build_color_options()

        self.avatar_display = self._build_avatar()

        self.controls = [
            ft.Text("User Profile", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.avatar_display,
            self.first_name_field,
            self.last_name_field,
            ft.Text("Preferred Color:", size=16),
            self.color_selection,
            ft.Divider(height=20),
            ft.Row(
                controls=[
                    ft.FilledButton("Save", on_click=self.save_profile),
                    ft.OutlinedButton("Cancel", on_click=lambda _: self.on_back()),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]

    def _get_initials(self) -> str:
        first = self.first_name_field.value or ""
        last = self.last_name_field.value or ""
        initials = ""
        if first:
            initials += first[0].upper()
        if last:
            initials += last[0].upper()

        if not initials and self.user.name:
            # Fallback to name initials
            parts = self.user.name.split()
            if len(parts) >= 2:
                initials = f"{parts[0][0].upper()}{parts[-1][0].upper()}"
            elif parts:
                initials = parts[0][0].upper()

        if not initials:
            initials = self.user.email[0].upper()

        return initials

    def _build_avatar(self) -> ft.CircleAvatar:
        initials = self._get_initials()
        self.avatar_text_control = ft.Text(initials, color=ft.Colors.WHITE)
        return ft.CircleAvatar(
            content=self.avatar_text_control,
            bgcolor=self.selected_color,
            radius=40,
        )

    def update_avatar_initials(self, e):
        """Update avatar initials when name fields change."""
        initials = self._get_initials()
        text_control: Any = self.avatar_text_control
        text_control.value = initials
        self.avatar_display.update()

    def _build_color_options(self):
        self.color_selection.controls.clear()
        for color in self.color_options:
            is_selected = color == self.selected_color
            self.color_selection.controls.append(
                ft.Container(
                    width=30,
                    height=30,
                    bgcolor=color,
                    border_radius=15,
                    border=ft.Border.all(2, ft.Colors.WHITE) if is_selected else None,
                    on_click=self.on_color_click,
                    data=color,
                    tooltip=color,
                )
            )

    def on_color_click(self, e):
        """Handle color selection."""
        self.selected_color = e.control.data
        self._build_color_options()
        self.avatar_display.bgcolor = self.selected_color
        self.update()

    def save_profile(self, e):
        """Save profile changes to the configuration file."""
        self.user.first_name = self.first_name_field.value
        self.user.last_name = self.last_name_field.value
        self.user.preferred_color = self.selected_color

        # Update full name if both parts are present
        if self.user.first_name and self.user.last_name:
            self.user.name = f"{self.user.first_name} {self.user.last_name}"

        update_user_profile(
            self.user.id,
            self.user.first_name,
            self.user.last_name,
            self.user.preferred_color,
        )

        self.page_ref.overlay.append(
            ft.SnackBar(ft.Text("Profile updated successfully!"), open=True)
        )
        self.page_ref.update()

        if self.on_save:
            self.on_save()

        self.on_back()
