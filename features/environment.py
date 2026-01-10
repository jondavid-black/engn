import shutil
import tempfile
import os


def before_scenario(context, scenario):
    # Create a temporary directory for file system operations
    context.test_dir = tempfile.mkdtemp()
    context.original_cwd = os.getcwd()
    os.chdir(context.test_dir)


def after_scenario(context, scenario):
    # Restore original directory and clean up
    os.chdir(context.original_cwd)
    shutil.rmtree(context.test_dir)
