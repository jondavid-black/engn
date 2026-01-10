from importlib.metadata import version, PackageNotFoundError
from pathlib import Path


def get_version() -> str:
    try:
        return version("engn")
    except PackageNotFoundError:
        return "Unknown (package not installed)"


def get_asset_path(path: str) -> Path:
    """
    Get the absolute path to a shared asset.

    Args:
        path: Relative path to the asset (e.g., 'images/logo.png')

    Returns:
        Path object pointing to the asset.
    """
    base_dir = Path(__file__).parent
    asset_path = base_dir / "assets" / path
    return asset_path
