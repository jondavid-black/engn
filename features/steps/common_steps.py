from behave import given, when, then
import subprocess
import sys
from engn.utils import get_version


@given("the {app_name} application is installed")  # type: ignore
def step_app_installed(context, app_name):
    context.app_name = app_name


@when('I run "{command}"')  # type: ignore
def step_run_command(context, command):
    # We run the command using subprocess to simulate real CLI usage
    # We use 'uv run' to ensure we are in the correct environment or call python -m
    cmd_parts = command.split()
    # Replace the command name with python -m <module> execution for test robustness in dev
    if cmd_parts[0] in ["engn", "sysengn", "projengn"]:
        cmd_parts[0] = f"{cmd_parts[0]}.main"

    # Execute as a module
    result = subprocess.run(
        [sys.executable, "-m"] + cmd_parts,
        capture_output=True,
        text=True,
        cwd=sys.path[0],  # Ensure we are running from project root context if needed
    )
    context.output = result.stdout.strip()
    context.return_code = result.returncode


@then("the output should contain the version number")  # type: ignore
def step_verify_output(context):
    expected_version = get_version()
    assert expected_version in context.output
    assert context.return_code == 0
