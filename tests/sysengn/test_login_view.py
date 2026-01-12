import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from engn.ui import LoginView
from engn.core.auth import User


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    # Mock store if needed
    page.session.store = MagicMock()
    page.overlay = MagicMock()
    return page


def test_login_view_init(mock_page):
    on_success = MagicMock()
    view = LoginView(
        page=mock_page, on_login_success=on_success, icon="icon.png", app_name="TestApp"
    )
    assert view.app_name == "TestApp"
    assert len(view.controls) > 0


def test_local_login_success(mock_page):
    on_success = MagicMock()
    view = LoginView(
        page=mock_page,
        on_login_success=on_success,
        icon="icon.png",
        app_name="TestApp",
        allow_passwords=True,
    )

    view.email_field.value = "test@example.com"
    view.password_field.value = "password"

    mock_user = User(id="1", email="test@example.com", name="Test User")

    with patch("engn.ui.views.authenticate_local_user", return_value=mock_user):
        view.handle_local_login(None)

        # Check if user was set in session/store
        store = getattr(mock_page.session, "store", mock_page.session)
        store.set.assert_called_with("user", mock_user)
        on_success.assert_called_once()


def test_local_login_failure(mock_page):
    on_success = MagicMock()
    view = LoginView(
        page=mock_page,
        on_login_success=on_success,
        icon="icon.png",
        app_name="TestApp",
        allow_passwords=True,
    )

    view.email_field.value = "test@example.com"
    view.password_field.value = "wrong"

    with patch("engn.ui.views.authenticate_local_user", return_value=None):
        view.handle_local_login(None)

        on_success.assert_not_called()
        mock_page.overlay.append.assert_called()


@pytest.mark.anyio
async def test_oauth_login_click(mock_page):
    on_success = MagicMock()
    mock_provider = MagicMock()
    mock_provider.authorization_endpoint = "https://github.com/login/oauth/authorize"

    view = LoginView(
        page=mock_page,
        on_login_success=on_success,
        icon="icon.png",
        app_name="TestApp",
        oauth_providers=[mock_provider],
    )

    # Simulate OAuth button click
    # The handler is returned by _on_oauth_click
    handler = view._on_oauth_click(mock_provider)
    await handler(None)

    mock_page.login.assert_called_with(mock_provider)
