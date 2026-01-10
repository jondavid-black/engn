from behave import given, when, then
from engn.issue_tracker import IssueTracker
from unittest.mock import MagicMock, patch
import json


@given("the beads issue tracker is initialized")
def step_tracker_init(context):
    context.tracker = IssueTracker()
    context.mock_bd_run = MagicMock()
    # Patch subprocess.run on the instance or class to intercept calls
    context.patcher = patch("subprocess.run", context.mock_bd_run)
    context.patcher.start()


@when('I create a new task with title "{title}"')
def step_create_task(context, title):
    # Mock the return value for create
    context.mock_bd_run.return_value = MagicMock(
        stdout=json.dumps({"id": "bd-100", "title": title, "status": "open"}),
        returncode=0,
    )
    context.last_issue = context.tracker.create_issue(title)


@when("I list open issues")
def step_list_issues(context):
    # Mock list return. If we just created one, return that in a list
    context.mock_bd_run.return_value = MagicMock(
        stdout=json.dumps([context.last_issue]), returncode=0
    )
    context.issues = context.tracker.list_issues()


@then('I should see an issue with title "{title}" in the list')
def step_verify_issue_in_list(context, title):
    found = any(issue["title"] == title for issue in context.issues)
    assert found, f"Issue with title '{title}' not found in {context.issues}"


@given('a task exists with title "{title}"')
def step_task_exists(context, title):
    context.existing_task_id = "bd-101"
    context.existing_task_title = title
    # We simulate it already existing, no action needed on tracker
    # but we prepare mocks for subsequent calls


@when('I add a comment "{comment}" to the task')
def step_add_comment(context, comment):
    context.mock_bd_run.return_value = MagicMock(
        stdout=json.dumps({"id": context.existing_task_id, "comment": comment}),
        returncode=0,
    )
    context.comment_result = context.tracker.add_comment(
        context.existing_task_id, comment
    )


@then('the task should have a comment "{comment}"')
def step_verify_comment(context, comment):
    # In a real integration test we'd query comments.
    # Here we verify the mock was called correctly and result matches
    args = context.mock_bd_run.call_args[0][0]
    assert "comments" in args
    assert "add" in args
    assert context.existing_task_id in args
    assert comment in args


@when('I update the task status to "{status}"')
def step_update_status(context, status):
    context.mock_bd_run.return_value = MagicMock(
        stdout=json.dumps({"id": context.existing_task_id, "status": status}),
        returncode=0,
    )
    context.update_result = context.tracker.update_status(
        context.existing_task_id, status
    )


@then('the task status should be "{status}"')
def step_verify_status(context, status):
    assert context.update_result["status"] == status
    args = context.mock_bd_run.call_args[0][0]
    assert "update" in args
    assert "--status" in args
    assert status in args


def after_scenario(context, scenario):
    if hasattr(context, "patcher"):
        context.patcher.stop()
