from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field, create_model

from engn.data.models import Enumeration, TypeDef
from engn.data.primitives import PRIMITIVE_TYPE_MAP


class DynamicTypeRegistry:
    def __init__(self):
        self._types: Dict[str, Any] = {}

    def register(self, name: str, model: Any):
        self._types[name] = model

    def get(self, name: str) -> Optional[Any]:
        return self._types.get(name)


def _resolve_type(
    type_name: str, registry: DynamicTypeRegistry, primitive_map: Dict[str, Any]
) -> Any:
    """
    Resolves a string type definition to a Python/Pydantic type.
    Returns None if the type cannot be resolved yet (missing dependency).
    """
    # Handle list[T]
    if type_name.startswith("list[") and type_name.endswith("]"):
        inner = type_name[5:-1]
        inner_type = _resolve_type(inner, registry, primitive_map)
        if inner_type is None:
            return None
        return List[inner_type]  # type: ignore

    # Handle map[K, V]
    if type_name.startswith("map[") and type_name.endswith("]"):
        inner = type_name[4:-1]
        # Split by comma, ensuring we don't split nested brackets if possible
        # Simple split for now, assuming primitive keys
        parts = inner.split(",", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid map definition: {type_name}")

        key_type_str = parts[0].strip()
        val_type_str = parts[1].strip()

        key_type = _resolve_type(key_type_str, registry, primitive_map)
        val_type = _resolve_type(val_type_str, registry, primitive_map)

        if key_type is None or val_type is None:
            return None

        return Dict[key_type, val_type]  # type: ignore

    # Handle ref[T] - treat as just T
    if type_name.startswith("ref[") and type_name.endswith("]"):
        target = type_name[4:-1]
        return _resolve_type(target, registry, primitive_map)

    # Check primitives
    if type_name in primitive_map:
        return primitive_map[type_name]

    # Check registry (for already defined types or enums)
    registered = registry.get(type_name)
    if registered:
        return registered

    # Type not found
    return None


def gen_pydantic_models(
    definitions: List[Union[TypeDef, Enumeration]],
) -> Dict[str, Type[BaseModel]]:
    """
    Dynamically generate Pydantic model classes from a list of TypeDef and Enumeration instances.
    """
    registry = DynamicTypeRegistry()

    # Separate Enums and TypeDefs
    enums = [d for d in definitions if isinstance(d, Enumeration)]
    type_defs = [d for d in definitions if isinstance(d, TypeDef)]

    # First pass: Register Enums
    for enum_def in enums:
        # Create a dynamic Enum
        # We use standard Enum, but we could make it a str Enum for easier serialization
        enum_dict = {v: v for v in enum_def.values}
        enum_cls = Enum(enum_def.name, enum_dict, type=str)
        registry.register(enum_def.name, enum_cls)

    # Second pass: TypeDefs with dependency resolution
    pending = list(type_defs)

    # We loop until all types are resolved or we make no progress (circular/missing dep)
    while pending:
        progress = False
        retry_queue = []

        for type_def in pending:
            field_definitions = {}
            ready = True

            for prop in type_def.properties:
                py_type = _resolve_type(prop.type, registry, PRIMITIVE_TYPE_MAP)

                if py_type is None:
                    # Dependency missing, defer this type
                    ready = False
                    break

                # Handle optional/required and defaults
                field_args = {}

                if prop.description:
                    field_args["description"] = prop.description

                if prop.default is not None:
                    field_args["default"] = prop.default
                elif prop.presence == "optional":
                    field_args["default"] = None
                    py_type = Optional[py_type]
                else:
                    # Required field with no default
                    field_args["default"] = ...

                # Handle list constraints
                if prop.list_min is not None:
                    field_args["min_length"] = prop.list_min
                if prop.list_max is not None:
                    field_args["max_length"] = prop.list_max

                # numeric constraints
                if prop.gt is not None:
                    field_args["gt"] = prop.gt
                if prop.ge is not None:
                    field_args["ge"] = prop.ge
                if prop.lt is not None:
                    field_args["lt"] = prop.lt
                if prop.le is not None:
                    field_args["le"] = prop.le
                if prop.multiple_of is not None:
                    field_args["multiple_of"] = prop.multiple_of

                # extended numeric constraints
                # Note: 'exclude' and 'whole_number' require custom validators or field validators
                # which are harder to attach to dynamically created Pydantic models via simple Field arguments.
                # However, we can use 'Annotated' with 'AfterValidator' or custom field validators if we refactor.
                # For now, let's inject simple check logic if we can, or acknowledge the limitation.

                # We will handle 'exclude' and 'whole_number' by wrapping the type in Annotated with a validator
                if prop.exclude is not None or prop.whole_number:
                    from typing import Annotated
                    from pydantic import AfterValidator

                    validators = []

                    if prop.exclude:
                        excluded_values = set(prop.exclude)

                        def check_exclude(v):
                            if v in excluded_values:
                                raise ValueError("Value is excluded")
                            return v

                        validators.append(AfterValidator(check_exclude))

                    if prop.whole_number:

                        def check_whole(v):
                            if v % 1 != 0:
                                raise ValueError("Value must be a whole number")
                            return v

                        validators.append(AfterValidator(check_whole))

                    for v in validators:
                        py_type = Annotated[py_type, v]

                # string constraints
                if prop.str_min is not None:
                    field_args["min_length"] = prop.str_min
                if prop.str_max is not None:
                    field_args["max_length"] = prop.str_max
                if prop.str_regex is not None:
                    field_args["pattern"] = prop.str_regex

                # date/time constraints
                if prop.before is not None or prop.after is not None:
                    from typing import Annotated
                    from pydantic import AfterValidator
                    import datetime

                    dt_validators = []

                    if prop.before is not None:
                        # Capture prop.before in closure
                        limit_before = prop.before

                        def check_before(v):
                            if v >= limit_before:
                                raise ValueError(f"Value must be before {limit_before}")
                            return v

                        dt_validators.append(AfterValidator(check_before))

                    if prop.after is not None:
                        limit_after = prop.after

                        def check_after(v):
                            if v <= limit_after:
                                raise ValueError(f"Value must be after {limit_after}")
                            return v

                        dt_validators.append(AfterValidator(check_after))

                    for v in dt_validators:
                        py_type = Annotated[py_type, v]

                # path constraints
                if any(
                    x is not None
                    for x in [
                        prop.path_exists,
                        prop.is_dir,
                        prop.is_file,
                        prop.file_ext,
                    ]
                ):
                    from typing import Annotated
                    from pydantic import AfterValidator
                    import pathlib

                    path_validators = []

                    if prop.path_exists:

                        def check_exists(v):
                            p = pathlib.Path(str(v))
                            if not p.exists():
                                raise ValueError(f"Path '{p}' does not exist")
                            return v

                        path_validators.append(AfterValidator(check_exists))

                    if prop.is_dir:

                        def check_is_dir(v):
                            p = pathlib.Path(str(v))
                            if p.exists() and not p.is_dir():
                                raise ValueError(f"Path '{p}' is not a directory")
                            return v

                        path_validators.append(AfterValidator(check_is_dir))

                    if prop.is_file:

                        def check_is_file(v):
                            p = pathlib.Path(str(v))
                            if p.exists() and not p.is_file():
                                raise ValueError(f"Path '{p}' is not a file")
                            return v

                        path_validators.append(AfterValidator(check_is_file))

                    if prop.file_ext is not None:
                        allowed_exts = set(prop.file_ext)

                        def check_ext(v):
                            p = pathlib.Path(str(v))
                            # suffixes returns list, suffix returns last. Usually we check suffix.
                            # But if user provides .tar.gz, suffix is .gz.
                            # Let's check pure suffix for now.
                            if p.suffix not in allowed_exts:
                                raise ValueError(
                                    f"File extension '{p.suffix}' not allowed. Must be one of {allowed_exts}"
                                )
                            return v

                        path_validators.append(AfterValidator(check_ext))

                    for v in path_validators:
                        py_type = Annotated[py_type, v]

                # url constraints
                if any(x is not None for x in [prop.url_base, prop.url_protocols]):
                    from typing import Annotated
                    from pydantic import AfterValidator

                    url_validators = []

                    if prop.url_protocols is not None:
                        allowed_protocols = set(prop.url_protocols)

                        def check_protocol(v):
                            s = str(v)
                            if "://" not in s:
                                raise ValueError(
                                    "Invalid URL format (missing protocol)"
                                )
                            proto = s.split("://")[0]
                            if proto not in allowed_protocols:
                                raise ValueError(
                                    f"Protocol '{proto}' not allowed. Must be one of {allowed_protocols}"
                                )
                            return v

                        url_validators.append(AfterValidator(check_protocol))

                    if prop.url_base is not None:
                        base = prop.url_base

                        def check_base(v):
                            s = str(v)
                            if not s.startswith(base):
                                raise ValueError(f"URL must start with '{base}'")
                            return v

                        url_validators.append(AfterValidator(check_base))

                    for v in url_validators:
                        py_type = Annotated[py_type, v]

                # Other custom validation logic will be handled below if needed,
                # but Pydantic's Field handles most standard constraints.

                field_definitions[prop.name] = (py_type, Field(**field_args))

            if ready:
                # Add the engn_type discriminator field
                # It acts as a constant identifier for this type
                # We use Literal so Pydantic can use it for discriminated unions
                from typing import Literal

                field_definitions["engn_type"] = (
                    Literal[type_def.name],  # type: ignore
                    Field(default=type_def.name, frozen=True),
                )

                model = create_model(
                    type_def.name,
                    **field_definitions,  # type: ignore
                    __doc__=type_def.description,
                    __base__=BaseModel,
                )

                model = create_model(
                    type_def.name,
                    **field_definitions,  # type: ignore
                    __doc__=type_def.description,
                    __base__=BaseModel,
                )

                # Set extra config
                model.model_config["extra"] = "forbid"

                registry.register(type_def.name, model)
                progress = True
            else:
                retry_queue.append(type_def)

        if not progress and retry_queue:
            missing_names = [t.name for t in retry_queue]
            raise ValueError(
                f"Unable to resolve dependencies for types: {missing_names}. "
                "Possible circular dependency or missing type definition."
            )

        pending = retry_queue

    return registry._types
