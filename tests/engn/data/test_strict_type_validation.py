import pytest
from pydantic import ValidationError
from engn.data.models import TypeDef, Property, Enumeration, Schema


def test_schema_strict_type_validation_success():
    """Verify that a valid schema passes validation."""
    enum = Enumeration(name="Status", values=["active", "inactive"])
    prop = Property(name="status", type="Status")
    typedef = TypeDef(name="Person", properties=[prop])

    # This should pass
    schema = Schema(types=[typedef], enums=[enum])
    assert len(schema.types) == 1
    assert len(schema.enums) == 1


def test_schema_strict_type_validation_missing_type():
    """Verify that a schema with a missing type fails validation."""
    prop = Property(name="address", type="Address")
    typedef = TypeDef(name="Person", properties=[prop])

    # Address is not defined in the schema
    with pytest.raises(ValidationError, match="Unknown type 'Address'"):
        Schema(types=[typedef], enums=[])


def test_schema_strict_type_validation_missing_type_in_list():
    """Verify that a schema with a missing type in a list generic fails validation."""
    prop = Property(name="tags", type="list[Tag]")
    typedef = TypeDef(name="Person", properties=[prop])

    # Tag is not defined
    with pytest.raises(ValidationError, match="Unknown type 'Tag'"):
        Schema(types=[typedef], enums=[])


def test_schema_strict_type_validation_missing_type_in_map_value():
    """Verify that a schema with a missing type in a map generic value fails validation."""
    prop = Property(name="metadata", type="map[str, Meta]")
    typedef = TypeDef(name="Person", properties=[prop])

    # Meta is not defined
    with pytest.raises(ValidationError, match="Unknown type 'Meta'"):
        Schema(types=[typedef], enums=[])


def test_schema_strict_type_validation_ref_target_missing():
    """Verify that a schema with a missing ref target type fails validation."""
    # Note: ref[NonExistent.id] should fail
    prop = Property(name="ref", type="ref[NonExistent.id]")
    typedef = TypeDef(name="Person", properties=[prop])

    with pytest.raises(ValidationError, match="Unknown type 'NonExistent'"):
        Schema(types=[typedef], enums=[])
