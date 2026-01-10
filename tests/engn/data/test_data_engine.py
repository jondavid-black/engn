from engn.data.models import TypeDef, Property, Enumeration, Schema
from engn.data.storage import JSONLStorage


def test_schema_model_creation():
    prop = Property(name="age", type="int", presence="required")
    typedef = TypeDef(name="Person", properties=[prop])
    enum = Enumeration(name="Status", values=["active", "inactive"])
    schema = Schema(types=[typedef], enums=[enum])

    assert schema.types[0].name == "Person"
    assert schema.types[0].properties[0].name == "age"
    assert schema.enums[0].name == "Status"
    assert "active" in schema.enums[0].values


def test_jsonl_storage_write_read(tmp_path):
    file_path = tmp_path / "test.jsonl"
    storage = JSONLStorage(file_path, TypeDef)

    prop = Property(name="name", type="str")
    item1 = TypeDef(name="Item1", properties=[prop])
    item2 = TypeDef(name="Item2", properties=[prop])

    storage.write([item1, item2])

    loaded_items = storage.read()
    assert len(loaded_items) == 2
    assert loaded_items[0].name == "Item1"
    assert loaded_items[1].name == "Item2"


def test_jsonl_storage_append(tmp_path):
    file_path = tmp_path / "append.jsonl"
    storage = JSONLStorage(file_path, TypeDef)

    prop = Property(name="name", type="str")
    item1 = TypeDef(name="Item1", properties=[prop])
    storage.write([item1])

    item2 = TypeDef(name="Item2", properties=[prop])
    storage.append(item2)

    loaded_items = storage.read()
    assert len(loaded_items) == 2
    assert loaded_items[1].name == "Item2"


def test_jsonl_storage_read_nonexistent_file(tmp_path):
    file_path = tmp_path / "nonexistent.jsonl"
    storage = JSONLStorage(file_path, TypeDef)

    items = storage.read()
    assert items == []
