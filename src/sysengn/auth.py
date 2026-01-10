from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from engn.config import ProjectConfig


class Authenticator:
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.ph = PasswordHasher()

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
