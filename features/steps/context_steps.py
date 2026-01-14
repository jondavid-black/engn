"""Step definitions for application context BDD tests."""

from typing import Any, cast
from unittest.mock import MagicMock
from behave import given, then, when
from engn.core.context import AppContext


@given("a new application context is initialized")  # type: ignore
def step_context_initialized(context):
    """Initialize a new AppContext."""
    context.app_context = AppContext()


@when('I set the active project to "{project_id}" in the context')  # type: ignore
def step_set_active_project(context, project_id):
    """Set the active project in the context."""
    context.app_context.active_project_id = project_id


@then('the active project in the context should be "{project_id}"')  # type: ignore
def step_check_active_project(context, project_id):
    """Check the active project in the context."""
    assert context.app_context.active_project_id == project_id


@given("a component is subscribed to context changes")  # type: ignore
def step_subscribe_component(context):
    """Subscribe a mock component to context changes."""
    context.listener_notified = False

    def listener(ctx):
        context.listener_notified = True

    context.app_context.subscribe(listener)


@then("the component should be notified of the change")  # type: ignore
def step_check_notification(context):
    """Check if the component was notified."""
    assert context.listener_notified, "Component was not notified of context change"
