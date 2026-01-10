from pathlib import Path
from typing import Generic, Type, TypeVar, List, Union, Annotated

from pydantic import BaseModel, TypeAdapter, Field

from engn.data.models import TypeDef, Enumeration

# Define the discriminated union of supported types
EngnDataModel = Annotated[Union[TypeDef, Enumeration], Field(discriminator="engn_type")]

T = TypeVar("T", bound=BaseModel)


class JSONLStorage(Generic[T]):
    """
    Generic storage engine for reading and writing Pydantic models to JSONL files.
    """

    def __init__(self, file_path: Path, model_type: Type[T] | TypeAdapter[T]):
        """
        Initialize the storage engine.

        Args:
            file_path: Absolute path to the JSONL file.
            model_type: The Pydantic model class or TypeAdapter to use.
                        If creating for polymorphic types, pass TypeAdapter(EngnDataModel).
        """
        self.file_path = file_path
        if isinstance(model_type, TypeAdapter):
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
