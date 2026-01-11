import os
import uuid
import logging
import tomllib
import tomli_w
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Any, Mapping, cast

# Workaround for flet 0.80.1 ImportError
import flet.version

if not hasattr(flet.version, "version"):
    setattr(flet.version, "version", flet.version.__version__)


from flet.auth.oauth_provider import OAuthProvider
from flet.auth.providers import GitHubOAuthProvider, GoogleOAuthProvider

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("engn.toml")
ph = PasswordHasher()


class Role(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


@dataclass
class User:
    """Represents an authenticated user."""

    id: str
    email: str
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_color: Optional[str] = None
    default_project: Optional[str] = None
    roles: list[Role] = field(default_factory=list)
    theme_preference: str = "DARK"

    def has_role(self, role: Role) -> bool:
        """Checks if the user has a specific role."""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Checks if the user has a specific permission."""
        if Role.ADMIN in self.roles:
            return True
        return False


def get_oauth_providers() -> list[OAuthProvider]:
    """Configures and returns the list of available OAuth providers."""
    providers: list[OAuthProvider] = []

    # Google
    g_id = os.getenv("GOOGLE_CLIENT_ID")
    g_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if g_id and g_secret:
        providers.append(
            GoogleOAuthProvider(
                client_id=g_id,
                client_secret=g_secret,
                redirect_url="http://localhost:8550/api/oauth/redirect",
            )
        )

    # GitHub
    gh_id = os.getenv("GITHUB_CLIENT_ID")
    gh_secret = os.getenv("GITHUB_CLIENT_SECRET")
    if gh_id and gh_secret:
        providers.append(
            GitHubOAuthProvider(
                client_id=gh_id,
                client_secret=gh_secret,
                redirect_url="http://localhost:8550/api/oauth/redirect",
            )
        )

    return providers


def _read_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"users": []}
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def _write_config(config: dict):
    def remove_none(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: remove_none(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [remove_none(v) for v in obj]
        return obj

    clean_config = cast(Mapping[str, Any], remove_none(config))
    with CONFIG_PATH.open("wb") as f:
        tomli_w.dump(clean_config, f)


def authenticate_local_user(email: str, password: str) -> Optional[User]:
    """Authenticates a user against the local config file."""
    config = _read_config()
    users_data = config.get("users", [])

    for user_data in users_data:
        if user_data.get("email") == email:
            stored_hash = user_data.get("password_hash")
            if not stored_hash:
                continue

            try:
                ph.verify(stored_hash, password)
                # Success
                roles = [Role(r) for r in user_data.get("roles", [])]
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    name=user_data.get("name"),
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                    preferred_color=user_data.get("preferred_color"),
                    default_project=user_data.get("default_project"),
                    roles=roles,
                    theme_preference=user_data.get("theme_preference", "DARK"),
                )
            except VerifyMismatchError:
                return None
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                return None

    # If no users exist, the example code suggested creating the first one
    if not users_data:
        logger.info("Creating initial admin user")
        return create_user(
            email, password, name="Admin User", roles=[Role.ADMIN, Role.USER]
        )

    return None


def create_user(
    email: str, password: str, name: str = "", roles: Optional[list[Role]] = None
) -> User:
    """Creates a new user in the config file."""
    if roles is None:
        roles = [Role.USER]

    password_hash = ph.hash(password)
    user_id = str(uuid.uuid4())

    config = _read_config()
    if "users" not in config:
        config["users"] = []

    # Check if user already exists
    if any(u.get("email") == email for u in config["users"]):
        raise ValueError(f"User with email {email} already exists")

    user_data = {
        "id": user_id,
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "roles": [r.value for r in roles],
        "theme_preference": "DARK",
        "default_project": None,
    }

    config["users"].append(user_data)
    _write_config(config)

    return User(
        id=user_id,
        email=email,
        name=name,
        roles=roles,
        theme_preference="DARK",
        default_project=None,
    )


def update_user_theme_preference(user_id: str, theme_mode: str) -> None:
    """Updates the user's theme preference in the config file."""
    config = _read_config()
    for user_data in config.get("users", []):
        if user_data.get("id") == user_id:
            user_data["theme_preference"] = theme_mode
            _write_config(config)
            return


def update_user_default_project(user_id: str, default_project: Optional[str]) -> None:
    """Updates the user's default project in the config file."""
    config = _read_config()
    for user_data in config.get("users", []):
        if user_data.get("id") == user_id:
            user_data["default_project"] = default_project
            _write_config(config)
            return


def update_user_profile(
    user_id: str,
    first_name: Optional[str],
    last_name: Optional[str],
    preferred_color: Optional[str],
) -> None:
    """Updates the user's profile information in the config file."""
    config = _read_config()
    for user_data in config.get("users", []):
        if user_data.get("id") == user_id:
            user_data["first_name"] = first_name
            user_data["last_name"] = last_name
            user_data["preferred_color"] = preferred_color
            _write_config(config)
            return
