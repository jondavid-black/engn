import pytest
from engn.core.auth import (
    User,
    Role,
    authenticate_local_user,
    create_user,
    update_user_theme_preference,
    update_user_profile,
    remove_user,
    list_users,
    get_user_by_email,
    add_role_to_user,
    remove_role_from_user,
    get_all_roles,
    add_role,
    remove_role,
    set_config_path,
)


@pytest.fixture
def temp_config(tmp_path):
    config_file = tmp_path / "engn.jsonl"
    set_config_path(config_file)
    yield config_file
    # Reset to default if possible, or just let it be since other tests don't use it
    # We don't have an easy way to reset to "default" without knowing it


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


def test_remove_user(temp_config):
    create_user("test@example.com", "password123")
    assert remove_user("test@example.com") is True
    # Should return False if user doesn't exist
    assert remove_user("test@example.com") is False


def test_remove_user_not_found(temp_config):
    assert remove_user("nonexistent@example.com") is False


def test_list_users(temp_config):
    create_user("user1@example.com", "pass1", name="User One")
    create_user("user2@example.com", "pass2", name="User Two")

    users = list_users()
    assert len(users) == 2
    emails = [u.email for u in users]
    assert "user1@example.com" in emails
    assert "user2@example.com" in emails


def test_list_users_empty(temp_config):
    users = list_users()
    assert len(users) == 0


def test_get_user_by_email(temp_config):
    create_user("test@example.com", "password123", name="Test User")

    user = get_user_by_email("test@example.com")
    assert user is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_get_user_by_email_not_found(temp_config):
    user = get_user_by_email("nonexistent@example.com")
    assert user is None


def test_add_role_to_user(temp_config):
    create_user("test@example.com", "password123")

    result = add_role_to_user("test@example.com", Role.ADMIN)
    assert result is True

    user = get_user_by_email("test@example.com")
    assert user is not None
    assert Role.ADMIN in user.roles


def test_add_role_to_user_already_has_role(temp_config):
    create_user("test@example.com", "password123", roles=[Role.USER])

    # Adding USER again should succeed but not duplicate
    result = add_role_to_user("test@example.com", Role.USER)
    assert result is True

    user = get_user_by_email("test@example.com")
    assert user is not None
    assert user.roles.count(Role.USER) == 1


def test_add_role_to_user_not_found(temp_config):
    result = add_role_to_user("nonexistent@example.com", Role.ADMIN)
    assert result is False


def test_remove_role_from_user(temp_config):
    create_user("test@example.com", "password123", roles=[Role.ADMIN, Role.USER])

    result = remove_role_from_user("test@example.com", Role.ADMIN)
    assert result is True

    user = get_user_by_email("test@example.com")
    assert user is not None
    assert Role.ADMIN not in user.roles
    assert Role.USER in user.roles


def test_remove_role_from_user_doesnt_have_role(temp_config):
    create_user("test@example.com", "password123", roles=[Role.USER])

    # Removing a role the user doesn't have should succeed silently
    result = remove_role_from_user("test@example.com", Role.ADMIN)
    assert result is True


def test_remove_role_from_user_not_found(temp_config):
    result = remove_role_from_user("nonexistent@example.com", Role.ADMIN)
    assert result is False


def test_get_all_roles():
    roles = get_all_roles()
    assert Role.ADMIN in roles
    assert Role.USER in roles
    assert Role.GUEST in roles
    assert len(roles) == 3


def test_add_role_raises_error():
    with pytest.raises(ValueError, match="Cannot add role"):
        add_role("REVIEWER")


def test_remove_role_raises_error():
    with pytest.raises(ValueError, match="Cannot remove role"):
        remove_role("ADMIN")
