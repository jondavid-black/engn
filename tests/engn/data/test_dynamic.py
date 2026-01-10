import pytest
from pydantic import BaseModel, ValidationError

from engn.data.dynamic import gen_pydantic_models
from engn.data.models import Enumeration, Property, TypeDef


def test_gen_simple_model():
    """Test generating a simple model with primitive fields."""
    user_def = TypeDef(
        name="User",
        description="A user profile",
        properties=[
            Property(name="id", type="int", presence="required"),
            Property(name="username", type="str", presence="required"),
            Property(name="email", type="str", presence="optional"),
        ],
    )

    registry = gen_pydantic_models([user_def])
    User = registry["User"]

    assert issubclass(User, BaseModel)
    assert User.__name__ == "User"

    # Test instantiation
    u = User(id=1, username="alice", engn_type="User")
    assert u.id == 1
    assert u.username == "alice"
    assert u.email is None
    assert u.engn_type == "User"

    # Test validation error
    with pytest.raises(ValidationError):
        User(id="not-an-int", username="bob")


def test_gen_enum():
    """Test generating an enumeration."""
    role_enum = Enumeration(
        name="Role",
        values=["admin", "editor", "viewer"],
    )

    registry = gen_pydantic_models([role_enum])
    Role = registry["Role"]

    assert Role.admin.value == "admin"
    assert Role.editor.value == "editor"


def test_gen_nested_models():
    """Test generating models with dependencies (nesting)."""
    address_def = TypeDef(
        name="Address",
        properties=[
            Property(name="street", type="str", presence="required"),
            Property(name="city", type="str", presence="required"),
        ],
    )

    user_def = TypeDef(
        name="User",
        properties=[
            Property(name="name", type="str", presence="required"),
            Property(name="address", type="Address", presence="required"),
        ],
    )

    # Pass in arbitrary order to test dependency resolution
    registry = gen_pydantic_models([user_def, address_def])

    User = registry["User"]
    Address = registry["Address"]

    addr = Address(street="123 Main St", city="Springfield", engn_type="Address")
    user = User(name="Bob", address=addr, engn_type="User")

    assert user.address.city == "Springfield"


def test_gen_list_map_fields():
    """Test list and map fields."""
    group_def = TypeDef(
        name="Group",
        properties=[
            Property(name="tags", type="list[str]", presence="required"),
            Property(name="scores", type="map[str, int]", presence="required"),
        ],
    )

    registry = gen_pydantic_models([group_def])
    Group = registry["Group"]

    g = Group(tags=["a", "b"], scores={"Alice": 10, "Bob": 20}, engn_type="Group")

    assert g.tags == ["a", "b"]
    assert g.scores["Alice"] == 10


def test_circular_dependency_error():
    """Test that circular dependencies raise an error."""
    a_def = TypeDef(
        name="A", properties=[Property(name="b", type="B", presence="required")]
    )
    b_def = TypeDef(
        name="B", properties=[Property(name="a", type="A", presence="required")]
    )

    with pytest.raises(ValueError, match="Unable to resolve dependencies"):
        gen_pydantic_models([a_def, b_def])
