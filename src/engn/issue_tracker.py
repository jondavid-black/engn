import json
import subprocess
from pathlib import Path
from typing import Any, Optional


class IssueTrackerError(Exception):
    """Base exception for issue tracker errors."""

    pass


class IssueTracker:
    """Interface for interacting with the beads (bd) issue tracker."""

    def __init__(self, working_directory: Optional[str | Path] = None):
        self.working_directory = (
            Path(working_directory) if working_directory else Path.cwd()
        )

    def _run_bd_command(self, args: list[str]) -> Any:
        """
        Run a bd command and return the JSON output.

        Args:
            args: List of command arguments.

        Returns:
            Parsed JSON output or None if output is empty.

        Raises:
            IssueTrackerError: If the command fails.
        """
        cmd = ["bd"] + args + ["--json"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.working_directory),
            )
            if not result.stdout.strip():
                return None
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise IssueTrackerError(f"Command failed: {e.stderr}") from e
        except json.JSONDecodeError as e:
            raise IssueTrackerError(f"Failed to parse JSON output: {e}") from e

    def list_issues(
        self, status: str = "open", limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        List issues in the project.

        Args:
            status: Filter by status (open, closed, etc.). Defaults to "open".
            limit: Max number of issues to return. Defaults to 50.

        Returns:
            List of issue dictionaries.
        """
        args = ["list", "--status", status, "--limit", str(limit)]
        result = self._run_bd_command(args)
        return result if isinstance(result, list) else []

    def create_issue(
        self,
        title: str,
        description: Optional[str] = None,
        issue_type: str = "task",
        priority: int = 2,
    ) -> dict[str, Any]:
        """
        Create a new issue.

        Args:
            title: Title of the issue.
            description: Optional description.
            issue_type: Type of issue (task, bug, feature). Defaults to "task".
            priority: Priority (0-4). Defaults to 2.

        Returns:
            Dictionary containing the created issue details.
        """
        args = [
            "create",
            title,
            "--type",
            issue_type,
            "--priority",
            str(priority),
        ]
        if description:
            args.extend(["--description", description])

        result = self._run_bd_command(args)
        # bd create returns the issue object, usually a dict or list with 1 dict
        if isinstance(result, list) and result:
            return result[0]
        if isinstance(result, dict):
            return result
        raise IssueTrackerError("Unexpected return format from create command")

    def add_comment(self, issue_id: str, comment: str) -> dict[str, Any]:
        """
        Add a comment to an issue.

        Args:
            issue_id: The ID of the issue.
            comment: The comment text.

        Returns:
            Dictionary containing the added comment details.
        """
        args = ["comments", "add", issue_id, comment]
        result = self._run_bd_command(args)
        if isinstance(result, dict):
            return result
        # Sometimes it might return a list or just success message wrapped
        if isinstance(result, list) and result:
            return result[0]
        raise IssueTrackerError("Unexpected return format from add_comment")

    def update_status(self, issue_id: str, status: str) -> dict[str, Any]:
        """
        Update the status of an issue.

        Args:
            issue_id: The ID of the issue.
            status: The new status (e.g., in_progress, closed).

        Returns:
            Dictionary containing the updated issue details.
        """
        args = ["update", issue_id, "--status", status]
        result = self._run_bd_command(args)
        if isinstance(result, list) and result:
            return result[0]
        if isinstance(result, dict):
            return result
        raise IssueTrackerError("Unexpected return format from update_status")
