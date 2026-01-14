from pathlib import Path
from typing import Generic, Type, TypeVar, List, Union, Annotated, Sequence

from pydantic import BaseModel, TypeAdapter, Field

from engn.data.models import TypeDef, Enumeration, Import, Module
from engn.data.dynamic import gen_pydantic_models

# Define the discriminated union of supported types
EngnDataModel = Annotated[
    Union[TypeDef, Enumeration, Import, Module], Field(discriminator="engn_type")
]

T = TypeVar("T", bound=BaseModel)


class JSONLStorage(Generic[T]):
    """
    Generic storage engine for reading and writing Pydantic models to JSONL files.
    """

    def __init__(
        self,
        file_path: Path,
        model_type: Type[T]
        | TypeAdapter[T]
        | Sequence[Union[TypeDef, Enumeration, Module]],
    ):
        """
        Initialize the storage engine.

        Args:
            file_path: Absolute path to the JSONL file.
            model_type: The Pydantic model class, TypeAdapter, or list of TypeDefs.
                        If a list of TypeDefs is provided, dynamic models are generated,
                        and a discriminated union adapter is created.
        """
        self.file_path = file_path
        self._is_dynamic = isinstance(model_type, list)
        self._initial_definitions = (
            list(model_type) if isinstance(model_type, list) else []
        )

        if isinstance(model_type, list):
            if not model_type:
                # Initialize with empty adapter, to be built in read()
                self._adapter = None
                return

            # Dynamic generation mode
            # 1. Generate models
            registry = gen_pydantic_models(model_type)
            # 2. Extract generated model classes (filtering out Enums if necessary,
            #    though Enums in union is tricky - usually we want the Model types)
            #    We assume the list contains TypeDefs which become Models.
            #    Enums are supported as fields but maybe not as top-level items unless wrapped.
            #    For now, let's include all generated BaseModel subclasses.
            models = [
                m
                for m in registry.values()
                if isinstance(m, type) and issubclass(m, BaseModel)
            ]

            if not models:
                # Fallback if no models generated? Or raise error?
                # If only Enums were passed, we might have an issue if we expect T=BaseModel
                # But let's assume at least one TypeDef.

                # If we passed CLASSES, `gen_pydantic_models` will fail or do nothing because it expects instances.
                # The test passed `model_type=[TypeDef, Enumeration]`.
                # We should update the test to pass an empty list if we want "start from scratch".

                # However, if we want to allow "start empty", we should handle `not models` more gracefully.
                self._adapter = None
                return

            # 3. Create a discriminated union
            #    The 'engn_type' field in each dynamic model acts as the discriminator.
            #    We also include the core meta-model types in the union to support mixed files.
            UnionType = Union[tuple(models + [TypeDef, Enumeration, Import, Module])]  # type: ignore
            self._adapter = TypeAdapter(
                Annotated[UnionType, Field(discriminator="engn_type")]
            )

        elif isinstance(model_type, TypeAdapter):
            self._adapter = model_type
        else:
            self._adapter = TypeAdapter(model_type)

    def write(self, items: List[T], mode: str = "w") -> None:
        """
        Write a list of items to the JSONL file.

        Args:
            items: List of Pydantic model instances to write.
            mode: File open mode ('w' for overwrite, 'a' for append).
        """
        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, mode, encoding="utf-8") as f:
            for item in items:
                # Use the adapter to serialize to JSON bytes, then decode to string
                if self._adapter:
                    json_bytes = self._adapter.dump_json(item)
                    f.write(json_bytes.decode("utf-8") + "\n")
                else:
                    # Fallback if no adapter (e.g. writing definitions manually?)
                    # Or simple model dump
                    f.write(item.model_dump_json() + "\n")

    def _rebuild_adapter(
        self, definitions: Sequence[Union[TypeDef, Enumeration, Module]]
    ) -> None:
        """
        Rebuilds the TypeAdapter with new definitions.
        """
        registry = gen_pydantic_models(list(definitions))
        models = [
            m
            for m in registry.values()
            if isinstance(m, type) and issubclass(m, BaseModel)
        ]

        if not models:
            # If we still can't build models (e.g. only enums), we might need to handle this.
            # But for now we assume definitions lead to models.
            self._adapter = None
            return

        # Include core types in the union
        UnionType = Union[tuple(models + [TypeDef, Enumeration, Import, Module])]  # type: ignore
        self._adapter = TypeAdapter(
            Annotated[UnionType, Field(discriminator="engn_type")]
        )

    def read(self) -> List[T]:
        """
        Read all items from the JSONL file.

        If dynamic mode is active, handles out-of-order definitions by:
        1. Reading all lines.
        2. Extracting definitions (TypeDef, Enumeration).
        3. Rebuilding the schema.
        4. Parsing remaining items.
        """
        if not self.file_path.exists():
            return []

        lines = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not self._is_dynamic:
            # Standard mode - single pass
            # We assume adapter is present in standard mode
            if self._adapter is None:
                return []

            items = []
            for line in lines:
                items.append(self._adapter.validate_json(line))
            return items

        # Dynamic mode with potential out-of-order definitions

        # 1. First pass: Collect all definitions and raw data
        definitions = list(self._initial_definitions)
        raw_items = []

        # We need to identify definitions.
        # We can use a temporary adapter for just the definition types.
        def_adapter = TypeAdapter(
            Annotated[
                Union[TypeDef, Enumeration, Module], Field(discriminator="engn_type")
            ]
        )

        for line in lines:
            try:
                # Try to parse as definition
                item = def_adapter.validate_json(line)
                definitions.append(item)
                # We also keep it as a raw item to return it?
                # Usually definitions are part of the stream but typically we want the DATA instances.
                # But if the file is mixed, the user might expect everything back?
                # The return type is List[T]. If T is Union[TypeDef, Enum, GeneratedModels], then yes.
                # If T is just GeneratedModels, then no.
                # Given EngnDataModel includes TypeDef and Enum, we probably want to return them too.
                raw_items.append((line, item))
            except Exception:
                # Not a definition (or invalid one), treat as data instance
                raw_items.append((line, None))

        # 2. Rebuild adapter with all found definitions
        if definitions:
            self._rebuild_adapter(definitions)

        if self._adapter is None:
            # If we still have no adapter, we can only return the definitions we found.
            # If there are unknown data items, we should fail validation.
            parsed_items = []
            for line, parsed_def in raw_items:
                if parsed_def:
                    parsed_items.append(parsed_def)
                else:
                    # Trigger validation error for unknown data items
                    def_adapter.validate_json(line)
            return parsed_items

        # 3. Second pass: Parse everything with the full adapter
        final_items = []
        for line, pre_parsed in raw_items:
            if pre_parsed:
                final_items.append(pre_parsed)
            else:
                # We expect all definitions to be loaded now.
                # If validation fails here, it is a genuine error (invalid data or missing definition).
                # We should propagate the error so the user knows the data is bad.
                item = self._adapter.validate_json(line)
                final_items.append(item)

        # 4. Third pass: Validate references
        self._validate_references(final_items)

        return final_items

    def _validate_references(self, items: List[T]) -> None:
        """
        Validate referential integrity of the loaded items.
        """
        if not items:
            return

        # 1. Identify which fields are references and build needed targets
        needed_targets = set()
        fields_with_refs = {}  # Map model name -> list of (field_name, target_ref)

        # Inspect all unique model types in the list
        # Note: items might contain TypeDefs/Enumerations too. We skip those or handle them?
        # References usually come from data models pointing to data models.
        # TypeDefs don't have references (except in type definition strings, which are validated elsewhere).

        # We need to look at the classes of the items.
        # Or better, we can iterate over the generated models if we have access to them.
        # But `items` contains instances.

        seen_classes = set()
        for item in items:
            cls = item.__class__
            if cls in seen_classes:
                continue
            seen_classes.add(cls)

            # Check if it has fields (Pydantic model)
            if not hasattr(cls, "model_fields"):
                continue

            for name, field_info in cls.model_fields.items():
                if field_info.json_schema_extra and isinstance(
                    field_info.json_schema_extra, dict
                ):
                    target = field_info.json_schema_extra.get("reference_target")
                    if target:
                        needed_targets.add(target)
                        fields_with_refs.setdefault(cls.__name__, []).append(
                            (name, target)
                        )

        if not needed_targets:
            return

        # 2. Build index of available values for needed targets
        # Structure: {"Type.Prop": {value1, value2, ...}}
        index = {t: set() for t in needed_targets}

        for item in items:
            model_name = item.__class__.__name__
            # Check if this item contributes to any target
            # Optimization: pre-calculate which fields of this model are needed
            # But iterating all needed_targets is okay if not too many.

            # Better: Map "Type" -> list of properties we need to index
            # But we have "Type.Prop" keys.

            # Let's iterate over needed_targets and check if this item matches the Type
            for target in needed_targets:
                target_type, target_prop = target.split(".")
                if model_name == target_type:
                    # This item is of the target type, index the property value
                    if hasattr(item, target_prop):
                        val = getattr(item, target_prop)
                        if val is not None:
                            index[target].add(val)

        # 3. Validate references
        for item in items:
            model_name = item.__class__.__name__
            if model_name in fields_with_refs:
                for field_name, target in fields_with_refs[model_name]:
                    val = getattr(item, field_name)
                    # If value is None/Optional and not set, skip?
                    # If field is required, Pydantic ensures it's not None (unless default).
                    # If field is Optional, it might be None.
                    if val is None:
                        continue

                    # Also skip if value is empty list (if we support list of refs)?
                    # Current implementation supports scalar ref.

                    if val not in index.get(target, set()):
                        raise ValueError(
                            f"Reference error in {model_name}.{field_name}: "
                            f"Value '{val}' not found in target '{target}'"
                        )

    def append(self, item: T) -> None:
        """
        Append a single item to the JSONL file.

        Args:
            item: The Pydantic model instance to append.
        """
        self.write([item], mode="a")
