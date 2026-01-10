from behave import given, when, then  # type: ignore
from engn.data.models import TypeDef, Property, Enumeration
from engn.data.storage import JSONLStorage, EngnDataModel
import json


@when('I save the definitions to "{filename}"')  # type: ignore
def step_save_definitions(context, filename):
    file_path = context.test_dir / filename
    # We might have multiple definitions stored in context
    definitions = []
    if hasattr(context, "defined_type"):
        definitions.append(context.defined_type)
    if hasattr(context, "defined_types"):
        definitions.extend(context.defined_types.values())

    storage = JSONLStorage(file_path, EngnDataModel)
    storage.write(definitions)


@then('reading "{filename}" should return the types "{type1}" and "{type2}"')  # type: ignore
def step_read_types_verification(context, filename, type1, type2):
    file_path = context.test_dir / filename
    storage = JSONLStorage(file_path, EngnDataModel)
    items = storage.read()
    names = {item.name for item in items if hasattr(item, "name")}
    assert type1 in names
    assert type2 in names


@given('I have a schema with "{type1}" and "{type2}" types defined')  # type: ignore
def step_define_schema(context, type1, type2):
    # Hardcoded schema for the test scenario
    user_def = TypeDef(
        name=type1,
        properties=[Property(name="id", type="int"), Property(name="name", type="str")],
    )
    post_def = TypeDef(
        name=type2,
        properties=[
            Property(name="id", type="int"),
            Property(name="user_id", type="ref[User.id]"),
            Property(name="content", type="str"),
        ],
    )
    context.schema_defs = [user_def, post_def]


@when('I save a "{type_name}" with id {id:d} and name "{name}" to "{filename}"')  # type: ignore
def step_save_user(context, type_name, id, name, filename):
    file_path = context.test_dir / filename

    # We construct the JSON manually to append to file
    # Or use storage with dynamic models.
    # To use storage, we need to initialize it with definitions.

    storage = JSONLStorage(file_path, context.schema_defs)

    # We need to construct the item. Since we are in dynamic mode, we need the generated class.
    # storage._adapter handles serialization, but storage.write expects T.
    # But we can cheat and use append/write with the raw dict if we could...
    # but write expects T.

    # However, we can write raw json strings to the file directly.
    # This simulates "saving" data.

    mode = "a" if file_path.exists() else "w"
    with open(file_path, mode) as f:
        item = {"engn_type": type_name, "id": id, "name": name}
        f.write(json.dumps(item) + "\n")


@when(
    'I save a "{type_name}" with id {id:d}, user_id {user_id:d}, and content "{content}" to "{filename}"'
)  # type: ignore
def step_save_post(context, type_name, id, user_id, content, filename):
    file_path = context.test_dir / filename
    mode = "a" if file_path.exists() else "w"
    with open(file_path, mode) as f:
        item = {
            "engn_type": type_name,
            "id": id,
            "user_id": user_id,
            "content": content,
        }
        f.write(json.dumps(item) + "\n")


@then('reading "{filename}" should succeed without errors')  # type: ignore
def step_read_succeeds(context, filename):
    file_path = context.test_dir / filename
    storage = JSONLStorage(file_path, context.schema_defs)
    try:
        items = storage.read()
        assert len(items) > 0
    except Exception as e:
        assert False, f"Read failed with error: {e}"


@then('reading "{filename}" should fail with a reference error')  # type: ignore
def step_read_fails(context, filename):
    file_path = context.test_dir / filename
    storage = JSONLStorage(file_path, context.schema_defs)
    try:
        storage.read()
        assert False, "Read should have failed"
    except ValueError as e:
        assert "Reference error" in str(e)


# We also need to update existing steps to handle "I define a data type..." accumulating types
# The existing step overwrites context.defined_type.
# I'll update the existing step to also store in a list/dict.

# Removed duplicate step definition
