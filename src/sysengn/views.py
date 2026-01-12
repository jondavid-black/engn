import flet as ft
from typing import Callable, Any, Optional
from engn.core.auth import (
    User,
    Role,
    authenticate_local_user,
    update_user_profile,
    create_user,
    remove_user,
    list_users,
    add_role_to_user,
    remove_role_from_user,
)
from argon2 import PasswordHasher

ph = PasswordHasher()


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


class AdminView(ft.Column):
    """Admin panel for user and role management."""

    def __init__(
        self,
        page: ft.Page,
        user: User,
        on_back: Callable[[], None],
    ):
        super().__init__()
        self.page_ref = page
        self.user = user
        self.on_back = on_back

        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO

        # User list data table
        self.users_table = self._build_users_table()

        # Add user form fields
        self.new_email_field = ft.TextField(
            label="Email",
            width=250,
            on_submit=self._add_user,
        )
        self.new_name_field = ft.TextField(
            label="Display Name",
            width=250,
        )
        self.new_password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=250,
        )
        self.new_password_confirm_field = ft.TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            width=250,
            on_submit=self._add_user,
        )
        self.new_role_dropdown = ft.Dropdown(
            label="Initial Role",
            width=150,
            options=[ft.dropdown.Option(r.value) for r in Role],
            value=Role.USER.value,
        )

        self.controls = self._build_controls()

    def _build_controls(self) -> list[ft.Control]:
        return [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    ft.Icons.ARROW_BACK,
                                    on_click=lambda _: self.on_back(),
                                    tooltip="Back",
                                ),
                                ft.Text(
                                    "Admin Panel",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Divider(),
                        # User Management Section
                        ft.Text(
                            "User Management",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Container(height=10),
                        # Add User Form
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Add New User", size=14, italic=True),
                                    ft.Row(
                                        controls=[
                                            self.new_email_field,
                                            self.new_name_field,
                                        ],
                                        wrap=True,
                                    ),
                                    ft.Row(
                                        controls=[
                                            self.new_password_field,
                                            self.new_password_confirm_field,
                                        ],
                                        wrap=True,
                                    ),
                                    ft.Row(
                                        controls=[
                                            self.new_role_dropdown,
                                            ft.FilledButton(
                                                "Add User",
                                                icon=ft.Icons.PERSON_ADD,
                                                on_click=self._add_user,
                                            ),
                                        ],
                                    ),
                                ],
                                spacing=10,
                            ),
                            padding=15,
                            bgcolor=ft.Colors.GREY_900,
                            border_radius=8,
                        ),
                        ft.Container(height=20),
                        # Users Table
                        ft.Text("Existing Users", size=14, italic=True),
                        self.users_table,
                        ft.Container(height=20),
                        # Available Roles Info
                        ft.Text(
                            "Available Roles",
                            size=18,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.ADMIN_PANEL_SETTINGS,
                                                color=ft.Colors.RED_400,
                                            ),
                                            ft.Text("ADMIN", weight=ft.FontWeight.BOLD),
                                            ft.Text(
                                                "- Full system access, user management"
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.PERSON,
                                                color=ft.Colors.BLUE_400,
                                            ),
                                            ft.Text("USER", weight=ft.FontWeight.BOLD),
                                            ft.Text("- Standard user access"),
                                        ],
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.PERSON_OUTLINE,
                                                color=ft.Colors.GREY_400,
                                            ),
                                            ft.Text("GUEST", weight=ft.FontWeight.BOLD),
                                            ft.Text("- Limited read-only access"),
                                        ],
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=15,
                            bgcolor=ft.Colors.GREY_900,
                            border_radius=8,
                        ),
                    ],
                    spacing=5,
                ),
                padding=30,
                expand=True,
            ),
        ]

    def _build_users_table(self) -> ft.DataTable:
        users = list_users()
        rows = []

        for u in users:
            is_current_user = u.id == self.user.id

            # Role management buttons
            role_buttons = []
            for role in Role:
                has_role = role in u.roles
                role_buttons.append(
                    ft.IconButton(
                        icon=ft.Icons.CHECK_CIRCLE
                        if has_role
                        else ft.Icons.CIRCLE_OUTLINED,
                        icon_color=ft.Colors.GREEN_400
                        if has_role
                        else ft.Colors.GREY_600,
                        tooltip=f"{'Remove' if has_role else 'Add'} {role.value}",
                        on_click=lambda e,
                        email=u.email,
                        r=role,
                        has=has_role: self._toggle_role(email, r, has),
                        disabled=is_current_user and role == Role.ADMIN,
                    )
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(u.email)),
                        ft.DataCell(ft.Text(u.name or "-")),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.Text(role.value, size=12) for role in Role
                                ],
                                spacing=25,
                            )
                        ),
                        ft.DataCell(ft.Row(controls=role_buttons, spacing=0)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED_400,
                                tooltip="Remove User",
                                on_click=lambda e,
                                email=u.email: self._confirm_remove_user(email),
                                disabled=is_current_user,
                            )
                        ),
                    ],
                )
            )

        return ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Email")),
                ft.DataColumn(label=ft.Text("Name")),
                ft.DataColumn(label=ft.Text("Roles")),
                ft.DataColumn(label=ft.Text("Toggle Roles")),
                ft.DataColumn(label=ft.Text("Actions")),
            ],
            rows=rows,
            border=ft.Border.all(1, ft.Colors.GREY_700),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_800),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_800),
        )

    def _refresh_users_table(self):
        new_table = self._build_users_table()
        # Find and replace the table in controls
        container: Any = self.controls[0]
        column: Any = container.content
        for i, control in enumerate(column.controls):
            if isinstance(control, ft.DataTable):
                column.controls[i] = new_table
                self.users_table = new_table
                break
        self.update()

    def _add_user(self, e):
        email = self.new_email_field.value
        name = self.new_name_field.value
        password = self.new_password_field.value
        confirm = self.new_password_confirm_field.value
        role_value = self.new_role_dropdown.value

        # Validation
        if not email:
            self._show_error("Email is required")
            return

        if not password:
            self._show_error("Password is required")
            return

        if password != confirm:
            self._show_error("Passwords do not match")
            return

        if len(password) < 4:
            self._show_error("Password must be at least 4 characters")
            return

        try:
            roles = [Role(role_value)] if role_value else [Role.USER]
            create_user(email, password, name or "", roles)
            self._show_success(f"User '{email}' created successfully")

            # Clear form
            self.new_email_field.value = ""
            self.new_name_field.value = ""
            self.new_password_field.value = ""
            self.new_password_confirm_field.value = ""
            self.new_role_dropdown.value = Role.USER.value

            self._refresh_users_table()
        except ValueError as ex:
            self._show_error(str(ex))

    def _toggle_role(self, email: str, role: Role, currently_has: bool):
        try:
            if currently_has:
                remove_role_from_user(email, role)
                self._show_success(f"Removed {role.value} from {email}")
            else:
                add_role_to_user(email, role)
                self._show_success(f"Added {role.value} to {email}")
            self._refresh_users_table()
        except Exception as ex:
            self._show_error(str(ex))

    def _confirm_remove_user(self, email: str):
        def do_remove(e):
            dialog.open = False
            self.page_ref.update()
            self._remove_user(email)

        def cancel(e):
            dialog.open = False
            self.page_ref.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(f"Are you sure you want to remove user '{email}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.TextButton("Delete", on_click=do_remove),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page_ref.overlay.append(dialog)
        dialog.open = True
        self.page_ref.update()

    def _remove_user(self, email: str):
        if remove_user(email):
            self._show_success(f"User '{email}' removed")
            self._refresh_users_table()
        else:
            self._show_error(f"Failed to remove user '{email}'")

    def _show_error(self, message: str):
        self.page_ref.overlay.append(
            ft.SnackBar(
                ft.Text(message),
                bgcolor=ft.Colors.RED_900,
                open=True,
            )
        )
        self.page_ref.update()

    def _show_success(self, message: str):
        self.page_ref.overlay.append(
            ft.SnackBar(
                ft.Text(message),
                bgcolor=ft.Colors.GREEN_900,
                open=True,
            )
        )
        self.page_ref.update()
