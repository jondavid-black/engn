import pytest
from engn.core.auth import (
    User,
    Role,
    authenticate_local_user,
    create_user,
    update_user_theme_preference,
    update_user_profile,
)


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    config_file = tmp_path / "engn.toml"
    monkeypatch.setattr("engn.core.auth.CONFIG_PATH", config_file)
    return config_file


def test_create_user(temp_config):
    user = create_user("test@example.com", "password123", name="Test User")
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert Role.USER in user.roles
    assert temp_config.exists()


def test_authenticate_local_user_success(temp_config):
    create_user("test@example.com", "password123", name="Test User")
    user = authenticate_local_user("test@example.com", "password123")
    assert user is not None
    assert user.email == "test@example.com"


def test_authenticate_local_user_fail(temp_config):
    create_user("test@example.com", "password123")
    user = authenticate_local_user("test@example.com", "wrongpassword")
    assert user is None


def test_authenticate_initial_admin(temp_config):
    # When no users exist, it should create an initial admin
    user = authenticate_local_user("admin@example.com", "adminpass")
    assert user is not None
    assert user.email == "admin@example.com"
    assert Role.ADMIN in user.roles

    # Verify it was actually saved
    user2 = authenticate_local_user("admin@example.com", "adminpass")
    assert user2 is not None
    assert user2.id == user.id


def test_update_theme_preference(temp_config):
    user = create_user("test@example.com", "password123")
    update_user_theme_preference(user.id, "LIGHT")

    authenticated_user = authenticate_local_user("test@example.com", "password123")
    assert authenticated_user is not None
    assert authenticated_user.theme_preference == "LIGHT"


def test_update_user_profile(temp_config):
    user = create_user("test@example.com", "password123")
    update_user_profile(user.id, "First", "Last", "blue")

    authenticated_user = authenticate_local_user("test@example.com", "password123")
    assert authenticated_user is not None
    assert authenticated_user.first_name == "First"
    assert authenticated_user.last_name == "Last"
    assert authenticated_user.preferred_color == "blue"


def test_duplicate_user_fails(temp_config):
    create_user("test@example.com", "password123")
    with pytest.raises(ValueError, match="already exists"):
        create_user("test@example.com", "otherpass")


def test_user_has_role():
    user = User(id="1", email="t@t.com", roles=[Role.ADMIN])
    assert user.has_role(Role.ADMIN)
    assert not user.has_role(Role.USER)


def test_user_has_permission():
    admin = User(id="1", email="a@a.com", roles=[Role.ADMIN])
    user = User(id="2", email="u@u.com", roles=[Role.USER])

    assert admin.has_permission("anything")
    assert not user.has_permission("anything")
