from engn.main import load_standard_modules
from engn.data.models import _MODULE_REGISTRY


def test_load_standard_modules():
    """Test that standard modules are correctly loaded into the registry."""
    # Ensure registry is clear before test
    _MODULE_REGISTRY.clear()

    load_standard_modules()

    # Check if SysML-v1 is loaded
    assert "SysML-v1" in _MODULE_REGISTRY
    assert _MODULE_REGISTRY["SysML-v1"].name == "SysML-v1"
    assert "mbse/sysml_v1/sysml_v1_schema.jsonl" in _MODULE_REGISTRY["SysML-v1"].files
