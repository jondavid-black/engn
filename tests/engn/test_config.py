from pathlib import Path
from engn.config import ProjectConfig


def test_load_defaults(tmp_path: Path):
    """Test loading configuration when no file exists returns defaults."""
    config = ProjectConfig.load(tmp_path)
    assert config.pm_path == "pm"
    assert config.sysengn_path == "arch"


def test_load_from_file(tmp_path: Path):
    """Test loading configuration from a valid toml file."""
    config_file = tmp_path / "engn.toml"
    content = """
    [paths]
    pm = "management"
    sysengn = "architecture"
    """
    config_file.write_text(content, encoding="utf-8")

    config = ProjectConfig.load(tmp_path)
    assert config.pm_path == "management"
    assert config.sysengn_path == "architecture"


def test_load_partial_config(tmp_path: Path):
    """Test loading when only some fields are defined."""
    config_file = tmp_path / "engn.toml"
    content = """
    [paths]
    pm = "custom_pm"
    """
    config_file.write_text(content, encoding="utf-8")

    config = ProjectConfig.load(tmp_path)
    assert config.pm_path == "custom_pm"
    assert config.sysengn_path == "arch"  # default


def test_load_invalid_toml(tmp_path: Path):
    """Test loading from an invalid toml file falls back to defaults."""
    config_file = tmp_path / "engn.toml"
    config_file.write_text("invalid toml content [}", encoding="utf-8")

    config = ProjectConfig.load(tmp_path)
    # Should safely return defaults instead of crashing
    assert config.pm_path == "pm"
    assert config.sysengn_path == "arch"
