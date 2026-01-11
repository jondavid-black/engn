"""Terminal emulator component using ttyd for VT100 terminal support."""

import shutil
import subprocess
import sys
import time
from typing import Any, Callable

import flet as ft

try:
    import flet_webview as fwv

    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False


class TerminalEmulator(ft.Container):
    """A terminal emulator component that embeds ttyd via WebView.

    This component uses ttyd to serve a real terminal session as a web page,
    then embeds it using Flet's WebView. Provides full VT100/xterm support
    including colors, cursor movement, and mouse clicks.

    Platform Support:
        - Web: Full support via flet-webview
        - macOS: Full support via flet-webview
        - iOS/Android: Full support via flet-webview
        - Windows/Linux desktop: Not supported (WebView limitation)

    Requirements:
        - ttyd binary must be installed and available in PATH
        - flet-webview package must be installed

    Example:
        ```python
        terminal = TerminalEmulator(
            command=["python", "my_agent.py"],
            port=7681,
            on_connected=lambda: print("Terminal connected"),
            on_error=lambda msg: print(f"Error: {msg}"),
        )
        page.add(terminal)
        ```
    """

    DEFAULT_PORT = 7681
    STARTUP_DELAY = 1.0

    def __init__(
        self,
        command: list[str] | None = None,
        port: int = DEFAULT_PORT,
        writable: bool = True,
        on_connected: Callable[[], None] | None = None,
        on_disconnected: Callable[[], None] | None = None,
        on_error: Callable[[str], None] | None = None,
        startup_delay: float = STARTUP_DELAY,
        **kwargs: Any,
    ):
        """Initialize the terminal emulator.

        Args:
            command: Command to run in the terminal. Defaults to system shell.
            port: Port for ttyd to serve on. Defaults to 7681.
            writable: Allow terminal input. Defaults to True.
            on_connected: Callback when terminal connects successfully.
            on_disconnected: Callback when terminal disconnects.
            on_error: Callback when an error occurs.
            startup_delay: Seconds to wait for ttyd to start.
            **kwargs: Additional arguments passed to ft.Container.
        """
        # Initialize private attributes BEFORE super().__init__
        # to avoid conflicts with ft.Container properties
        self._ttyd_process: subprocess.Popen[bytes] | None = None
        self._is_running = False
        self._webview: Any = None
        self._terminal_port = port

        super().__init__(**kwargs)
        self.command = command or self._get_default_shell()
        self.writable = writable
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.on_error = on_error
        self.startup_delay = startup_delay

        # Check requirements and build content
        self.expand = kwargs.get("expand", True)
        self.content = self._build_content()

    def _get_default_shell(self) -> list[str]:
        """Get the default shell command for the current platform."""
        if sys.platform == "win32":
            return ["cmd.exe"]
        return ["/bin/bash"]

    def _check_ttyd_available(self) -> bool:
        """Check if ttyd is available in PATH."""
        return shutil.which("ttyd") is not None

    def _check_platform_supported(self) -> bool:
        """Check if current platform supports WebView."""
        # WebView is supported on Web, macOS, iOS, Android
        # Not supported on Windows/Linux desktop
        # We can't reliably detect runtime platform in Flet,
        # so we rely on WebView availability and let it fail gracefully
        return WEBVIEW_AVAILABLE

    def _build_content(self) -> ft.Control:
        """Build the terminal content based on platform support."""
        # Check for ttyd
        if not self._check_ttyd_available():
            return self._build_error_view(
                "ttyd not found",
                "The ttyd binary is required but not found in PATH.\n\n"
                "Install ttyd:\n"
                "  - macOS: brew install ttyd\n"
                "  - Ubuntu/Debian: apt install ttyd\n"
                "  - Arch: pacman -S ttyd\n"
                "  - Windows: Download from github.com/tsl0922/ttyd/releases",
            )

        # Check for WebView support
        if not self._check_platform_supported():
            return self._build_error_view(
                "WebView not available",
                "The flet-webview package is required.\n\n"
                "Install with: pip install flet-webview\n\n"
                "Note: WebView is only supported on:\n"
                "  - Web target\n"
                "  - macOS desktop\n"
                "  - iOS/Android mobile\n\n"
                "Windows and Linux desktop are not supported.",
            )

        # Build the WebView terminal
        return self._build_webview()

    def _build_error_view(self, title: str, message: str) -> ft.Container:
        """Build an error message view."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.ERROR),
                    ft.Text(
                        title,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ERROR,
                    ),
                    ft.Text(
                        message,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16,
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=8,
            padding=24,
        )

    def _build_webview(self) -> ft.Control:
        """Build the WebView component for the terminal."""
        # This method is only called when WEBVIEW_AVAILABLE is True
        assert WEBVIEW_AVAILABLE, "WebView module not available"
        self._webview = fwv.WebView(  # type: ignore[possibly-undefined]
            url=f"http://localhost:{self._terminal_port}",
            expand=True,
            on_page_started=self._handle_page_started,
            on_page_ended=self._handle_page_ended,
            on_web_resource_error=self._handle_web_error,
        )
        return self._webview

    def _handle_page_started(self, e: Any) -> None:
        """Handle WebView page started event."""
        pass  # Loading in progress

    def _handle_page_ended(self, e: Any) -> None:
        """Handle WebView page loaded event."""
        self._is_running = True
        if self.on_connected:
            self.on_connected()

    def _handle_web_error(self, e: Any) -> None:
        """Handle WebView error event."""
        error_msg = str(e.data) if hasattr(e, "data") else "Unknown error"
        if self.on_error:
            self.on_error(error_msg)

    def start(self) -> bool:
        """Start the ttyd process and terminal.

        Returns:
            True if started successfully, False otherwise.
        """
        if self._ttyd_process is not None:
            return True  # Already running

        if not self._check_ttyd_available():
            if self.on_error:
                self.on_error("ttyd not found in PATH")
            return False

        try:
            ttyd_args = ["ttyd", "--port", str(self._terminal_port)]
            if self.writable:
                ttyd_args.append("--writable")
            ttyd_args.extend(self.command)

            self._ttyd_process = subprocess.Popen(
                ttyd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for ttyd to start
            time.sleep(self.startup_delay)

            # Check if process is still running
            if self._ttyd_process.poll() is not None:
                stderr = self._ttyd_process.stderr
                error_output = stderr.read().decode() if stderr else "Unknown error"
                if self.on_error:
                    self.on_error(f"ttyd failed to start: {error_output}")
                self._ttyd_process = None
                return False

            return True

        except FileNotFoundError:
            if self.on_error:
                self.on_error("ttyd executable not found")
            return False
        except Exception as e:
            if self.on_error:
                self.on_error(f"Failed to start ttyd: {e}")
            return False

    def stop(self) -> None:
        """Stop the ttyd process."""
        if self._ttyd_process is not None:
            self._ttyd_process.terminate()
            try:
                self._ttyd_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._ttyd_process.kill()
            self._ttyd_process = None
            self._is_running = False
            if self.on_disconnected:
                self.on_disconnected()

    def restart(self) -> bool:
        """Restart the terminal.

        Returns:
            True if restarted successfully, False otherwise.
        """
        self.stop()
        return self.start()

    @property
    def is_running(self) -> bool:
        """Check if the terminal is currently running."""
        return self._is_running and self._ttyd_process is not None

    @property
    def port(self) -> int:
        """Get the ttyd port."""
        return self._terminal_port

    @property
    def terminal_url(self) -> str:
        """Get the ttyd URL."""
        return f"http://localhost:{self._terminal_port}"

    def did_mount(self) -> None:
        """Called when the control is added to the page."""
        super().did_mount()
        # Auto-start the terminal when mounted
        self.start()

    def will_unmount(self) -> None:
        """Called when the control is removed from the page."""
        super().will_unmount()
        # Clean up the ttyd process
        self.stop()

    def __del__(self) -> None:
        """Ensure ttyd process is cleaned up."""
        # Guard against incomplete initialization
        if hasattr(self, "_ttyd_process"):
            self.stop()
