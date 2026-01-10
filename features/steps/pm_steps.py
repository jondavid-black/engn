from behave import given, when, then  # type: ignore
from pathlib import Path
import sys

# Ensure src is in python path
project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from engn.pm import ProjectManager


@given('I use the ProjectManager to create a project from "{repo_url}"')  # type: ignore
def step_pm_create_project(context, repo_url):
    pm = ProjectManager(context.test_dir)
    pm.create_project(repo_url)


@then('the project "{project_name}" should be listed in the project list')  # type: ignore
def step_pm_project_listed(context, project_name):
    pm = ProjectManager(context.test_dir)
    projects = pm.list_projects()
    assert project_name in projects, f"Project '{project_name}' not found in {projects}"


@when('I use the ProjectManager to delete the project "{project_name}"')  # type: ignore
def step_pm_delete_project(context, project_name):
    pm = ProjectManager(context.test_dir)
    pm.delete_project(project_name)


@then('the project "{project_name}" should not be listed in the project list')  # type: ignore
def step_pm_project_not_listed(context, project_name):
    pm = ProjectManager(context.test_dir)
    projects = pm.list_projects()
    assert project_name not in projects, (
        f"Project '{project_name}' was found in {projects} but should have been deleted"
    )
