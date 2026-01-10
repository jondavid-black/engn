from pydantic import TypeAdapter
from typing import Union, Dict, Any
from engn.data.models import TypeDef, Property, Enumeration, Schema
from engn.data.storage import JSONLStorage, EngnDataModel


def test_schema_model_creation():
    prop = Property(name="age", type="int", presence="required")
    typedef = TypeDef(name="Person", properties=[prop])
    enum = Enumeration(name="Status", values=["active", "inactive"])
    schema = Schema(types=[typedef], enums=[enum])

    assert schema.types[0].name == "Person"
    assert schema.types[0].engn_type == "type_def"
    assert schema.types[0].properties[0].name == "age"
    assert schema.enums[0].name == "Status"
    assert schema.enums[0].engn_type == "enum"
    assert "active" in schema.enums[0].values


def test_polymorphic_storage_write_read(tmp_path):
    file_path = tmp_path / "polymorphic.jsonl"
    adapter = TypeAdapter(EngnDataModel)
    storage = JSONLStorage(file_path, adapter)

    prop = Property(name="role", type="Status")
    typedef = TypeDef(name="User", properties=[prop])
    enum = Enumeration(name="Status", values=["admin", "guest"])

    # Write mixed types
    storage.write([typedef, enum])

    loaded_items = storage.read()
    assert len(loaded_items) == 2

    # Check types using isinstance
    assert isinstance(loaded_items[0], TypeDef)
    assert loaded_items[0].name == "User"

    assert isinstance(loaded_items[1], Enumeration)
    assert loaded_items[1].name == "Status"
    assert "admin" in loaded_items[1].values


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


def test_nested_person_address_jsonl(tmp_path):
    # 1. Define Address Type
    addr_props = [
        Property(name="street", type="str"),
        Property(name="city", type="str"),
        Property(name="state", type="str"),
        Property(name="zip_code", type="str"),
    ]
    address_def = TypeDef(name="Address", properties=addr_props)

    # 2. Define Person Type with nested Address
    person_props = [
        Property(name="name", type="str"),
        Property(name="email", type="str"),
        Property(name="address", type="Address"),  # References the Address type
    ]
    person_def = TypeDef(name="Person", properties=person_props)

    # 3. Create a data instance (as a dict for now, since dynamic model generation isn't strictly enforced yet)
    person_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62704",
        },
    }

    # 4. Write to JSONL
    # We need an adapter that can handle both TypeDef/Enum (EngnDataModel) AND generic data (dict)
    # In a real scenario, we might want a stricter wrapper for data instances, but for this test:
    adapter = TypeAdapter(Union[EngnDataModel, Dict[str, Any]])

    file_path = tmp_path / "nested_data.jsonl"
    storage = JSONLStorage(file_path, adapter)

    storage.write([address_def, person_def, person_data])

    # 5. Read back
    loaded_items = storage.read()

    assert len(loaded_items) == 3

    # Verify Address Definition
    loaded_addr_def = loaded_items[0]
    assert isinstance(loaded_addr_def, TypeDef)
    assert loaded_addr_def.name == "Address"
    assert len(loaded_addr_def.properties) == 4

    # Verify Person Definition
    loaded_person_def = loaded_items[1]
    assert isinstance(loaded_person_def, TypeDef)
    assert loaded_person_def.name == "Person"
    assert loaded_person_def.properties[2].name == "address"
    assert loaded_person_def.properties[2].type == "Address"

    # Verify Person Data
    loaded_data = loaded_items[2]
    assert isinstance(loaded_data, dict)
    assert loaded_data["name"] == "Jane Doe"
    assert loaded_data["email"] == "jane@example.com"

    # Verify nested address data
    assert isinstance(loaded_data["address"], dict)
    assert loaded_data["address"]["street"] == "123 Main St"
    assert loaded_data["address"]["zip_code"] == "62704"
