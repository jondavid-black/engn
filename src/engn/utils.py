from importlib.metadata import version, PackageNotFoundError
import tomllib
from pathlib import Path


def get_version() -> str:
    """
    Retrieve the version from the installed package or pyproject.toml as a fallback.
    """
    try:
        return version("engn")
    except (PackageNotFoundError, ImportError):
        # Fallback for development when package is not installed
        try:
            pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("project", {}).get("version", "unknown")
        except Exception:
            pass
        return "unknown"
