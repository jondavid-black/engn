import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
        Load configuration from engn.jsonl or engn.toml in the project root.
        If file doesn't exist, return defaults.
        """
        # Try engn.jsonl first
        jsonl_path = project_root / "engn.jsonl"
        if jsonl_path.exists():
            try:
                with open(jsonl_path, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        if data.get("engn_type") == "ProjectConfig":
                            return cls(
                                pm_path=data.get("pm_path", "pm"),
                                sysengn_path=data.get("sysengn_path", "arch"),
                                ux_path=data.get("ux_path", "ux"),
                                auth=AuthConfig(),  # Auth moved to workspace level
                            )
            except Exception:
                pass

        # Fallback to engn.toml
        config_path = project_root / "engn.toml"
        if not config_path.exists():
            return cls(auth=AuthConfig())

        try:
            import tomllib

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
            return cls(auth=AuthConfig())
