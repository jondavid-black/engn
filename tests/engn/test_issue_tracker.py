import pytest
from unittest.mock import patch, MagicMock
from engn.issue_tracker import IssueTracker, IssueTrackerError
import json
import subprocess


@pytest.fixture
def tracker():
    return IssueTracker()


def test_list_issues_success(tracker):
    mock_output = [{"id": "bd-1", "title": "Test Issue", "status": "open"}]
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(mock_output), returncode=0)

        issues = tracker.list_issues()

        assert issues == mock_output
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "list" in args
        assert "--json" in args


def test_create_issue_success(tracker):
    mock_output = {"id": "bd-2", "title": "New Issue"}
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(mock_output), returncode=0)

        issue = tracker.create_issue("New Issue", description="Desc")

        assert issue == mock_output
        args = mock_run.call_args[0][0]
        assert "create" in args
        assert "New Issue" in args
        assert "--description" in args


def test_add_comment_success(tracker):
    mock_output = {"id": "bd-1", "comment": "Nice"}
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(mock_output), returncode=0)

        result = tracker.add_comment("bd-1", "Nice")

        assert result == mock_output
        args = mock_run.call_args[0][0]
        assert "comments" in args
        assert "add" in args


def test_update_status_success(tracker):
    mock_output = {"id": "bd-1", "status": "in_progress"}
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(mock_output), returncode=0)

        result = tracker.update_status("bd-1", "in_progress")

        assert result == mock_output
        args = mock_run.call_args[0][0]
        assert "update" in args
        assert "--status" in args


def test_command_failure(tracker):
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["bd"], stderr="Error")

        with pytest.raises(IssueTrackerError):
            tracker.list_issues()


def test_json_decode_error(tracker):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Invalid JSON", returncode=0)

        with pytest.raises(IssueTrackerError):
            tracker.list_issues()
