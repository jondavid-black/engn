from engn.core.auth import (
    Role as Role,
    User as User,
    authenticate_local_user as authenticate_local_user,
    update_user_theme_preference as update_user_theme_preference,
)
from engn.config import ProjectConfig


class Authenticator:
    def __init__(self, config: ProjectConfig):
        self.config = config

    def get_current_user(self) -> User:
        """
        Get the current user based on configuration.
        """
        username = (
            self.config.auth.username
            if self.config.auth and self.config.auth.username
            else "admin"
        )

        return User(
            id="1",
            email=f"{username}@example.com",
            name=username,
            first_name=username.capitalize(),
            last_name="User",
            roles=[Role.ADMIN, Role.USER],
            theme_preference="DARK",
        )

    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate a user.
        """
        user = authenticate_local_user(email, password)
        return user is not None
