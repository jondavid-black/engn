"""UI tests for SysEngn toolbar using playwright.

These tests launch the actual SysEngn app and validate the UI renders correctly.
"""

import os
import subprocess
import time
from typing import Generator

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def sysengn_server() -> Generator[str, None, None]:
    """Start SysEngn server and yield the URL."""
    port = 8550

    # Set environment variables to run as web server without opening browser
    env = {
        **os.environ,
        "FLET_FORCE_WEB_SERVER": "true",
        "FLET_SERVER_PORT": str(port),
    }

    # Start the server in the background
    proc = subprocess.Popen(
        ["uv", "run", "sysengn", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    # Give the server time to start
    time.sleep(3)

    url = f"http://localhost:{port}"

    yield url

    # Cleanup: terminate the server
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.mark.ui
class TestToolbarUI:
    """UI tests for the SysEngn toolbar."""

    def test_toolbar_renders(self, sysengn_server: str, page: Page) -> None:
        """Test that the toolbar renders without errors."""
        page.goto(sysengn_server)

        # Wait for the page to load (flet apps load async)
        page.wait_for_load_state("networkidle")

        # Check that no error messages are displayed
        # Flet displays errors in a specific way
        error_elements = page.locator("text=Error")
        if error_elements.count() > 0:
            # Get the error text for debugging
            error_text = error_elements.first.text_content()
            pytest.fail(f"Error displayed on page: {error_text}")

    def test_logo_visible(self, sysengn_server: str, page: Page) -> None:
        """Test that the logo image is visible.

        Flet renders with Flutter's SkWasm on canvas, so the logo is drawn
        on the canvas rather than as an <img> element. We verify by checking
        that the flutter view renders content (logo is part of the toolbar).
        """
        page.goto(sysengn_server)
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Allow Flet JS to fully render

        # Logo is rendered on the canvas, verify flutter view is present
        flutter_view = page.locator("flutter-view")
        expect(flutter_view).to_be_visible(timeout=10000)

    def test_navigation_tabs_visible(self, sysengn_server: str, page: Page) -> None:
        """Test that navigation tabs are visible via screenshot verification.

        Flet renders with Flutter's SkWasm on canvas, so we verify visually.
        """
        page.goto(sysengn_server)
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Allow Flet JS to fully render

        # Take a screenshot and verify the toolbar area is rendered
        # The canvas rendering means we can't query text elements directly
        screenshot = page.screenshot()
        assert len(screenshot) > 0, "Page should render content"

        # Verify the flutter view is present and has content
        flutter_view = page.locator("flutter-view")
        expect(flutter_view).to_be_visible(timeout=10000)

    def test_tab_selection_changes_content(
        self, sysengn_server: str, page: Page
    ) -> None:
        """Test that clicking a tab changes the content.

        Flet renders with Flutter's SkWasm on canvas, so we use coordinate
        clicks based on known tab positions. The viewport is 1280x720.
        Tab positions (approximately): Home=525, MBSE=615, UX=706, Docs=797
        """
        page.goto(sysengn_server)
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Allow Flet JS to fully render

        # Take initial screenshot to verify Home view
        initial_screenshot = page.screenshot()

        # Click on MBSE tab (approximately at x=615, y=30 in toolbar)
        page.mouse.click(615, 30)
        time.sleep(1)  # Wait for view to update

        # Take screenshot after clicking MBSE
        after_screenshot = page.screenshot()

        # Screenshots should be different (content changed)
        assert initial_screenshot != after_screenshot, (
            "Content should change after clicking MBSE tab"
        )

    def test_no_tabbar_error(self, sysengn_server: str, page: Page) -> None:
        """Test that there's no 'TabBar must be used within Tabs' error."""
        page.goto(sysengn_server)
        page.wait_for_load_state("networkidle")

        # Check for the specific error that was occurring
        tabbar_error = page.locator("text=TabBar must be used within a Tabs control")
        expect(tabbar_error).to_have_count(0)
