import pytest
from pathlib import Path
from engn.utils import get_asset_path


def test_get_asset_path_structure():
    """Test that get_asset_path returns a Path object with correct structure."""
    path = get_asset_path("images/logo.png")
    assert isinstance(path, Path)
    assert path.name == "logo.png"
    assert path.parent.name == "images"
    assert path.parent.parent.name == "assets"
    assert path.parent.parent.parent.name == "engn"


def test_get_asset_path_absolute():
    """Test that the returned path is absolute."""
    path = get_asset_path("test.txt")
    assert path.is_absolute()
