import pytest

from engn.data.models import Property
from engn.data.primitives import PRIMITIVE_TYPE_MAP, ReferenceMarker


def test_primitive_map_completeness():
    """Ensure standard types and astropy types are registered."""
    assert "str" in PRIMITIVE_TYPE_MAP
    assert "int" in PRIMITIVE_TYPE_MAP
    assert "length" in PRIMITIVE_TYPE_MAP  # Astropy
    assert "mass" in PRIMITIVE_TYPE_MAP  # Astropy
    assert "PositiveInt" in PRIMITIVE_TYPE_MAP  # Pydantic


def test_astropy_quantity_validation():
    """Test that Astropy quantity types validate correctly."""
    LengthType = PRIMITIVE_TYPE_MAP["length"]

    # Valid length
    val = LengthType.validate("10 m")
    assert val == "10 m"

    # Valid length (different unit)
    val = LengthType.validate("10 km")
    assert val == "10 km"

    # Invalid unit (mass instead of length)
    with pytest.raises(ValueError, match="Physical type mismatch"):
        LengthType.validate("10 kg")

    # Invalid format
    with pytest.raises(ValueError, match="Invalid quantity"):
        LengthType.validate("not a quantity")


def test_property_type_validation_primitive():
    """Test validation of known primitives."""
    # Should pass
    p = Property(name="test_prop", type="str")
    assert p.type == "str"

    p = Property(name="test_prop", type="length")
    assert p.type == "length"


def test_property_type_validation_generics():
    """Test validation of list, map, and ref generics."""
    # List
    p = Property(name="test_list", type="list[str]")
    assert p.type == "list[str]"

    # Map
    p = Property(name="test_map", type="map[str]")
    assert p.type == "map[str]"

    # Ref
    p = Property(name="test_ref", type="ref[SomeType]")
    assert p.type == "ref[SomeType]"


def test_property_type_unknown_but_allowed():
    """Test that unknown types (potential TypeDefs) are allowed."""
    # This is currently allowed by logic, assuming it's a TypeDef reference
    p = Property(name="test_custom", type="CustomUserType")
    assert p.type == "CustomUserType"


def test_reference_marker():
    """Test ReferenceMarker behavior."""
    ref1 = ReferenceMarker("TargetA")
    ref2 = ReferenceMarker("TargetA")
    ref3 = ReferenceMarker("TargetB")

    assert repr(ref1) == "ref[TargetA]"
    assert ref1 == ref2
    assert ref1 != ref3
