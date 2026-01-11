"""Unit tests for TerminalEmulator component."""

import sys
from unittest.mock import MagicMock, patch


from engn.ui.terminal_emulator import TerminalEmulator


class TestTerminalEmulatorInit:
    """Tests for TerminalEmulator initialization."""

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_default_initialization(self, mock_which: MagicMock) -> None:
        """Test component initializes with default values."""
        mock_which.return_value = "/usr/bin/ttyd"
        terminal = TerminalEmulator()

        assert terminal.port == TerminalEmulator.DEFAULT_PORT
        assert terminal.writable is True
        assert terminal.is_running is False
        assert (
            terminal.terminal_url == f"http://localhost:{TerminalEmulator.DEFAULT_PORT}"
        )

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_custom_initialization(self, mock_which: MagicMock) -> None:
        """Test component initializes with custom values."""
        mock_which.return_value = "/usr/bin/ttyd"
        terminal = TerminalEmulator(
            command=["python", "script.py"],
            port=9000,
            writable=False,
        )

        assert terminal.command == ["python", "script.py"]
        assert terminal.port == 9000
        assert terminal.writable is False
        assert terminal.terminal_url == "http://localhost:9000"

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_default_shell_linux(self, mock_which: MagicMock) -> None:
        """Test default shell on Linux."""
        mock_which.return_value = "/usr/bin/ttyd"
        with patch.object(sys, "platform", "linux"):
            terminal = TerminalEmulator()
            assert terminal.command == ["/bin/bash"]

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_default_shell_windows(self, mock_which: MagicMock) -> None:
        """Test default shell on Windows."""
        mock_which.return_value = "C:\\Program Files\\ttyd\\ttyd.exe"
        with patch.object(sys, "platform", "win32"):
            terminal = TerminalEmulator()
            assert terminal.command == ["cmd.exe"]


class TestTerminalEmulatorErrorViews:
    """Tests for error view rendering."""

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_ttyd_not_found_error(self, mock_which: MagicMock) -> None:
        """Test error view when ttyd is not installed."""
        mock_which.return_value = None
        terminal = TerminalEmulator()

        # Should show error content, not webview
        assert terminal.content is not None
        # Error view contains a Column with error message
        assert hasattr(terminal.content, "content")

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", False)
    def test_webview_not_available_error(self, mock_which: MagicMock) -> None:
        """Test error view when flet-webview is not installed."""
        mock_which.return_value = "/usr/bin/ttyd"
        terminal = TerminalEmulator()

        # Should show error content
        assert terminal.content is not None


class TestTerminalEmulatorCallbacks:
    """Tests for callback handling."""

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_callbacks_stored(self, mock_which: MagicMock) -> None:
        """Test that callbacks are properly stored."""
        mock_which.return_value = "/usr/bin/ttyd"
        on_connected = MagicMock()
        on_disconnected = MagicMock()
        on_error = MagicMock()

        terminal = TerminalEmulator(
            on_connected=on_connected,
            on_disconnected=on_disconnected,
            on_error=on_error,
        )

        assert terminal.on_connected is on_connected
        assert terminal.on_disconnected is on_disconnected
        assert terminal.on_error is on_error


class TestTerminalEmulatorProcessManagement:
    """Tests for ttyd process management."""

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_start_without_ttyd(self, mock_which: MagicMock) -> None:
        """Test start fails when ttyd is not available."""
        mock_which.return_value = "/usr/bin/ttyd"
        terminal = TerminalEmulator()

        # Now make ttyd unavailable for start
        mock_which.return_value = None
        on_error = MagicMock()
        terminal.on_error = on_error

        result = terminal.start()
        assert result is False
        on_error.assert_called_once_with("ttyd not found in PATH")

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.subprocess.Popen")
    @patch("engn.ui.terminal_emulator.time.sleep")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_start_success(
        self,
        mock_sleep: MagicMock,
        mock_popen: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test successful start."""
        mock_which.return_value = "/usr/bin/ttyd"
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process

        terminal = TerminalEmulator(command=["bash"])
        result = terminal.start()

        assert result is True
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert "ttyd" in call_args
        assert "--writable" in call_args
        assert "bash" in call_args

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.subprocess.Popen")
    @patch("engn.ui.terminal_emulator.time.sleep")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_start_process_fails(
        self,
        mock_sleep: MagicMock,
        mock_popen: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test start when ttyd process exits immediately."""
        mock_which.return_value = "/usr/bin/ttyd"
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process exited
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"port already in use"
        mock_process.stderr = mock_stderr
        mock_popen.return_value = mock_process

        on_error = MagicMock()
        terminal = TerminalEmulator(on_error=on_error)
        result = terminal.start()

        assert result is False
        on_error.assert_called_once()
        assert "port already in use" in on_error.call_args[0][0]

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.subprocess.Popen")
    @patch("engn.ui.terminal_emulator.time.sleep")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_stop(
        self,
        mock_sleep: MagicMock,
        mock_popen: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test stopping the terminal."""
        mock_which.return_value = "/usr/bin/ttyd"
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        on_disconnected = MagicMock()
        terminal = TerminalEmulator(on_disconnected=on_disconnected)
        terminal.start()
        terminal.stop()

        mock_process.terminate.assert_called_once()
        on_disconnected.assert_called_once()
        assert terminal.is_running is False

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.subprocess.Popen")
    @patch("engn.ui.terminal_emulator.time.sleep")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_restart(
        self,
        mock_sleep: MagicMock,
        mock_popen: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test restarting the terminal."""
        mock_which.return_value = "/usr/bin/ttyd"
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        terminal = TerminalEmulator()
        terminal.start()
        result = terminal.restart()

        assert result is True
        assert mock_popen.call_count == 2  # Called twice (start + restart)

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_double_start(self, mock_which: MagicMock) -> None:
        """Test that starting twice returns True without creating new process."""
        mock_which.return_value = "/usr/bin/ttyd"
        terminal = TerminalEmulator()

        # Manually set process to simulate already running
        terminal._ttyd_process = MagicMock()

        result = terminal.start()
        assert result is True  # Returns True without creating new process


class TestTerminalEmulatorProperties:
    """Tests for component properties."""

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_terminal_url_property(self, mock_which: MagicMock) -> None:
        """Test terminal_url property returns correct value."""
        mock_which.return_value = "/usr/bin/ttyd"
        terminal = TerminalEmulator(port=8080)
        assert terminal.terminal_url == "http://localhost:8080"

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_port_property(self, mock_which: MagicMock) -> None:
        """Test port property returns correct value."""
        mock_which.return_value = "/usr/bin/ttyd"
        terminal = TerminalEmulator(port=8080)
        assert terminal.port == 8080

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_is_running_false_by_default(self, mock_which: MagicMock) -> None:
        """Test is_running is False by default."""
        mock_which.return_value = "/usr/bin/ttyd"
        terminal = TerminalEmulator()
        assert terminal.is_running is False

    @patch("engn.ui.terminal_emulator.shutil.which")
    @patch("engn.ui.terminal_emulator.subprocess.Popen")
    @patch("engn.ui.terminal_emulator.time.sleep")
    @patch("engn.ui.terminal_emulator.WEBVIEW_AVAILABLE", True)
    def test_is_running_after_start(
        self,
        mock_sleep: MagicMock,
        mock_popen: MagicMock,
        mock_which: MagicMock,
    ) -> None:
        """Test is_running after successful start."""
        mock_which.return_value = "/usr/bin/ttyd"
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        terminal = TerminalEmulator()
        terminal.start()

        # is_running requires both _is_running flag and process
        # Note: _is_running is set by page_ended callback, not start()
        assert terminal._ttyd_process is not None
