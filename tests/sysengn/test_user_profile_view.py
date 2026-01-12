import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from engn.ui import UserProfileView
from engn.core.auth import User


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    page.session.store = MagicMock()
    page.overlay = MagicMock()
    return page


@pytest.fixture
def test_user():
    return User(
        id="test-id",
        email="test@example.com",
        name="Test User",
        first_name="Test",
        last_name="User",
        preferred_color=ft.Colors.BLUE,
    )


def test_user_profile_view_init(mock_page, test_user):
    on_back = MagicMock()
    view = UserProfileView(page=mock_page, user=test_user, on_back=on_back)

    assert view.first_name_field.value == "Test"
    assert view.last_name_field.value == "User"
    assert view.selected_color == ft.Colors.BLUE
    # Initials for "Test User" should be "TU"
    assert isinstance(view.avatar_display.content, ft.Text)
    assert view.avatar_display.content.value == "TU"


def test_user_profile_view_initials_fallback(mock_page):
    user = User(id="1", email="onlyemail@example.com", name=None)
    view = UserProfileView(page=mock_page, user=user, on_back=MagicMock())
    # Initials should fallback to email first letter "O"
    assert isinstance(view.avatar_display.content, ft.Text)
    assert view.avatar_display.content.value == "O"


def test_user_profile_view_change_name_updates_initials(mock_page, test_user):
    view = UserProfileView(page=mock_page, user=test_user, on_back=MagicMock())
    # Mock update to avoid flet internal errors in non-rendered control
    view.avatar_display.update = MagicMock()

    view.first_name_field.value = "John"
    view.last_name_field.value = "Doe"
    view.update_avatar_initials(None)

    assert isinstance(view.avatar_display.content, ft.Text)
    assert view.avatar_display.content.value == "JD"


def test_user_profile_view_change_color(mock_page, test_user):
    view = UserProfileView(page=mock_page, user=test_user, on_back=MagicMock())
    view.update = MagicMock()

    mock_event = MagicMock()
    mock_event.control.data = ft.Colors.RED
    view.on_color_click(mock_event)

    assert view.selected_color == ft.Colors.RED
    assert view.avatar_display.bgcolor == ft.Colors.RED


def test_user_profile_view_save(mock_page, test_user):
    on_back = MagicMock()
    on_save = MagicMock()
    view = UserProfileView(
        page=mock_page, user=test_user, on_back=on_back, on_save=on_save
    )

    view.first_name_field.value = "New"
    view.last_name_field.value = "Name"
    view.selected_color = ft.Colors.GREEN

    with patch("engn.ui.views.update_user_profile") as mock_update:
        view.save_profile(None)

        mock_update.assert_called_once_with("test-id", "New", "Name", ft.Colors.GREEN)
        assert test_user.first_name == "New"
        assert test_user.last_name == "Name"
        assert test_user.name == "New Name"
        assert test_user.preferred_color == ft.Colors.GREEN

        on_save.assert_called_once()
        on_back.assert_called_once()
        mock_page.overlay.append.assert_called()
