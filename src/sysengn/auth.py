from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from engn.config import ProjectConfig


class Role(Enum):
    ADMIN = auto()
    USER = auto()


@dataclass
class User:
    id: str
    name: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_color: Optional[str] = None
    theme_preference: str = "DARK"
    roles: list[Role] = field(default_factory=list)

    def has_role(self, role: Role) -> bool:
        return role in self.roles


def update_user_theme_preference(user_id: str, preference: str) -> None:
    """
    Update the user's theme preference.
    For now, this is a stub as we don't have a database.
    """
    pass


class Authenticator:
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.ph = PasswordHasher()

    def get_current_user(self) -> User:
        """
        Get the current user based on configuration.
        Since we only have single user auth via config, we return a default admin user
        mapped to that config.
        """
        username = (
            self.config.auth.username
            if self.config.auth and self.config.auth.username
            else "admin"
        )

        return User(
            id="1",
            name=username,
            email=f"{username}@example.com",
            first_name=username.capitalize(),
            last_name="User",
            roles=[Role.ADMIN, Role.USER],
            theme_preference="DARK",
        )

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate a user against the configuration.
        """
        if (
            not self.config.auth
            or not self.config.auth.username
            or not self.config.auth.password_hash
        ):
            return False

        if username != self.config.auth.username:
            return False

        try:
            self.ph.verify(self.config.auth.password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    def hash_password(self, password: str) -> str:
        """
        Hash a password for storage.
        """
        return self.ph.hash(password)
