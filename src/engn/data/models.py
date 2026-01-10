from typing import Any, Literal
from pydantic import BaseModel, Field


class BaseDataModel(BaseModel):
    """Base model for all data engine models."""

    model_config = {"extra": "forbid"}


class Enumeration(BaseDataModel):
    """
    Defines an enumerated type with a fixed set of values.
    """

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

    # Constraints can be added here as needed, mirroring the YASL example but kept simple for now
    list_min: int | None = None
    list_max: int | None = None


class TypeDef(BaseDataModel):
    """
    Defines a complex data type consisting of multiple properties.
    """

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

    types: list[TypeDef] = Field(
        default_factory=list, description="Collection of data type definitions"
    )
    enums: list[Enumeration] = Field(
        default_factory=list, description="Collection of enumeration definitions"
    )
