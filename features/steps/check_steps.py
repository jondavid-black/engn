from behave import when, then  # type: ignore
import subprocess
import sys
import os
from pathlib import Path


@when('I run the "check" command with "{path}"')  # type: ignore
def step_run_check_with_path(context, path):
    """Run the check command with a specific path."""
    project_root = Path(__file__).resolve().parents[2]
    src_path = project_root / "src"

    cmd = [sys.executable, "-m", "engn.main", "proj", "check", path]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")

    # Run in the temporary directory created by filesystem steps if available
    cwd = getattr(context, "temp_dir", os.getcwd())

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env)
    context.output = result.stdout + result.stderr
    context.return_code = result.returncode


@when('I run the "check" command')  # type: ignore
def step_run_check_default(context):
    """Run the check command without arguments."""
    project_root = Path(__file__).resolve().parents[2]
    src_path = project_root / "src"

    cmd = [sys.executable, "-m", "engn.main", "proj", "check"]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")

    cwd = getattr(context, "temp_dir", os.getcwd())

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env)
    context.output = result.stdout + result.stderr
    context.return_code = result.returncode


@then('the output should contain "{text}"')  # type: ignore
def step_output_contains(context, text):
    """Check if output contains specific text."""
    assert text in context.output, f"Expected '{text}' in output:\n{context.output}"
