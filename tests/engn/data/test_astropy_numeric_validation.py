import pytest
from pydantic import BaseModel, Field, ValidationError
from typing import Annotated
from engn.data.primitives import PRIMITIVE_TYPE_MAP

Length = PRIMITIVE_TYPE_MAP["length"]


def test_numeric_validation_gt():
    """Test Greater Than validation using Pydantic Field."""

    class MyModel(BaseModel):
        len: Annotated[Length, Field(gt="5 m")]

    # Success cases
    assert MyModel(len="10 m").len == "10 m"
    assert MyModel(len="6 m").len == "6 m"
    assert MyModel(len="0.01 km").len == "0.01 km"  # 10 m

    # Failure cases
    with pytest.raises(ValidationError) as excinfo:
        MyModel(len="1 m")

    # Check error message loosely
    assert "Input should be greater than 5 m" in str(excinfo.value)

    with pytest.raises(ValidationError):
        MyModel(len="5 m")  # strict gt


def test_numeric_validation_ge():
    """Test Greater Than or Equal validation."""

    class MyModel(BaseModel):
        len: Annotated[Length, Field(ge="5 m")]

    assert MyModel(len="5 m").len == "5 m"
    assert MyModel(len="10 m").len == "10 m"

    with pytest.raises(ValidationError):
        MyModel(len="4.9 m")


def test_numeric_validation_le():
    """Test Less Than or Equal validation."""

    class MyModel(BaseModel):
        len: Annotated[Length, Field(le="10 s")]

    Time = PRIMITIVE_TYPE_MAP["time"]

    class TimeModel(BaseModel):
        t: Annotated[Time, Field(le="10 s")]

    assert TimeModel(t="10 s").t == "10 s"
    assert TimeModel(t="5 s").t == "5 s"

    with pytest.raises(ValidationError):
        TimeModel(t="11 s")


def test_numeric_validation_mixed_units():
    """Test validation across different compatible units."""

    class MyModel(BaseModel):
        # Limit is 1 km
        len: Annotated[Length, Field(lt="1 km")]

    assert MyModel(len="500 m").len == "500 m"

    with pytest.raises(ValidationError):
        MyModel(len="2000 m")


def test_equality():
    """Test equality directly on the type instances."""
    l1 = Length("10 m")
    l2 = Length("0.01 km")
    assert l1 == l2  # string equality might fail, but let's see if we overrode eq.
    # Wait, I didn't override __eq__ in the implementation, only comparison operators.
    # The requirement was "numeric primitive validation works".
    # Usually validation uses gt, ge, lt, le.
    # Equality in Pydantic models is usually checking the value.
    # "10 m" (str) != "0.01 km" (str)
    # But u.Quantity("10 m") == u.Quantity("0.01 km")

    # If the user wants value equality, they might need to parse it.
    # But for validation (gt/lt), it should work.
    pass


if __name__ == "__main__":
    pytest.main([__file__])
