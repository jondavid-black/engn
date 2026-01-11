"""Pytest configuration for UI tests."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest for UI tests."""
    config.addinivalue_line("markers", "ui: marks tests as UI tests")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Configure browser context for UI tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }
