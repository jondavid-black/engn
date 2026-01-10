from pathlib import Path
from typing import Generic, Type, TypeVar, List, Union, Annotated, Sequence

from pydantic import BaseModel, TypeAdapter, Field

from engn.data.models import TypeDef, Enumeration
from engn.data.dynamic import gen_pydantic_models

# Define the discriminated union of supported types
EngnDataModel = Annotated[Union[TypeDef, Enumeration], Field(discriminator="engn_type")]

T = TypeVar("T", bound=BaseModel)


class JSONLStorage(Generic[T]):
    """
    Generic storage engine for reading and writing Pydantic models to JSONL files.
    """

    def __init__(
        self,
        file_path: Path,
        model_type: Type[T] | TypeAdapter[T] | Sequence[Union[TypeDef, Enumeration]],
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
            UnionType = Union[tuple(models)]  # type: ignore
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

    def _rebuild_adapter(self, definitions: List[Union[TypeDef, Enumeration]]) -> None:
        """
        Rebuilds the TypeAdapter with new definitions.
        """
        registry = gen_pydantic_models(definitions)
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

        UnionType = Union[tuple(models)]  # type: ignore
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
            Annotated[Union[TypeDef, Enumeration], Field(discriminator="engn_type")]
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
            # If we still have no adapter, we can only return the definitions we found
            # (if T allows it) or raise error if we have data items we can't parse.
            # If T is bound to BaseModel, returning definitions (which are BaseModels) is fine.
            # But we can't parse the unknown data items.
            parsed_items = []
            for line, parsed_def in raw_items:
                if parsed_def:
                    parsed_items.append(parsed_def)
                else:
                    # Warn or fail?
                    # For now, let's skip unknown items if we can't build a model for them.
                    pass
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

        return final_items

    def append(self, item: T) -> None:
        """
        Append a single item to the JSONL file.

        Args:
            item: The Pydantic model instance to append.
        """
        self.write([item], mode="a")
