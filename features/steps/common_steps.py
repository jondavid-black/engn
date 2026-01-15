from behave import given, when, then
import subprocess
import sys
import os
import shlex
from pathlib import Path

# Add src to sys.path to allow imports
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from engn.utils import get_version  # noqa: E402


@given("the {app_name} application is installed")  # type: ignore
def step_app_installed(context, app_name):
    context.app_name = app_name


@when('I run "{command}"')  # type: ignore
def step_run_command(context, command):
    # We run the command using subprocess to simulate real CLI usage
    # We use 'uv run' to ensure we are in the correct environment or call python -m
    cmd_parts = shlex.split(command)
    # Replace the command name with python -m <module> execution for test robustness in dev
    if cmd_parts[0] == "engn":
        cmd_parts[0] = "engn.main"

    # Execute as a module
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, "-m"] + cmd_parts,
        capture_output=True,
        text=True,
        cwd=os.getcwd(),  # Use the current working directory (which might be temp dir)
        env=env,
    )
    context.output = result.stdout.strip()
    context.return_code = result.returncode


@then("the output should contain the version number")  # type: ignore
def step_verify_output(context):
    expected_version = get_version()
    if expected_version not in context.output:
        print(
            f"DEBUG: Expected version '{expected_version}' not found in output '{context.output}'"
        )
    assert expected_version in context.output
    assert context.return_code == 0
