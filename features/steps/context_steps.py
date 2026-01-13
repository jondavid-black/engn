"""Step definitions for application context BDD tests."""

from unittest.mock import MagicMock
from behave import given, then, when
from engn.core.context import AppContext, get_app_context
import flet as ft


@given("a new application context is initialized")
def step_context_initialized(context):
    """Initialize a new AppContext."""
    context.app_context = AppContext()


@when('I set the active project to "{project_id}" in the context')
def step_set_active_project(context, project_id):
    """Set the active project in the context."""
    context.app_context.active_project_id = project_id


@then('the active project in the context should be "{project_id}"')
def step_check_active_project(context, project_id):
    """Check the active project in the context."""
    assert context.app_context.active_project_id == project_id


@given("a component is subscribed to context changes")
def step_subscribe_component(context):
    """Subscribe a mock component to context changes."""
    context.listener_notified = False

    def listener(ctx):
        context.listener_notified = True

    context.app_context.subscribe(listener)


@then("the component should be notified of the change")
def step_check_notification(context):
    """Check if the component was notified."""
    assert context.listener_notified, "Component was not notified of context change"


@when('I select project "{project_id}" in the toolbar dropdown')
def step_select_project_toolbar(context, project_id):
    """Simulate selecting a project in the toolbar dropdown."""
    # Find the project dropdown
    dropdown = context.toolbar.project_dropdown

    # Simulate selection
    e = MagicMock(spec=ft.ControlEvent)
    e.control = dropdown
    e.control.value = project_id

    # Trigger on_select
    if hasattr(dropdown, "on_select") and dropdown.on_select:
        dropdown.on_select(e)


@then('the application context active project should be "{project_id}"')
def step_check_app_context_project(context, project_id):
    """Check the active project in the application context."""
    # The toolbar uses get_app_context(page)
    app_ctx = get_app_context(context.mock_page)
    assert app_ctx.active_project_id == project_id
