import os
import uuid
import logging
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Any

# Workaround for flet 0.80.1 ImportError
import flet.version

if not hasattr(flet.version, "version"):
    setattr(flet.version, "version", flet.version.__version__)


from flet.auth.oauth_provider import OAuthProvider
from flet.auth.providers import GitHubOAuthProvider, GoogleOAuthProvider

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from pydantic import BaseModel

from engn.data.storage import JSONLStorage

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("engn.jsonl")
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
    roles_hash: Optional[str] = None
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


def _get_storage() -> JSONLStorage[Any]:
    """Get a JSONLStorage instance for the config file."""
    return JSONLStorage(CONFIG_PATH, [])


def _calculate_roles_hash(roles: list[str]) -> str:
    """Calculates a hash for the user's roles."""
    roles_str = ",".join(sorted(roles))
    return hashlib.sha256(roles_str.encode()).hexdigest()


def _read_all_items() -> list[Any]:
    """Read all items from the JSONL config file."""
    storage = _get_storage()
    return storage.read()


def _get_users_data() -> list[dict[str, Any]]:
    """Extract user data items from the config."""
    import json

    users = []
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get("engn_type") == "User":
                        users.append(data)
                except json.JSONDecodeError:
                    continue
    return users


def authenticate_local_user(email: str, password: str) -> Optional[User]:
    """Authenticates a user against the local config file."""
    users_data = _get_users_data()

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
                    id=str(user_data["id"]),
                    email=user_data["email"],
                    name=user_data.get("name"),
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                    preferred_color=user_data.get("preferred_color"),
                    default_project=user_data.get("default_project"),
                    roles=roles,
                    roles_hash=user_data.get("roles_hash"),
                    theme_preference=user_data.get("theme_preference", "DARK"),
                )
            except VerifyMismatchError:
                return None
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                return None

    # If no users exist, create the first one
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

    users_data = _get_users_data()

    # Check if user already exists
    if any(u.get("email") == email for u in users_data):
        raise ValueError(f"User with email {email} already exists")

    # Build user dict with the new data
    roles_list = [r.value for r in roles]
    roles_hash = _calculate_roles_hash(roles_list)
    user_dict = {
        "engn_type": "User",
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "roles": roles_list,
        "roles_hash": roles_hash,
        "theme_preference": "DARK",
    }
    if name:
        user_dict["name"] = name
        user_dict["first_name"] = name.split()[0] if name else None
        user_dict["last_name"] = (
            " ".join(name.split()[1:]) if len(name.split()) > 1 else None
        )

    # Append by writing to file in append mode
    import json

    with CONFIG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(user_dict) + "\n")

    return User(
        id=user_id,
        email=email,
        name=name,
        first_name=user_dict.get("first_name"),
        last_name=user_dict.get("last_name"),
        roles=roles,
        roles_hash=roles_hash,
        theme_preference="DARK",
        default_project=None,
    )


def update_user_theme_preference(user_id: str, theme_mode: str) -> None:
    """Updates the user's theme preference in the config file."""
    _update_user_field(user_id, "theme_preference", theme_mode)


def update_user_default_project(user_id: str, default_project: Optional[str]) -> None:
    """Updates the user's default project in the config file."""
    _update_user_field(user_id, "default_project", default_project)


def update_user_profile(
    user_id: str,
    first_name: Optional[str],
    last_name: Optional[str],
    preferred_color: Optional[str],
) -> None:
    """Updates the user's profile information in the config file."""
    import json

    lines = []
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()

    updated = False
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("engn_type") == "User" and str(data.get("id")) == user_id:
                data["first_name"] = first_name
                data["last_name"] = last_name
                data["preferred_color"] = preferred_color
                updated = True
            new_lines.append(json.dumps(data) + "\n")
        except json.JSONDecodeError:
            new_lines.append(line + "\n")

    if updated:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            f.writelines(new_lines)


def _update_user_field(user_id: str, field_name: str, value: Any) -> None:
    """Generic helper to update a single field for a user."""
    import json

    lines = []
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()

    updated = False
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("engn_type") == "User" and str(data.get("id")) == user_id:
                data[field_name] = value
                updated = True
            new_lines.append(json.dumps(data) + "\n")
        except json.JSONDecodeError:
            new_lines.append(line + "\n")

    if updated:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            f.writelines(new_lines)


def remove_user(email: str) -> bool:
    """Removes a user from the config file by email. Returns True if removed."""
    import json

    lines = []
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()

    removed = False
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("engn_type") == "User" and data.get("email") == email:
                removed = True
                continue  # Skip this line
            new_lines.append(json.dumps(data) + "\n")
        except json.JSONDecodeError:
            new_lines.append(line + "\n")

    if removed:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return removed


def list_users() -> list[User]:
    """Returns a list of all users."""
    users_data = _get_users_data()
    users = []
    for user_data in users_data:
        roles = [Role(r) for r in user_data.get("roles", [])]
        users.append(
            User(
                id=str(user_data["id"]),
                email=user_data["email"],
                name=user_data.get("name"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                preferred_color=user_data.get("preferred_color"),
                default_project=user_data.get("default_project"),
                roles=roles,
                roles_hash=user_data.get("roles_hash"),
                theme_preference=user_data.get("theme_preference", "DARK"),
            )
        )
    return users


def get_user_by_email(email: str) -> Optional[User]:
    """Gets a user by email address."""
    users_data = _get_users_data()
    for user_data in users_data:
        if user_data.get("email") == email:
            roles = [Role(r) for r in user_data.get("roles", [])]
            return User(
                id=str(user_data["id"]),
                email=user_data["email"],
                name=user_data.get("name"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                preferred_color=user_data.get("preferred_color"),
                default_project=user_data.get("default_project"),
                roles=roles,
                roles_hash=user_data.get("roles_hash"),
                theme_preference=user_data.get("theme_preference", "DARK"),
            )
    return None


def add_role_to_user(email: str, role: Role) -> bool:
    """Adds a role to a user. Returns True if successful."""
    import json

    lines = []
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()

    updated = False
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("engn_type") == "User" and data.get("email") == email:
                current_roles = data.get("roles", [])
                if role.value not in current_roles:
                    current_roles.append(role.value)
                    data["roles"] = current_roles
                    data["roles_hash"] = _calculate_roles_hash(current_roles)
                updated = True
            new_lines.append(json.dumps(data) + "\n")
        except json.JSONDecodeError:
            new_lines.append(line + "\n")

    if updated:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return updated


def remove_role_from_user(email: str, role: Role) -> bool:
    """Removes a role from a user. Returns True if successful."""
    import json

    lines = []
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()

    updated = False
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("engn_type") == "User" and data.get("email") == email:
                current_roles = data.get("roles", [])
                if role.value in current_roles:
                    current_roles.remove(role.value)
                    data["roles"] = current_roles
                    data["roles_hash"] = _calculate_roles_hash(current_roles)
                updated = True
            new_lines.append(json.dumps(data) + "\n")
        except json.JSONDecodeError:
            new_lines.append(line + "\n")

    if updated:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return updated


def get_all_roles() -> list[Role]:
    """Returns a list of all available roles."""
    return list(Role)


def add_role(role_name: str) -> None:
    """
    Note: Roles are defined as an Enum and cannot be dynamically added at runtime.
    This function is a placeholder that raises an error explaining this.
    """
    raise ValueError(
        f"Cannot add role '{role_name}'. Roles are defined in the Role enum "
        "and require code changes to add new roles."
    )


def remove_role(role_name: str) -> None:
    """
    Note: Roles are defined as an Enum and cannot be dynamically removed at runtime.
    This function is a placeholder that raises an error explaining this.
    """
    raise ValueError(
        f"Cannot remove role '{role_name}'. Roles are defined in the Role enum "
        "and require code changes to remove roles."
    )
