import pytest
from engn.config import ProjectConfig, AuthConfig
from sysengn.auth import Authenticator


@pytest.fixture
def authenticator():
    config = ProjectConfig(
        auth=AuthConfig(
            username="testuser",
            password_hash="$argon2id$v=19$m=65536,t=3,p=4$passwordhashplaceholder",
        )
    )
    # Mocking the hash for valid verification if possible or using a real hash
    # For this test, let's create a real hash using the authenticator's hasher first to be safe
    auth = Authenticator(config)
    real_hash = auth.hash_password("password123")
    config.auth.password_hash = real_hash
    return Authenticator(config)


def test_hash_password(authenticator):
    password = "secret_password"
    hashed = authenticator.hash_password(password)
    assert hashed != password
    assert hashed.startswith("$argon2id")


def test_authenticate_success(authenticator):
    assert authenticator.authenticate("testuser", "password123") is True


def test_authenticate_wrong_password(authenticator):
    assert authenticator.authenticate("testuser", "wrongpassword") is False


def test_authenticate_wrong_username(authenticator):
    assert authenticator.authenticate("wronguser", "password123") is False


def test_authenticate_no_auth_config():
    config = ProjectConfig()
    auth = Authenticator(config)
    assert auth.authenticate("user", "pass") is False
