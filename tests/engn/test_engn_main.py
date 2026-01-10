import pytest
from unittest.mock import patch
from engn.main import main
from engn.utils import get_version


def test_get_version_fallback():
    # Test that get_version returns the unknown message when package is not found
    # We mock version to raise PackageNotFoundError to trigger the fallback
    with patch("engn.utils.version") as mock_version:
        from importlib.metadata import PackageNotFoundError

        mock_version.side_effect = PackageNotFoundError("Package not found")
        # Just ensure it returns the specific string for unknown version
        assert get_version() == "Unknown (package not installed)"


def test_engn_version_flag(capsys):
    with patch("sys.argv", ["engn", "--version"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out or get_version() in captured.out


def test_engn_no_args(capsys):
    with patch("sys.argv", ["engn"]):
        main()
        captured = capsys.readouterr()
        assert "Hello from engn!" in captured.out
