from behave import when, then  # type: ignore
from engn.data.models import TypeDef, Property


@when(
    'I define a child data type "{type_name}" extending "{parent_name}" with properties'
)  # type: ignore
def step_define_type_extending(context, type_name, parent_name):
    properties = []
    for row in context.table:
        properties.append(
            Property(
                name=row["name"],
                type=row["type"],
                presence=row["presence"],
            )
        )

    # Store in the same dictionary as other types
    if not hasattr(context, "defined_types"):
        context.defined_types = {}

    # Create the type def with extends
    new_type = TypeDef(name=type_name, properties=properties, extends=parent_name)
    context.defined_types[type_name] = new_type
    context.defined_type = new_type  # Set as current for other steps


@then('the "{type_name}" type should extend "{parent_name}"')  # type: ignore
def step_verify_extends(context, type_name, parent_name):
    type_def = context.defined_types.get(type_name)
    assert type_def is not None, f"Type {type_name} not found"
    assert type_def.extends == parent_name, (
        f"Expected {type_name} to extend {parent_name}, but got {type_def.extends}"
    )


@then('the "{type_name}" type should have property "{prop_name}"')  # type: ignore
def step_verify_property(context, type_name, prop_name):
    type_def = context.defined_types.get(type_name)
    assert type_def is not None, f"Type {type_name} not found"

    prop_names = [p.name for p in type_def.properties]
    assert prop_name in prop_names, (
        f"Property {prop_name} not found in {type_name}. Available: {prop_names}"
    )
