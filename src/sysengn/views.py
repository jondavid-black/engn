import flet as ft
from sysengn.auth import Authenticator


class LoginView(ft.Container):
    def __init__(self, page: ft.Page, authenticator: Authenticator, on_success):
        super().__init__()
        self.page_ref = page
        self.authenticator = authenticator
        self.on_success = on_success
        self.username_field = ft.TextField(label="Username", width=300)
        self.password_field = ft.TextField(
            label="Password", password=True, can_reveal_password=True, width=300
        )
        self.error_text = ft.Text(color=ft.colors.RED)

        self.content = ft.Column(
            controls=[
                ft.Text("Login to SysEngn", size=30, weight=ft.FontWeight.BOLD),
                self.username_field,
                self.password_field,
                self.error_text,
                ft.ElevatedButton("Login", on_click=self.login, width=300),
                ft.Text("Or", size=14),
                ft.ElevatedButton(
                    "Login with GitHub",
                    on_click=self.login_with_github,
                    width=300,
                    icon=ft.icons.LOGIN,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
        self.alignment = ft.alignment.Alignment(0, 0)
        self.expand = True

    def login(self, e):
        username = self.username_field.value
        password = self.password_field.value

        if not username or not password:
            self.error_text.value = "Please enter username and password"
            self.update()
            return

        if self.authenticator.authenticate(username, password):
            self.on_success()
        else:
            self.error_text.value = "Invalid credentials"
            self.update()

    def login_with_github(self, e):
        # Placeholder for GitHub OAuth2 logic
        # In a real implementation, this would trigger the OAuth flow
        # Flet 0.26+ uses page.login, checking if it is available
        if hasattr(self.page_ref, "login"):
            # Using dynamic import or string reference to avoid static analysis issues if needed,
            # but usually just importing it correctly should work.
            # ft.auth is available at runtime as verified.
            from flet.auth import OAuthProvider

            self.page_ref.login(
                OAuthProvider(
                    client_id="github_client_id",
                    client_secret="github_client_secret",
                    authorization_endpoint="https://github.com/login/oauth/authorize",
                    token_endpoint="https://github.com/login/oauth/access_token",
                    redirect_url="http://localhost:8550/oauth_callback",
                )
            )
        else:
            # Fallback or error if login is not supported in this context
            print("Login method not available on page object")
