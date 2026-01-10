import pytest
from pydantic import ValidationError

from engn.data.models import TypeDef, Property
from engn.data.dynamic import gen_pydantic_models


def test_numeric_validation():
    """Test numeric validation constraints."""
    prop = Property(name="age", type="int", gt=0, le=120, multiple_of=2)
    type_def = TypeDef(name="Person", properties=[prop])

    models = gen_pydantic_models([type_def])
    Person = models["Person"]

    # Valid case
    p = Person(age=30)
    assert getattr(p, "age") == 30

    # Invalid: not greater than 0
    with pytest.raises(ValidationError) as exc:
        Person(age=0)
    assert "Input should be greater than 0" in str(exc.value)

    # Invalid: greater than 120
    # Note: 121 is not a multiple of 2, so it might fail that check first or as well.
    # To reliably test 'le', we should use a value that IS a multiple of 2 but > 120.
    with pytest.raises(ValidationError) as exc:
        Person(age=122)
    assert "Input should be less than or equal to 120" in str(exc.value)

    # Invalid: not multiple of 2
    with pytest.raises(ValidationError) as exc:
        Person(age=31)
    assert "Input should be a multiple of 2" in str(exc.value)


def test_string_validation():
    """Test string validation constraints."""
    prop = Property(name="code", type="str", str_min=3, str_max=5, str_regex="^[A-Z]+$")
    type_def = TypeDef(name="Product", properties=[prop])

    models = gen_pydantic_models([type_def])
    Product = models["Product"]

    # Valid case
    p = Product(code="ABC")
    assert getattr(p, "code") == "ABC"

    # Invalid: too short
    with pytest.raises(ValidationError) as exc:
        Product(code="AB")
    assert "String should have at least 3 characters" in str(exc.value)

    # Invalid: too long
    with pytest.raises(ValidationError) as exc:
        Product(code="ABCDEF")
    assert "String should have at most 5 characters" in str(exc.value)

    # Invalid: regex mismatch
    with pytest.raises(ValidationError) as exc:
        Product(code="abc")
    assert "String should match pattern '^[A-Z]+$'" in str(exc.value)


def test_list_validation():
    """Test list validation constraints."""
    prop = Property(name="tags", type="list[str]", list_min=1, list_max=3)
    type_def = TypeDef(name="Post", properties=[prop])

    models = gen_pydantic_models([type_def])
    Post = models["Post"]

    # Valid case
    p = Post(tags=["news"])
    assert getattr(p, "tags") == ["news"]

    # Invalid: too few items
    with pytest.raises(ValidationError) as exc:
        Post(tags=[])
    assert "List should have at least 1 item" in str(exc.value)

    # Invalid: too many items
    with pytest.raises(ValidationError) as exc:
        Post(tags=["a", "b", "c", "d"])
    assert "List should have at most 3 items" in str(exc.value)
