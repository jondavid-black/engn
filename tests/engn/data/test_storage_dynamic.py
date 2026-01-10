import json
from pathlib import Path
from typing import List

import pytest
from pydantic import ValidationError

from engn.data.models import TypeDef, Property, Enumeration
from engn.data.storage import JSONLStorage


def test_storage_dynamic_types(tmp_path: Path):
    """Test JSONLStorage with dynamically generated types."""

    # Define schema
    schema = [
        Enumeration(name="Status", values=["active", "inactive"]),
        TypeDef(
            name="Product",
            properties=[
                Property(name="id", type="int", presence="required"),
                Property(name="name", type="str", presence="required"),
                Property(name="status", type="Status", presence="required"),
            ],
        ),
    ]

    file_path = tmp_path / "products.jsonl"
    storage = JSONLStorage(file_path, model_type=schema)

    # Create items using the generated model via the adapter?
    # The storage exposes ._adapter, but usually we just pass dicts or objects.
    # But wait, storage.write expects items of type T.
    # With dynamic types, T is effectively Union[Product, Status, ...]

    # We can write dictionaries if validation passes?
    # No, JSONLStorage.write expects instances of T, and it calls adapter.dump_json(item).
    # If we pass a dict, Pydantic might validate it if we used validate_python,
    # but dump_json expects the model instance usually.

    # However, since we don't have easy access to the class `Product` here (it's internal to storage),
    # we might need to rely on the fact that TypeAdapter can handle dicts if configured?
    # Or we can just use the fact that we can't easily import the dynamic class here.

    # Actually, we can't easily instantiate the dynamic class outside.
    # But wait! The `gen_pydantic_models` returns a registry.
    # We used it inside `__init__` but didn't expose it.

    # This reveals a usage pattern issue:
    # If I use `JSONLStorage(..., model_type=list_of_defs)`, I get a storage engine capable of reading/writing.
    # But how do I CREATE the objects to write?

    # Option 1: The user must generate the models THEMSELVES first, then pass them to storage?
    #   - `registry = gen_models(defs)`
    #   - `storage = JSONLStorage(..., model_type=TypeAdapter(Union[registry.values()]))`
    #   This seems cleaner and avoids the magic inside storage.

    # Option 2: Storage exposes the generated models?

    # The requirement said: "When you read in a type definition from a JSONL line, dynamically generate a Pydantic type... This should allow you to load data items of a defined type into objects"

    # So `read()` returns objects.
    # `write()` takes objects.

    # Let's verify `read` works by manually creating a file.

    data = [
        {"engn_type": "Product", "id": 1, "name": "Widget", "status": "active"},
        {"engn_type": "Product", "id": 2, "name": "Gadget", "status": "inactive"},
    ]

    with open(file_path, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    # Test Read
    items = storage.read()
    assert len(items) == 2
    assert items[0].name == "Widget"  # type: ignore
    assert items[0].status == "active"  # type: ignore
    assert items[0].__class__.__name__ == "Product"

    # Test Write (append)
    # We can append one of the read items
    new_item = items[0]
    storage.append(new_item)

    items_again = storage.read()
    assert len(items_again) == 3


def test_storage_dynamic_validation_error(tmp_path: Path):
    """Test that invalid data raises validation error."""
    schema = [
        TypeDef(
            name="Simple",
            properties=[Property(name="val", type="int", presence="required")],
        )
    ]
    file_path = tmp_path / "simple.jsonl"
    storage = JSONLStorage(file_path, model_type=schema)

    with open(file_path, "w") as f:
        f.write(json.dumps({"engn_type": "Simple", "val": "not-an-int"}) + "\n")

    with pytest.raises(ValidationError):
        storage.read()
