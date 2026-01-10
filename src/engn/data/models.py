from typing import Any, Literal
from pydantic import BaseModel, Field


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

    list_min: int | None = None
    list_max: int | None = None


class TypeDef(BaseDataModel):
    """
    Defines a complex data type consisting of multiple properties.
    """

    engn_type: Literal["type_def"] = "type_def"
    name: str = Field(description="Unique name of the data type")
    description: str | None = Field(
        default=None, description="Description of what this type represents"
    )
    properties: list[Property] = Field(
        default_factory=list, description="List of properties defining this type"
    )


class Schema(BaseDataModel):
    """
    Container for defining data types and enumerations.
    """

    # Schema doesn't need a discriminator if it's not stored in the mixed list,
    # but for consistency we can add it or leave it.
    # Usually Schema is a container, not an item in the stream.
    types: list[TypeDef] = Field(
        default_factory=list, description="Collection of data type definitions"
    )
    enums: list[Enumeration] = Field(
        default_factory=list, description="Collection of enumeration definitions"
    )
