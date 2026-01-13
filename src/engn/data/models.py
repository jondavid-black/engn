from typing import Any, Literal, Dict
import datetime
from pydantic import BaseModel, Field, field_validator

from engn.data.primitives import PRIMITIVE_TYPE_MAP

# Global registry to store defined types and enumerations for validation
_MODEL_REGISTRY: Dict[str, Any] = {}


class BaseDataModel(BaseModel):
    """Base model for all data engine models."""

    model_config = {"extra": "forbid"}


class Enumeration(BaseDataModel):
    """
    Defines an enumerated type with a fixed set of values.
    """

    engn_type: Literal["enum"] = "enum"
    name: str = Field(description="Unique name of the enumeration")
    description: str | None = Field(
        default=None, description="Description of what this enum represents"
    )
    values: list[str] = Field(description="List of allowed values")

    def model_post_init(self, __context: Any) -> None:
        _MODEL_REGISTRY[self.name] = self


class Property(BaseDataModel):
    """
    Defines a single property within a data type.
    """

    name: str = Field(description="Name of the property")
    type: str = Field(
        description="Type of the property (primitive, enum, or other TypeDef)"
    )
    description: str | None = Field(
        default=None, description="Description of the property"
    )
    presence: Literal["required", "optional"] = Field(
        default="optional", description="Whether the property is required"
    )
    default: Any | None = Field(
        default=None, description="Default value if not provided"
    )

    unique: bool | None = Field(
        default=False, description="Whether the value must be unique"
    )

    # list constraints
    list_min: int | None = Field(
        default=None, description="Minimum number of items in list"
    )
    list_max: int | None = Field(
        default=None, description="Maximum number of items in list"
    )

    # numeric constraints
    gt: float | int | None = Field(default=None, description="Greater than")
    ge: float | int | None = Field(default=None, description="Greater than or equal to")
    lt: float | int | None = Field(default=None, description="Less than")
    le: float | int | None = Field(default=None, description="Less than or equal to")
    exclude: list[float | int] | None = Field(
        default=None, description="Excluded values"
    )
    multiple_of: float | int | None = Field(
        default=None, description="Value must be a multiple of this"
    )
    whole_number: bool | None = Field(
        default=False, description="Must be a whole number"
    )

    # string constraints
    str_min: int | None = Field(default=None, description="Minimum string length")
    str_max: int | None = Field(default=None, description="Maximum string length")
    str_regex: str | None = Field(default=None, description="Regex pattern")

    # date / time constraints
    before: datetime.date | datetime.datetime | datetime.time | None = Field(
        default=None, description="Must be before this time/date"
    )
    after: datetime.date | datetime.datetime | datetime.time | None = Field(
        default=None, description="Must be after this time/date"
    )

    # path constraints
    path_exists: bool | None = Field(default=None, description="Path must exist")
    is_dir: bool | None = Field(default=None, description="Path must be a directory")
    is_file: bool | None = Field(default=None, description="Path must be a file")
    file_ext: list[str] | None = Field(
        default=None, description="Allowed file extensions"
    )

    # url constraints
    url_base: str | None = Field(default=None, description="Base URL required")
    url_protocols: list[str] | None = Field(
        default=None, description="Allowed URL protocols"
    )
    url_reachable: bool | None = Field(
        default=False, description="URL must be reachable"
    )

    # any constraints
    any_of: list[str] | None = Field(
        default=None, description="Must be one of these types"
    )

    # ref constraints
    no_ref_check: bool | None = Field(
        default=None, description="Skip reference checking"
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Check if it's a known primitive
        if v in PRIMITIVE_TYPE_MAP:
            return v

        # Check for list/map generics
        if v.startswith("list[") and v.endswith("]"):
            # Simple recursive check (could be improved)
            # inner = v[5:-1]
            # Recursively validate inner type would be ideal but for now we just
            # check primitives or assume it's a forward reference to a defined type
            return v
        if v.startswith("map[") and v.endswith("]"):
            inner = v[4:-1]
            # Split by the first comma only, as complex value types might contain commas
            parts = inner.split(",", 1)

            if len(parts) != 2:
                raise ValueError(
                    f"Invalid map definition '{v}': Map type definition must take exactly 2 arguments (key, value)"
                )

            key_type = parts[0].strip()
            # value_type = parts[1].strip() # We don't strictly validate value type yet as it can be any custom type

            if key_type not in ("int", "str", "enum"):
                raise ValueError(
                    f"Invalid map key type '{key_type}': Map key type must be one of: int, str, enum"
                )

            # Validate that the value part does not contain top-level commas (meaning >2 args)
            value_part = parts[1].strip()
            bracket_depth = 0
            for char in value_part:
                if char == "[":
                    bracket_depth += 1
                elif char == "]":
                    bracket_depth -= 1
                elif char == "," and bracket_depth == 0:
                    raise ValueError(
                        f"Invalid map definition '{v}': Map type definition must take exactly 2 arguments (key, value)"
                    )

            return v
        if v.startswith("ref[") and v.endswith("]"):
            inner = v[4:-1]
            if "." not in inner:
                raise ValueError(
                    f"Invalid ref definition '{v}': Must be in format ref[Type.Property]"
                )
            parts = inner.split(".")
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid ref definition '{v}': Must be in format ref[Type.Property]"
                )
            if not parts[0] or not parts[1]:
                raise ValueError(
                    f"Invalid ref definition '{v}': Type and Property names cannot be empty"
                )
            # ensure parts[0] is a known type and parts[1] is a property of that type
            type_name = parts[0]
            prop_name = parts[1]

            if type_name in _MODEL_REGISTRY:
                target = _MODEL_REGISTRY[type_name]
                if isinstance(target, TypeDef):
                    if not any(p.name == prop_name for p in target.properties):
                        raise ValueError(
                            f"Property '{prop_name}' not found in type '{type_name}'"
                        )
                elif isinstance(target, Enumeration):
                    raise ValueError(
                        f"Cannot reference property '{prop_name}' on Enumeration '{type_name}'"
                    )

            return v

        # If not primitive, we assume it's a reference to a TypeDef or Enum defined elsewhere
        # Strict validation would require context of the whole schema, which we don't have here.
        return v


class TypeDef(BaseDataModel):
    """
    Defines a complex data type consisting of multiple properties.
    """

    engn_type: Literal["type_def"] = "type_def"
    name: str = Field(description="Unique name of the data type")
    extends: str | None = Field(
        default=None, description="Name of the parent type to extend"
    )
    description: str | None = Field(
        default=None, description="Description of what this type represents"
    )
    properties: list[Property] = Field(
        default_factory=list, description="List of properties defining this type"
    )

    def model_post_init(self, __context: Any) -> None:
        _MODEL_REGISTRY[self.name] = self


class Schema(BaseDataModel):
    """
    Defines a complete data schema consisting of multiple types and enumerations.
    """

    types: list[TypeDef] = Field(
        default_factory=list, description="List of type definitions"
    )
    enums: list[Enumeration] = Field(
        default_factory=list, description="List of enumeration definitions"
    )
