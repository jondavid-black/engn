import pytest
import tempfile
from pathlib import Path
from engn.data.storage import JSONLStorage
from engn.data.models import TypeDef, Property, Enumeration


def test_storage_ref_validation_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "data.jsonl"

        # Define schema
        schema_defs = [
            TypeDef(
                name="User",
                properties=[
                    Property(name="id", type="int"),
                    Property(name="name", type="str"),
                ],
            ),
            TypeDef(
                name="Post",
                properties=[
                    Property(name="id", type="int"),
                    Property(name="user_id", type="ref[User.id]"),
                    Property(name="content", type="str"),
                ],
            ),
        ]

        # Initialize storage with dynamic mode
        storage = JSONLStorage(file_path, schema_defs)

        # Create valid data (definitions will be handled by storage if we write them,
        # but here we initialize with definitions so we just write data)
        # Note: In dynamic mode, we need to use the generated classes to create items,
        # OR we can write dicts/json manually if we want.
        # But `storage.write` expects items of type T.
        # Since T is Union[GeneratedModels...], we need the classes.

        # Let's get the generated classes from the adapter
        # The adapter is built in __init__
        # But we can't easily access the classes from outside because they are in a local scope inside gen_pydantic_models.
        # However, storage._adapter exists.

        # Actually, for testing `read`, we can write the file manually with JSON.

        with open(file_path, "w") as f:
            # Write definitions (optional if we passed them to init, but read() logic
            # for dynamic mode relies on rebuilding adapter from file content if mixed)
            # But wait, `read` logic:
            # 1. First pass loads definitions from file AND uses self._initial_definitions.
            # So we don't strictly need to write definitions to file if we passed them to init.

            # Write User
            f.write('{"engn_type": "User", "id": 1, "name": "Alice"}\n')
            # Write Post referring to User 1
            f.write(
                '{"engn_type": "Post", "id": 101, "user_id": 1, "content": "Hello"}\n'
            )

        items = storage.read()
        assert len(items) == 2


def test_storage_ref_validation_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "data.jsonl"

        schema_defs = [
            TypeDef(
                name="User",
                properties=[
                    Property(name="id", type="int"),
                    Property(name="name", type="str"),
                ],
            ),
            TypeDef(
                name="Post",
                properties=[
                    Property(name="id", type="int"),
                    Property(name="user_id", type="ref[User.id]"),
                    Property(name="content", type="str"),
                ],
            ),
        ]

        storage = JSONLStorage(file_path, schema_defs)

        with open(file_path, "w") as f:
            f.write('{"engn_type": "User", "id": 1, "name": "Alice"}\n')
            # Write Post referring to non-existent User 999
            f.write(
                '{"engn_type": "Post", "id": 101, "user_id": 999, "content": "Hello"}\n'
            )

        # Should raise ValueError due to missing reference
        with pytest.raises(ValueError, match="Reference error"):
            storage.read()


def test_storage_ref_validation_ordering():
    """Test that validation works even if referred item comes later in file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "data.jsonl"

        schema_defs = [
            TypeDef(name="User", properties=[Property(name="id", type="int")]),
            TypeDef(
                name="Post", properties=[Property(name="user_id", type="ref[User.id]")]
            ),
        ]

        storage = JSONLStorage(file_path, schema_defs)

        with open(file_path, "w") as f:
            # Post comes BEFORE User
            f.write('{"engn_type": "Post", "user_id": 1}\n')
            f.write('{"engn_type": "User", "id": 1}\n')

        items = storage.read()
        assert len(items) == 2
