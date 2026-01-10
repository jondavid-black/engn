from behave import given, when, then  # type: ignore
from engn.data.models import TypeDef, Property, Enumeration
from engn.data.storage import JSONLStorage


@given("a temporary directory for data storage")  # type: ignore
def step_temp_dir(context):
    # Context.test_dir is already set by environment.py, but we ensure it's ready
    assert context.test_dir.exists()


@when('I define a data type "{type_name}" with properties')  # type: ignore
def step_define_type(context, type_name):
    properties = []
    for row in context.table:
        properties.append(
            Property(
                name=row["name"],
                type=row["type"],
                presence=row["presence"],
            )
        )
    context.defined_type = TypeDef(name=type_name, properties=properties)
    if not hasattr(context, "defined_types"):
        context.defined_types = {}
    context.defined_types[type_name] = context.defined_type


@when('I save the "{type_name}" type definition to "{filename}"')  # type: ignore
def step_save_type(context, type_name, filename):
    file_path = context.test_dir / filename
    storage = JSONLStorage(file_path, TypeDef)
    storage.write([context.defined_type])


@then('the file "{filename}" should exist')  # type: ignore
def step_file_exists(context, filename):
    file_path = context.test_dir / filename
    assert file_path.exists()


@then('reading "{filename}" should return the type "{type_name}"')  # type: ignore
def step_read_type_verification(context, filename, type_name):
    file_path = context.test_dir / filename
    storage = JSONLStorage(file_path, TypeDef)
    items = storage.read()
    assert len(items) == 1
    assert items[0].name == type_name
    assert items[0].properties == context.defined_type.properties


@when('I define an enumeration "{enum_name}" with values "{values}"')  # type: ignore
def step_define_enum(context, enum_name, values):
    value_list = [v.strip() for v in values.split(",")]
    context.defined_enum = Enumeration(name=enum_name, values=value_list)


@when('I save the "{enum_name}" enum definition to "{filename}"')  # type: ignore
def step_save_enum(context, enum_name, filename):
    file_path = context.test_dir / filename
    storage = JSONLStorage(file_path, Enumeration)
    storage.write([context.defined_enum])


@then('reading "{filename}" should return the enum "{enum_name}"')  # type: ignore
def step_read_enum_verification(context, filename, enum_name):
    file_path = context.test_dir / filename
    storage = JSONLStorage(file_path, Enumeration)
    items = storage.read()
    assert len(items) == 1
    assert items[0].name == enum_name
    assert items[0].values == context.defined_enum.values
