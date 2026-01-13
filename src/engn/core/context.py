"""Application context management for engn.

This module provides a centralized way to maintain and observe the current state
of the application, such as the active project and branch.
"""

from typing import Any, Callable, Optional


class AppContext:
    """Maintains the current state of the application.

    This class uses an observer pattern to notify listeners when the context
    information changes.
    """

    def __init__(self):
        self._active_project_id: Optional[str] = None
        self._active_branch: Optional[str] = None
        self._listeners: list[Callable[["AppContext"], None]] = []

    @property
    def active_project_id(self) -> Optional[str]:
        """Get the ID of the currently active project."""
        return self._active_project_id

    @active_project_id.setter
    def active_project_id(self, value: Optional[str]):
        """Set the ID of the currently active project and notify listeners."""
        if self._active_project_id != value:
            self._active_project_id = value
            self._notify_listeners()

    @property
    def active_branch(self) -> Optional[str]:
        """Get the name of the currently active branch."""
        return self._active_branch

    @active_branch.setter
    def active_branch(self, value: Optional[str]):
        """Set the name of the currently active branch and notify listeners."""
        if self._active_branch != value:
            self._active_branch = value
            self._notify_listeners()

    def subscribe(self, listener: Callable[["AppContext"], None]) -> None:
        """Subscribe a listener to context changes.

        Args:
            listener: A callable that takes the AppContext as an argument.
        """
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[["AppContext"], None]) -> None:
        """Unsubscribe a listener from context changes.

        Args:
            listener: The listener to remove.
        """
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self) -> None:
        """Notify all subscribed listeners of a context change."""
        for listener in self._listeners:
            try:
                listener(self)
            except Exception:
                # In a real app, we might want to log this error
                # but we don't want one listener to crash the notification loop
                pass

    def update(
        self, project_id: Optional[str] = None, branch: Optional[str] = None
    ) -> None:
        """Update multiple context values at once.

        Only notifies listeners once if any values changed.
        """
        changed = False
        if project_id is not None and self._active_project_id != project_id:
            self._active_project_id = project_id
            changed = True
        if branch is not None and self._active_branch != branch:
            self._active_branch = branch
            changed = True

        if changed:
            self._notify_listeners()


def get_app_context(page: Any) -> AppContext:
    """Get or create the AppContext for the given page session.

    Args:
        page: The Flet page object.

    Returns:
        The AppContext instance associated with the page.
    """
    if not hasattr(page, "app_context"):
        # We use setattr to avoid type checking issues if page doesn't have the attribute
        setattr(page, "app_context", AppContext())
    return getattr(page, "app_context")
