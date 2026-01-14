from typing import Any, Literal, Dict, Set
import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from engn.data.primitives import PRIMITIVE_TYPE_MAP

# Global registry to store defined types and enumerations for validation
_MODEL_REGISTRY: Dict[str, Any] = {}
_MODULE_REGISTRY: Dict[str, Any] = {}


def get_referenced_types(v: str) -> Set[str]:
    """
    Extracts all custom types referenced in a type definition string.
    Includes both structural dependencies and ref[] references.
    """
    if v in PRIMITIVE_TYPE_MAP:
        return set()

    if v.startswith("list[") and v.endswith("]"):
        inner = v[5:-1].strip()
        return get_referenced_types(inner)

    if v.startswith("map[") and v.endswith("]"):
        inner = v[4:-1].strip()
        parts = inner.split(",", 1)
        if len(parts) == 2:
            # map keys must be primitives (int, str, enum), but enum is a custom type
            key_type = parts[0].strip()
            val_type = parts[1].strip()
            refs = get_referenced_types(val_type)
            if key_type not in ("int", "str"):
                refs.add(key_type)
            return refs
        return set()

    if v.startswith("ref[") and v.endswith("]"):
        inner = v[4:-1].strip()
        parts = inner.split(".")
        if len(parts) >= 1:
            return {parts[0].strip()}
        return set()

    # Assume it's a direct type reference
    return {v}


def get_structural_dependencies(v: str) -> Set[str]:
    """
    Extracts custom types that are structural dependencies (embedded types).
    Excludes ref[] types since those are string references at runtime,
    not actual embedded type dependencies.
    """
    if v in PRIMITIVE_TYPE_MAP:
        return set()

    if v.startswith("list[") and v.endswith("]"):
        inner = v[5:-1].strip()
        return get_structural_dependencies(inner)

    if v.startswith("map[") and v.endswith("]"):
        inner = v[4:-1].strip()
        parts = inner.split(",", 1)
        if len(parts) == 2:
            key_type = parts[0].strip()
            val_type = parts[1].strip()
            refs = get_structural_dependencies(val_type)
            if key_type not in ("int", "str"):
                refs.add(key_type)
            return refs
        return set()

    # ref[] types are NOT structural dependencies
    if v.startswith("ref[") and v.endswith("]"):
        return set()

    # Assume it's a direct type reference (structural dependency)
    return {v}


class BaseDataModel(BaseModel):
    """Base model for all data engine models."""

    model_config = {"extra": "forbid"}


class Module(BaseDataModel):
    """
    Defines a module which is a named collection of JSONL files for reuse.
    """

    engn_type: Literal["module"] = "module"
    name: str = Field(description="Unique name of the module")
    description: str | None = Field(
        default=None, description="Description of the module"
    )
    files: list[str] = Field(description="List of JSONL file paths in this module")

    def model_post_init(self, __context: Any) -> None:
        _MODULE_REGISTRY[self.name] = self


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
            inner = v[5:-1].strip()
            # Recursively validate structure
            cls.validate_type(inner)
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
            value_type = parts[1].strip()

            if (
                key_type not in ("int", "str", "enum")
                and key_type not in PRIMITIVE_TYPE_MAP
            ):
                # if not a primitive key type, it might be an enum reference
                pass

            # Validate value type structure recursively
            cls.validate_type(value_type)

            # Validate that the value part does not contain top-level commas (meaning >2 args)
            bracket_depth = 0
            for char in value_type:
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

        # If not primitive, assume it's a reference to a TypeDef or Enum.
        # Strict validation is performed at the Schema level to support forward references.
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
    Defines a complete data schema consisting of multiple types, enumerations, and modules.
    """

    types: list[TypeDef] = Field(
        default_factory=list, description="List of type definitions"
    )
    enums: list[Enumeration] = Field(
        default_factory=list, description="List of enumeration definitions"
    )
    modules: list[Module] = Field(
        default_factory=list, description="List of module definitions"
    )

    @model_validator(mode="after")
    def validate_schema_types(self) -> "Schema":
        """
        Ensure all types referenced in properties are defined within the schema.
        """
        defined_types = {t.name for t in self.types} | {e.name for e in self.enums}

        for typedef in self.types:
            for prop in typedef.properties:
                referenced = get_referenced_types(prop.type)
                for ref_type in referenced:
                    if ref_type not in defined_types:
                        raise ValueError(
                            f"Unknown type '{ref_type}' referenced in property '{typedef.name}.{prop.name}'"
                        )
        return self


class Import(BaseDataModel):
    """
    Defines an import directive to include other JSONL files or named modules.

    Use files to include additional JSONL files in processing.
    Use modules to reference named modules defined with the 'module' type.
    """

    engn_type: Literal["import"] = "import"
    files: list[str] | None = Field(
        default=None, description="List of file paths to include in processing"
    )
    modules: list[str] | None = Field(
        default=None, description="List of module names to import"
    )

    @model_validator(mode="after")
    def validate_import(self) -> "Import":
        """Ensure at least one of files or modules is provided."""
        if not self.files and not self.modules:
            raise ValueError("Import must specify either 'files' or 'modules'")
        if self.files and self.modules:
            raise ValueError("Import cannot specify both 'files' and 'modules'")
        return self
