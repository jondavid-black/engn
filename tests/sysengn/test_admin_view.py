import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from engn.ui import AdminView
from engn.core.auth import User, Role


@pytest.fixture
def mock_page():
    page = MagicMock(spec=ft.Page)
    page.session = MagicMock()
    page.session.store = MagicMock()
    page.overlay = []
    page.update = MagicMock()
    return page


@pytest.fixture
def admin_user():
    return User(
        id="admin-id",
        email="admin@example.com",
        name="Admin User",
        roles=[Role.ADMIN, Role.USER],
    )


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    config_file = tmp_path / "engn.toml"
    monkeypatch.setattr("engn.core.auth.CONFIG_PATH", config_file)
    monkeypatch.setattr("engn.ui.views.list_users", lambda: [])
    return config_file


def test_admin_view_init(mock_page, admin_user):
    on_back = MagicMock()
    with patch("engn.ui.views.list_users", return_value=[admin_user]):
        view = AdminView(page=mock_page, user=admin_user, on_back=on_back)

    assert view.user == admin_user
    assert view.on_back == on_back
    assert view.new_email_field is not None
    assert view.new_password_field is not None
    assert view.new_role_dropdown.value == Role.USER.value


def test_admin_view_builds_users_table(mock_page, admin_user):
    test_users = [
        admin_user,
        User(
            id="user-2",
            email="user@example.com",
            name="Regular User",
            roles=[Role.USER],
        ),
    ]

    with patch("engn.ui.views.list_users", return_value=test_users):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    # Check that table has rows for users
    assert len(view.users_table.rows) == 2


def test_admin_view_add_user_validation_empty_email(mock_page, admin_user):
    with patch("engn.ui.views.list_users", return_value=[]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.new_email_field.value = ""
    view.new_password_field.value = "password123"
    view.new_password_confirm_field.value = "password123"

    view._add_user(None)

    # Should show error
    assert len(mock_page.overlay) == 1
    assert "Email is required" in mock_page.overlay[0].content.value


def test_admin_view_add_user_validation_empty_password(mock_page, admin_user):
    with patch("engn.ui.views.list_users", return_value=[]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.new_email_field.value = "new@example.com"
    view.new_password_field.value = ""
    view.new_password_confirm_field.value = ""

    view._add_user(None)

    assert len(mock_page.overlay) == 1
    assert "Password is required" in mock_page.overlay[0].content.value


def test_admin_view_add_user_validation_password_mismatch(mock_page, admin_user):
    with patch("engn.ui.views.list_users", return_value=[]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.new_email_field.value = "new@example.com"
    view.new_password_field.value = "password123"
    view.new_password_confirm_field.value = "differentpassword"

    view._add_user(None)

    assert len(mock_page.overlay) == 1
    assert "Passwords do not match" in mock_page.overlay[0].content.value


def test_admin_view_add_user_validation_short_password(mock_page, admin_user):
    with patch("engn.ui.views.list_users", return_value=[]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.new_email_field.value = "new@example.com"
    view.new_password_field.value = "123"
    view.new_password_confirm_field.value = "123"

    view._add_user(None)

    assert len(mock_page.overlay) == 1
    assert "at least 4 characters" in mock_page.overlay[0].content.value


def test_admin_view_add_user_success(mock_page, admin_user):
    new_user = User(
        id="new-id", email="new@example.com", name="New User", roles=[Role.USER]
    )

    with patch("engn.ui.views.list_users", return_value=[admin_user]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.new_email_field.value = "new@example.com"
    view.new_name_field.value = "New User"
    view.new_password_field.value = "password123"
    view.new_password_confirm_field.value = "password123"
    view.new_role_dropdown.value = Role.USER.value
    view.update = MagicMock()

    with patch("engn.ui.views.create_user", return_value=new_user) as mock_create:
        with patch("engn.ui.views.list_users", return_value=[admin_user, new_user]):
            view._add_user(None)

    mock_create.assert_called_once()
    # Form should be cleared
    assert view.new_email_field.value == ""
    assert view.new_password_field.value == ""


def test_admin_view_add_user_duplicate_error(mock_page, admin_user):
    with patch("engn.ui.views.list_users", return_value=[admin_user]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.new_email_field.value = "admin@example.com"
    view.new_name_field.value = "Duplicate"
    view.new_password_field.value = "password123"
    view.new_password_confirm_field.value = "password123"

    with patch(
        "engn.ui.views.create_user", side_effect=ValueError("User already exists")
    ):
        view._add_user(None)

    # Should show error
    assert any("already exists" in str(o.content.value) for o in mock_page.overlay)


def test_admin_view_toggle_role_add(mock_page, admin_user):
    test_user = User(id="user-id", email="user@example.com", roles=[Role.USER])

    with patch("engn.ui.views.list_users", return_value=[admin_user, test_user]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.update = MagicMock()

    with patch("engn.ui.views.add_role_to_user", return_value=True) as mock_add:
        with patch("engn.ui.views.list_users", return_value=[admin_user, test_user]):
            view._toggle_role("user@example.com", Role.ADMIN, False)

    mock_add.assert_called_once_with("user@example.com", Role.ADMIN)


def test_admin_view_toggle_role_remove(mock_page, admin_user):
    test_user = User(
        id="user-id", email="user@example.com", roles=[Role.ADMIN, Role.USER]
    )

    with patch("engn.ui.views.list_users", return_value=[admin_user, test_user]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.update = MagicMock()

    with patch("engn.ui.views.remove_role_from_user", return_value=True) as mock_remove:
        with patch("engn.ui.views.list_users", return_value=[admin_user, test_user]):
            view._toggle_role("user@example.com", Role.ADMIN, True)

    mock_remove.assert_called_once_with("user@example.com", Role.ADMIN)


def test_admin_view_remove_user(mock_page, admin_user):
    test_user = User(id="user-id", email="user@example.com", roles=[Role.USER])

    with patch("engn.ui.views.list_users", return_value=[admin_user, test_user]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view.update = MagicMock()

    with patch("engn.ui.views.remove_user", return_value=True) as mock_remove:
        with patch("engn.ui.views.list_users", return_value=[admin_user]):
            view._remove_user("user@example.com")

    mock_remove.assert_called_once_with("user@example.com")


def test_admin_view_remove_user_failure(mock_page, admin_user):
    with patch("engn.ui.views.list_users", return_value=[admin_user]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    with patch("engn.ui.views.remove_user", return_value=False):
        view._remove_user("nonexistent@example.com")

    # Should show error
    assert any("Failed to remove" in str(o.content.value) for o in mock_page.overlay)


def test_admin_view_show_error(mock_page, admin_user):
    with patch("engn.ui.views.list_users", return_value=[]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view._show_error("Test error message")

    assert len(mock_page.overlay) == 1
    assert mock_page.overlay[0].content.value == "Test error message"
    assert mock_page.overlay[0].bgcolor == ft.Colors.RED_900


def test_admin_view_show_success(mock_page, admin_user):
    with patch("engn.ui.views.list_users", return_value=[]):
        view = AdminView(page=mock_page, user=admin_user, on_back=MagicMock())

    view._show_success("Test success message")

    assert len(mock_page.overlay) == 1
    assert mock_page.overlay[0].content.value == "Test success message"
    assert mock_page.overlay[0].bgcolor == ft.Colors.GREEN_900


def test_admin_view_back_button(mock_page, admin_user):
    on_back = MagicMock()

    with patch("engn.ui.views.list_users", return_value=[]):
        view = AdminView(page=mock_page, user=admin_user, on_back=on_back)

    # The back button is in the controls
    view.on_back()

    on_back.assert_called_once()
