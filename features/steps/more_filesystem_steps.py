from behave import given
import os


@given('a file "{file_path}" with content:')  # type: ignore
def step_create_file_with_content(context, file_path):
    """Create a file with specific content."""
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(file_path, "w") as f:
        f.write(context.text)


@given('a directory "{dir_path}"')  # type: ignore
def step_create_directory(context, dir_path):
    """Create a directory."""
    os.makedirs(dir_path, exist_ok=True)
