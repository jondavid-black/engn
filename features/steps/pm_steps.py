from behave import given, when, then  # type: ignore
from pathlib import Path
import sys
import git

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


# Branching steps


@given('I have a project named "{project_name}"')  # type: ignore
def step_create_dummy_project(context, project_name):
    """Creates a dummy git project in the test directory."""
    project_dir = context.test_dir / project_name
    project_dir.mkdir()
    repo = git.Repo.init(project_dir)

    # Create an initial commit so we have a HEAD
    readme = project_dir / "README.md"
    readme.write_text("# Test Project")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    # Ensure active branch is main
    if repo.active_branch.name != "main":
        repo.create_head("main")
        repo.heads.main.checkout()


@when('I create a branch named "{branch_name}" in "{project_name}"')  # type: ignore
def step_create_branch(context, branch_name, project_name):
    pm = ProjectManager(context.test_dir)
    pm.create_branch(project_name, branch_name)


@then('the active branch for "{project_name}" should be "{branch_name}"')  # type: ignore
def step_verify_active_branch(context, project_name, branch_name):
    project_dir = context.test_dir / project_name
    repo = git.Repo(project_dir)
    assert repo.active_branch.name == branch_name


@then('"{branch_name}" should be in the list of branches for "{project_name}"')  # type: ignore
def step_verify_branch_exists(context, branch_name, project_name):
    pm = ProjectManager(context.test_dir)
    branches = pm.list_branches(project_name)
    assert branch_name in branches


@given('I have a branch named "{branch_name}" in "{project_name}"')  # type: ignore
def step_ensure_branch_exists(context, branch_name, project_name):
    pm = ProjectManager(context.test_dir)
    try:
        pm.create_branch(project_name, branch_name)
    except ValueError:
        # Branch might already exist or be active, which is fine
        pass


@when('I checkout the "{branch_name}" branch in "{project_name}"')  # type: ignore
def step_checkout_branch(context, branch_name, project_name):
    pm = ProjectManager(context.test_dir)
    pm.checkout_branch(project_name, branch_name)


@when('I delete the branch "{branch_name}" in "{project_name}"')  # type: ignore
def step_delete_branch(context, branch_name, project_name):
    pm = ProjectManager(context.test_dir)
    pm.delete_branch(project_name, branch_name)


@then('"{branch_name}" should not be in the list of branches for "{project_name}"')  # type: ignore
def step_verify_branch_not_exists(context, branch_name, project_name):
    pm = ProjectManager(context.test_dir)
    branches = pm.list_branches(project_name)
    assert branch_name not in branches
