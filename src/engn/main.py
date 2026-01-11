import argparse
import sys
from pathlib import Path
from typing import List

from pydantic import ValidationError

from engn.utils import get_version
from engn.config import ProjectConfig
from engn.data.storage import EngnDataModel
from engn import project


def run_check(target: Path | None, working_dir: Path) -> None:
    """
    Check validity of JSONL files in target path or configured paths.
    """
    files_to_check: List[Path] = []

    # 1. Determine files to check
    if target:
        if target.is_file():
            if target.suffix == ".jsonl":
                files_to_check.append(target)
        elif target.is_dir():
            files_to_check.extend(target.rglob("*.jsonl"))
        else:
            print(f"Error: Target '{target}' not found.")
            sys.exit(1)
    else:
        # Load config to get paths
        config = ProjectConfig.load(working_dir)
        # Check all configured paths
        for path_str in [config.pm_path, config.sysengn_path, config.ux_path]:
            path = working_dir / path_str
            if path.exists():
                files_to_check.extend(path.rglob("*.jsonl"))

    if not files_to_check:
        print("No JSONL files found to check.")
        return

    # 2. Process files
    errors: List[str] = []

    # Initialize storage with our union type
    # We use a dummy path since we'll set it per file or use a helper
    # Actually, JSONLStorage takes a specific file path.
    # But we can instantiate it for each file.

    # Create a TypeAdapter once for reuse since the model type is constant
    from pydantic import TypeAdapter

    adapter = TypeAdapter(EngnDataModel)

    for file_path in files_to_check:
        # Create storage instance for this file
        # We don't actually need the full storage engine instance here since we are doing custom
        # line-by-line validation to get line numbers, which the storage engine abstraction hides.
        # But if we wanted to reuse logic, we'd have to enhance storage engine or duplicate it.
        # Duplicating the read loop here is safer for the specific requirement of line reporting.

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        adapter.validate_json(line)
                    except ValidationError as e:
                        # Format error message
                        # Pydantic errors can be complex, let's just get the first error or summary
                        msg = str(e).replace("\n", " ")
                        # Truncate if too long?
                        if len(msg) > 200:
                            msg = msg[:197] + "..."

                        errors.append(f"{file_path}:{line_num}: {msg}")
                    except Exception as e:
                        errors.append(f"{file_path}:{line_num}: {str(e)}")

        except Exception as e:
            errors.append(f"{file_path}: Failed to open/read file: {str(e)}")

    # 3. Report results
    if not errors:
        print("All checks passed!")
    else:
        print(f"Found {len(errors)} errors.")
        for error in errors:
            print(error)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The Intelligent Engine for Building Systems"
    )
    parser.add_argument(
        "--version", action="store_true", help="Show the version and exit"
    )

    # Create subparsers for commands like 'init'
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Project command
    project_parser = subparsers.add_parser("project", help="Manage engn projects")
    project_subparsers = project_parser.add_subparsers(
        dest="subcommand", help="Project subcommands"
    )

    # project new <name>
    new_parser = project_subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("name", help="Name of the new project")

    # project clone <url>
    clone_parser = project_subparsers.add_parser(
        "clone", help="Clone an existing project"
    )
    clone_parser.add_argument("url", help="URL of the project to clone")
    clone_parser.add_argument("--name", help="Optional name for the project directory")

    # project delete <name>
    delete_parser = project_subparsers.add_parser("delete", help="Delete a project")
    delete_parser.add_argument("name", help="Name of the project to delete")
    delete_parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm deletion without prompting"
    )

    # project init <name>
    init_proj_parser = project_subparsers.add_parser(
        "init", help="Initialize an existing project with engn"
    )
    init_proj_parser.add_argument(
        "name", help="Name of the project directory to initialize"
    )

    # project status <name>
    status_parser = project_subparsers.add_parser("status", help="Show project status")
    status_parser.add_argument("name", help="Name of the project")

    # project list
    project_subparsers.add_parser("list", help="List all projects")

    # Top-level Init command (kept for backward compatibility, but uses new logic)
    init_parser = subparsers.add_parser("init", help="Initialize a new engn project")
    init_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to initialize the project in (default: current directory)",
    )

    # Check command
    check_parser = subparsers.add_parser("check", help="Check validity of data files")
    check_parser.add_argument(
        "target",
        nargs="?",
        help="Path to JSONL file or directory to check (default: check all configured paths)",
    )

    parser.add_argument(
        "-w",
        "--working-directory",
        default=".",
        help="The working directory for projects (default: current directory)",
    )

    args = parser.parse_args()

    if args.version:
        print(get_version())
        sys.exit(0)

    # Common argument handling
    working_dir = Path(args.working_directory).resolve()

    if args.command == "project":
        if not args.subcommand:
            project_parser.print_help()
            sys.exit(0)

        if args.subcommand == "new":
            try:
                project.create_new_project(args.name, working_dir)
                print(f"Created new project: {args.name}")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        elif args.subcommand == "clone":
            try:
                project.clone_project(args.url, working_dir, args.name)
                print(f"Cloned project from {args.url}")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        elif args.subcommand == "delete":
            if not args.yes:
                confirm = input(
                    f"Are you sure you want to delete project '{args.name}'? (y/N): "
                )
                if confirm.lower() != "y":
                    print("Deletion cancelled.")
                    sys.exit(0)

            if project.delete_project(args.name, working_dir):
                print(f"Deleted project: {args.name}")
            else:
                print(f"Error: Project '{args.name}' not found.")
                sys.exit(1)

        elif args.subcommand == "init":
            target_path = working_dir / args.name
            if not target_path.exists():
                print(f"Error: Directory '{args.name}' not found.")
                sys.exit(1)
            project.init_project_structure(target_path)
            print(f"Initialized project: {args.name}")

        elif args.subcommand == "list":
            projects = project.list_projects(working_dir)
            if not projects:
                print("No projects found.")
            else:
                for p in projects:
                    print(p)

        elif args.subcommand == "status":
            status = project.get_project_status(args.name, working_dir)
            if not status["exists"]:
                print(f"Project '{args.name}' not found.")
                sys.exit(1)

            print(f"Project: {status['name']}")
            print(f"Path: {status['path']}")
            print(f"Git: {'Yes' if status['is_git'] else 'No'}")
            print(f"Beads: {'Yes' if status['is_beads'] else 'No'}")
            print(f"Engn: {'Yes' if status['is_engn'] else 'No'}")
            if "git_status" in status:
                print(f"Git Status: {status['git_status']}")

        sys.exit(0)

    if args.command == "init":
        # Resolve the path relative to current working directory
        target_path = Path.cwd() / args.path
        project.init_project_structure(target_path)
        print(f"Initialized engn project in {target_path}")
        sys.exit(0)

    if args.command == "check":
        target = Path(args.target).resolve() if args.target else None
        run_check(target, working_dir)
        sys.exit(0)

    # No command provided
    parser.print_help()


if __name__ == "__main__":
    main()
