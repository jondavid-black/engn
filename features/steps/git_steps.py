from behave import given  # type: ignore
import subprocess


@given('I clone the repository "{repo_url}" to "{target_dir}"')  # type: ignore
def step_git_clone(context, repo_url, target_dir):
    # Clone the repository into the temporary test directory
    result = subprocess.run(
        ["git", "clone", repo_url, target_dir],
        capture_output=True,
        text=True,
        cwd=context.test_dir,
    )
    assert result.returncode == 0, f"Git clone failed: {result.stderr}"
