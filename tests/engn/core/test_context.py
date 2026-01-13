"""Unit tests for the application context module."""

from unittest.mock import MagicMock
from engn.core.context import AppContext, get_app_context


def test_app_context_initialization():
    """Test that AppContext initializes with default values."""
    context = AppContext()
    assert context.active_project_id is None
    assert context.active_branch is None


def test_app_context_set_project():
    """Test setting the active project ID."""
    context = AppContext()
    listener = MagicMock()
    context.subscribe(listener)

    context.active_project_id = "test-project"
    assert context.active_project_id == "test-project"
    listener.assert_called_once_with(context)


def test_app_context_set_branch():
    """Test setting the active branch."""
    context = AppContext()
    listener = MagicMock()
    context.subscribe(listener)

    context.active_branch = "main"
    assert context.active_branch == "main"
    listener.assert_called_once_with(context)


def test_app_context_update():
    """Test updating multiple values at once."""
    context = AppContext()
    listener = MagicMock()
    context.subscribe(listener)

    context.update(project_id="p1", branch="b1")
    assert context.active_project_id == "p1"
    assert context.active_branch == "b1"
    # Should only notify once
    listener.assert_called_once_with(context)


def test_app_context_no_notify_on_same_value():
    """Test that listeners are not notified if the value hasn't changed."""
    context = AppContext()
    context.active_project_id = "p1"

    listener = MagicMock()
    context.subscribe(listener)

    context.active_project_id = "p1"
    listener.assert_not_called()


def test_app_context_unsubscribe():
    """Test unsubscribing a listener."""
    context = AppContext()
    listener = MagicMock()
    context.subscribe(listener)
    context.unsubscribe(listener)

    context.active_project_id = "p1"
    listener.assert_not_called()


def test_get_app_context():
    """Test the get_app_context helper function."""

    class MockPage:
        pass

    page = MockPage()
    # Initial call should create a new context
    context1 = get_app_context(page)
    assert isinstance(context1, AppContext)
    assert getattr(page, "app_context") == context1

    # Subsequent call should return the same context
    context2 = get_app_context(page)
    assert context1 is context2
