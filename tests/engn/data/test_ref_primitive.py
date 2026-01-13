import pytest
from typing import List, Union
from engn.data.models import TypeDef, Property, Enumeration
from engn.data.dynamic import gen_pydantic_models


def test_ref_parsing():
    schema_defs: List[Union[TypeDef, Enumeration]] = [
        TypeDef(
            name="User",
            properties=[
                Property(name="id", type="int"),
                Property(name="name", type="str"),
            ],
        ),
        TypeDef(
            name="Post",
            properties=[
                Property(name="id", type="int"),
                Property(name="user_id", type="ref[User.id]"),
                Property(name="content", type="str"),
            ],
        ),
    ]

    try:
        pydantic_models = gen_pydantic_models(schema_defs)
    except Exception as e:
        pytest.fail(f"Model generation failed: {e}")

    assert "User" in pydantic_models
    assert "Post" in pydantic_models

    User = pydantic_models["User"]
    Post = pydantic_models["Post"]

    # Verify User.id is Optional[int] (since default presence is optional)
    from typing import Optional

    assert User.model_fields["id"].annotation == Optional[int]

    # Verify Post.user_id is Optional[int] (inherited from User.id)
    assert Post.model_fields["user_id"].annotation == Optional[int]

    # Verify metadata
    field_info = Post.model_fields["user_id"]
    # Pydantic V2 stores it in json_schema_extra
    extra = field_info.json_schema_extra
    assert extra is not None
    assert isinstance(extra, dict)
    assert extra["reference_target"] == "User.id"


def test_ref_parsing_error_invalid_format():
    # This should fail during Property validation, before gen_pydantic_models
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="Must be in format ref"):
        TypeDef(name="BadRef", properties=[Property(name="bad", type="ref[Invalid]")])


def test_ref_parsing_error_missing_target_type():
    schema_defs: List[Union[TypeDef, Enumeration]] = [
        TypeDef(
            name="MissingType",
            properties=[Property(name="bad", type="ref[NonExistent.id]")],
        )
    ]

    with pytest.raises(ValueError, match="Unable to resolve dependencies"):
        gen_pydantic_models(schema_defs)


def test_ref_parsing_error_missing_target_property():
    from pydantic import ValidationError

    with pytest.raises(
        (ValueError, ValidationError),
        match="Property 'non_existent' not found in type 'User'",
    ):
        schema_defs: List[Union[TypeDef, Enumeration]] = [
            TypeDef(name="User", properties=[Property(name="id", type="int")]),
            TypeDef(
                name="BadProp",
                properties=[Property(name="bad", type="ref[User.non_existent]")],
            ),
        ]
        gen_pydantic_models(schema_defs)
