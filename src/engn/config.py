from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Try to import tomllib (Python 3.11+), otherwise fallback
try:
    import tomllib  # type: ignore
except ImportError:
    # For older python versions, you might need 'tomli' installed
    # But this project requires 3.12, so tomllib should be available.
    import tomllib  # type: ignore


@dataclass
class AuthConfig:
    username: str | None = None
    password_hash: str | None = None


@dataclass
class ProjectConfig:
    pm_path: str = "pm"
    sysengn_path: str = "arch"
    ux_path: str = "ux"
    auth: AuthConfig | None = None

    @classmethod
    def load(cls, project_root: Path) -> "ProjectConfig":
        """
        Load configuration from engn.toml in the project root.
        If file doesn't exist, return defaults.
        """
        config_path = project_root / "engn.toml"
        if not config_path.exists():
            return cls(auth=AuthConfig())

        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)

            # Extract paths from config if they exist
            paths: dict[str, Any] = data.get("paths", {})

            # Extract auth from config
            auth_data: dict[str, Any] = data.get("auth", {})
            auth_config = AuthConfig(
                username=auth_data.get("username"),
                password_hash=auth_data.get("password_hash"),
            )

            return cls(
                pm_path=paths.get("pm", "pm"),
                sysengn_path=paths.get("sysengn", "arch"),
                ux_path=paths.get("ux", "ux"),
                auth=auth_config,
            )
        except Exception:
            # Log warning? For now just return defaults on error
            return cls(auth=AuthConfig())
