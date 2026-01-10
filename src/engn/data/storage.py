from pathlib import Path
from typing import Generic, Type, TypeVar, List, Union, Annotated

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
        model_type: Type[T] | TypeAdapter[T] | List[Union[TypeDef, Enumeration]],
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

        if isinstance(model_type, list):
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
                raise ValueError(
                    "No valid Pydantic models could be generated from definitions."
                )

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
                json_bytes = self._adapter.dump_json(item)
                f.write(json_bytes.decode("utf-8") + "\n")

    def read(self) -> List[T]:
        """
        Read all items from the JSONL file.

        Returns:
            List of Pydantic model instances.
        """
        if not self.file_path.exists():
            return []

        items = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # validate_json parses the JSON string and validates it against the model
                item = self._adapter.validate_json(line)
                items.append(item)
        return items

    def append(self, item: T) -> None:
        """
        Append a single item to the JSONL file.

        Args:
            item: The Pydantic model instance to append.
        """
        self.write([item], mode="a")
