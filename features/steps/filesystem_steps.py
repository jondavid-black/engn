from behave import given, then  # type: ignore
import os


@given('I create a temporary directory named "{dir_name}"')  # type: ignore
def step_create_temp_dir(context, dir_name):
    # Since we are already in a temp dir from environment.py, we just make a subdir
    os.makedirs(dir_name, exist_ok=True)


@then('a file named "{file_path}" should exist')  # type: ignore
def step_file_should_exist(context, file_path):
    assert os.path.isfile(file_path), f"File {file_path} does not exist"


@then('a directory named "{dir_path}" should exist')  # type: ignore
def step_directory_should_exist(context, dir_path):
    assert os.path.isdir(dir_path), f"Directory {dir_path} does not exist"


@then('the file "{file_path}" should contain "{content}"')  # type: ignore
def step_file_should_contain(context, file_path, content):
    assert os.path.isfile(file_path), f"File {file_path} does not exist"
    with open(file_path, "r") as f:
        file_content = f.read()
    assert content in file_content, f"File {file_path} does not contain '{content}'"
