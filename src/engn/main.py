import argparse
import getpass
import sys
import importlib.resources
from pathlib import Path
from typing import List

from pydantic import ValidationError

from engn.utils import get_version
from engn.config import ProjectConfig
from engn.data.storage import EngnDataModel
from engn.data.models import (
    TypeDef,
    Enumeration,
    Import,
    Module,
    get_referenced_types,
    get_structural_dependencies,
)
from engn import project
from engn.core.auth import (
    Role,
    create_user,
    remove_user,
    list_users,
    get_user_by_email,
    add_role_to_user,
    remove_role_from_user,
    get_all_roles,
)


def load_standard_modules() -> None:
    """Load standard modules packaged with the application."""
    try:
        # standard_modules.jsonl is in engn.data.modules
        resource_path = importlib.resources.files("engn.data.modules").joinpath(
            "standard_modules.jsonl"
        )

        if not resource_path.is_file():
            return

        from pydantic import TypeAdapter

        adapter = TypeAdapter(EngnDataModel)

        with resource_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    # This will automatically register modules via model_post_init
                    adapter.validate_json(line)
                except Exception:
                    pass
    except Exception:
        # Silently fail if resources cannot be loaded
        pass


def prompt_for_password() -> str:
    """Prompt for password with confirmation, hiding input."""
    while True:
        password = getpass.getpass("Password: ")
        if not password:
            print("Error: Password cannot be empty.")
            continue

        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Error: Passwords do not match. Please try again.")
            continue

        return password


def print_error(
    message: str,
    file_path: Path | None = None,
    line_num: int | None = None,
    verbose: bool = False,
) -> None:
    """
    Print an error message in a consistent format.
    Format: ERROR: <file_name> at line <line_number> - <error_message>
    """
    if file_path:
        if line_num is not None:
            print(f"ERROR: {file_path} at line {line_num} - {message}")
        else:
            print(f"ERROR: {file_path} - {message}")
    else:
        print(f"ERROR: {message}")
    if verbose:
        import traceback

        traceback.print_exc()


def run_check(target: Path | None, working_dir: Path, verbose: bool = False) -> None:
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

    # 2. Process files (with import resolution)
    # Store errors as (file_path, line_num, message) for sorting
    errors: List[tuple[Path, int, str]] = []
    # Track parsed items for post-validation of type references
    parsed_items: List[tuple[Path, int, TypeDef | Enumeration | Import]] = []
    # Track processed files to avoid infinite loops from circular imports
    processed_files: set[Path] = set()

    # Create a TypeAdapter once for reuse since the model type is constant
    from pydantic import TypeAdapter

    adapter = TypeAdapter(EngnDataModel)

    # Use a queue to process files, allowing imports to add more files
    files_queue = list(files_to_check)

    while files_queue:
        file_path = files_queue.pop(0)

        # Skip if already processed (handles circular imports)
        resolved_path = file_path.resolve()
        if resolved_path in processed_files:
            continue
        processed_files.add(resolved_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        item = adapter.validate_json(line)
                        parsed_items.append((file_path, line_num, item))

                        # Handle imports - add imported files to the queue
                        if isinstance(item, Import):
                            files_to_import = []
                            if item.files:
                                files_to_import.extend(item.files)
                            if item.modules:
                                from engn.data.models import _MODULE_REGISTRY

                                for module_name in item.modules:
                                    if module_name in _MODULE_REGISTRY:
                                        files_to_import.extend(
                                            _MODULE_REGISTRY[module_name].files
                                        )
                                    else:
                                        errors.append(
                                            (
                                                file_path,
                                                line_num,
                                                f"Module not found: {module_name}",
                                            )
                                        )

                            for import_file in files_to_import:
                                import_path = Path(import_file)
                                # Resolve relative paths from the importing file's directory
                                if not import_path.is_absolute():
                                    import_path = file_path.parent / import_path
                                if import_path.exists():
                                    files_queue.append(import_path)
                                else:
                                    errors.append(
                                        (
                                            file_path,
                                            line_num,
                                            f"Imported file not found: {import_file}",
                                        )
                                    )
                    except ValidationError as e:
                        msg = str(e).replace("\n", " ")
                        errors.append((file_path, line_num, msg))
                        if verbose:
                            import traceback

                            traceback.print_exc()
                    except Exception as e:
                        errors.append((file_path, line_num, str(e)))
                        if verbose:
                            import traceback

                            traceback.print_exc()

        except Exception as e:
            # File-level errors use line 0 so they sort first
            errors.append((file_path, 0, f"Failed to open/read file: {str(e)}"))
            if verbose:
                import traceback

                traceback.print_exc()

    # 3. Post-validation: check type references
    defined_types = set()
    for _, _, item in parsed_items:
        if isinstance(item, TypeDef):
            defined_types.add(item.name)
        elif isinstance(item, Enumeration):
            defined_types.add(item.name)

    for file_path, line_num, item in parsed_items:
        if isinstance(item, TypeDef):
            for prop in item.properties:
                referenced = get_referenced_types(prop.type)
                for ref_type in referenced:
                    if ref_type not in defined_types:
                        errors.append(
                            (
                                file_path,
                                line_num,
                                f"Unknown type '{ref_type}' referenced in property '{item.name}.{prop.name}'",
                            )
                        )

    # 4. Check for circular dependencies using structural dependencies
    # Build dependency graph: type_name -> set of types it depends on structurally
    type_to_location: dict[str, tuple[Path, int]] = {}
    dependency_graph: dict[str, set[str]] = {}

    for file_path, line_num, item in parsed_items:
        if isinstance(item, TypeDef):
            type_to_location[item.name] = (file_path, line_num)
            deps: set[str] = set()
            for prop in item.properties:
                structural_deps = get_structural_dependencies(prop.type)
                # Only include dependencies on other TypeDefs (not enums)
                for dep in structural_deps:
                    if dep in defined_types and dep not in {
                        e.name for _, _, e in parsed_items if isinstance(e, Enumeration)
                    }:
                        deps.add(dep)
            dependency_graph[item.name] = deps

    # Detect cycles using DFS
    def find_cycle(node: str, visited: set[str], path: list[str]) -> list[str] | None:
        if node in path:
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        if node in visited:
            return None
        visited.add(node)
        path.append(node)
        for dep in dependency_graph.get(node, set()):
            cycle = find_cycle(dep, visited, path)
            if cycle:
                return cycle
        path.pop()
        return None

    visited: set[str] = set()
    for type_name in dependency_graph:
        if type_name not in visited:
            cycle = find_cycle(type_name, visited, [])
            if cycle:
                # Report error for the first type in the cycle
                first_type = cycle[0]
                file_path, line_num = type_to_location.get(
                    first_type, (Path("unknown"), 0)
                )
                cycle_str = " -> ".join(cycle)
                errors.append(
                    (file_path, line_num, f"Circular dependency detected: {cycle_str}")
                )
                break  # Report only one cycle error to avoid duplicates

    # 5. Report results
    if not errors:
        print("All checks passed!")
    else:
        # Sort errors by file name, then line number
        errors.sort(key=lambda e: (str(e[0]), e[1]))
        print(f"Found {len(errors)} errors.")
        for file_path, line_num, msg in errors:
            if line_num == 0:
                print(f"{file_path}:  ERROR - {msg}")
            else:
                print(f"{file_path} at line {line_num}:  ERROR - {msg}")


def run_print(target: Path | None, working_dir: Path, verbose: bool = False) -> None:
    """
    Print enums, data types, and data from JSONL files in human-readable form.
    """
    files_to_process: List[Path] = []
    if target:
        if target.is_file():
            if target.suffix == ".jsonl":
                files_to_process.append(target)
        elif target.is_dir():
            files_to_process.extend(target.rglob("*.jsonl"))
        else:
            print(f"Error: Target '{target}' not found.")
            sys.exit(1)
    else:
        config = ProjectConfig.load(working_dir)
        for path_str in [config.pm_path, config.sysengn_path, config.ux_path]:
            path = working_dir / path_str
            if path.exists():
                files_to_process.extend(path.rglob("*.jsonl"))

    if not files_to_process:
        print("No JSONL files found to print.")
        return

    from engn.data.models import TypeDef, Enumeration
    from engn.data.storage import JSONLStorage
    from pydantic import TypeAdapter

    # 1. Collect all definitions across all files to support cross-file types
    # Process files with import resolution
    all_definitions = []
    def_adapter = TypeAdapter(EngnDataModel)
    processed_files: set[Path] = set()
    files_queue = list(files_to_process)

    while files_queue:
        file_path = files_queue.pop(0)

        # Skip if already processed
        resolved_path = file_path.resolve()
        if resolved_path in processed_files:
            continue
        processed_files.add(resolved_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = def_adapter.validate_json(line)
                        all_definitions.append(item)

                        # Handle imports - add imported files to the queue
                        if isinstance(item, Import):
                            if item.files:
                                for import_file in item.files:
                                    import_path = Path(import_file)
                                    if not import_path.is_absolute():
                                        import_path = file_path.parent / import_path
                                    if import_path.exists():
                                        files_queue.append(import_path)
                            if item.modules:
                                from engn.data.models import _MODULE_REGISTRY

                                for module_name in item.modules:
                                    if module_name in _MODULE_REGISTRY:
                                        module = _MODULE_REGISTRY[module_name]
                                        for import_file in module.files:
                                            import_path = Path(import_file)
                                            if not import_path.is_absolute():
                                                import_path = (
                                                    file_path.parent / import_path
                                                )
                                            if import_path.exists():
                                                files_queue.append(import_path)
                    except Exception:
                        pass  # Not a definition
        except Exception as e:
            if verbose:
                import traceback

                traceback.print_exc()
            else:
                print(f"ERROR: {file_path} - Failed to read: {e}")

    # Update files_to_process to include all resolved files
    files_to_process = list(processed_files)

    # Filter out Import items - they're directives, not type definitions
    type_definitions = [d for d in all_definitions if not isinstance(d, Import)]

    # 2. Process each file and print
    for file_path in files_to_process:
        print(f"\n{'=' * 20} {file_path} {'=' * 20}")
        try:
            storage = JSONLStorage(file_path, type_definitions)
            items = storage.read()
            if not items:
                print("No data items found.")
                continue

            for item in items:
                if isinstance(item, Enumeration):
                    print(f"\n[Enum] {item.name}")
                    if item.description:
                        print(f"  Description: {item.description}")
                    print(f"  Values: {', '.join(item.values)}")
                elif isinstance(item, TypeDef):
                    print(f"\n[Type] {item.name}")
                    if item.extends:
                        print(f"  Extends: {item.extends}")
                    if item.description:
                        print(f"  Description: {item.description}")
                    print("  Properties:")
                    for prop in item.properties:
                        presence = (
                            "required" if prop.presence == "required" else "optional"
                        )
                        default = (
                            f", default: {prop.default}"
                            if prop.default is not None
                            else ""
                        )
                        print(f"    - {prop.name}: {prop.type} ({presence}{default})")
                elif isinstance(item, Module):
                    print(f"\n[Module] {item.name}")
                    if item.description:
                        print(f"  Description: {item.description}")
                    print(f"  Files: {', '.join(item.files)}")
                elif isinstance(item, Import):
                    print("\n[Import]")
                    if item.files:
                        print(f"  Files: {', '.join(item.files)}")
                    if item.modules:
                        print(f"  Modules: {', '.join(item.modules)}")
                else:
                    # Data instance
                    print(f"\n[{item.__class__.__name__}]")
                    for field_name in item.__class__.model_fields:
                        if field_name == "engn_type":
                            continue
                        val = getattr(item, field_name)
                        print(f"  {field_name}: {val}")
        except Exception as e:
            if verbose:
                import traceback

                traceback.print_exc()
            else:
                print(f"ERROR: {file_path} - {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Digital Engine - The Intelligent Engine for Building Systems"
    )
    parser.add_argument(
        "--version", action="store_true", help="Show the version and exit"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # proj command with subcommands
    proj_parser = subparsers.add_parser("proj", help="Project management commands")
    proj_subparsers = proj_parser.add_subparsers(dest="proj_command")

    # proj new <name>
    proj_new_parser = proj_subparsers.add_parser("new", help="Create a new project")
    proj_new_parser.add_argument("name", help="Name of the new project")

    # proj clone <url>
    proj_clone_parser = proj_subparsers.add_parser(
        "clone", help="Clone an existing project"
    )
    proj_clone_parser.add_argument("url", help="URL of the project to clone")
    proj_clone_parser.add_argument(
        "--name", help="Optional name for the project directory"
    )

    # proj delete <name>
    proj_delete_parser = proj_subparsers.add_parser("delete", help="Delete a project")
    proj_delete_parser.add_argument("name", help="Name of the project to delete")
    proj_delete_parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm deletion without prompting"
    )

    # proj init [path]
    proj_init_parser = proj_subparsers.add_parser(
        "init", help="Initialize a project structure in a directory"
    )
    proj_init_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path or name of project to initialize (default: current directory)",
    )

    # proj status <name>
    proj_status_parser = proj_subparsers.add_parser(
        "status", help="Show project status"
    )
    proj_status_parser.add_argument("name", help="Name of the project")

    # proj list
    proj_subparsers.add_parser("list", help="List all projects")

    # proj check
    proj_check_parser = proj_subparsers.add_parser(
        "check", help="Check validity of data files"
    )
    proj_check_parser.add_argument(
        "target",
        nargs="?",
        help="Path to JSONL file or directory to check (default: check all configured paths)",
    )
    proj_check_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed error traces",
    )

    # user command with subcommands
    user_parser = subparsers.add_parser("user", help="Manage users")
    user_subparsers = user_parser.add_subparsers(dest="user_command")

    # user add
    user_add_parser = user_subparsers.add_parser("add", help="Add a new user")
    user_add_parser.add_argument("--name", default="", help="Display name for the user")
    user_add_parser.add_argument(
        "--role",
        action="append",
        choices=[r.value for r in Role],
        help="Role to assign (can be specified multiple times)",
    )

    # user remove
    user_remove_parser = user_subparsers.add_parser("remove", help="Remove a user")
    user_remove_parser.add_argument("email", help="Email of the user to remove")

    # user add-role
    user_add_role_parser = user_subparsers.add_parser(
        "add-role", help="Add a role to a user"
    )
    user_add_role_parser.add_argument("email", help="Email of the user")
    user_add_role_parser.add_argument(
        "role", choices=[r.value for r in Role], help="Role to add"
    )

    # user remove-role
    user_remove_role_parser = user_subparsers.add_parser(
        "remove-role", help="Remove a role from a user"
    )
    user_remove_role_parser.add_argument("email", help="Email of the user")
    user_remove_role_parser.add_argument(
        "role", choices=[r.value for r in Role], help="Role to remove"
    )

    # user list (for convenience)
    user_subparsers.add_parser("list", help="List all users")

    # role command with subcommands
    role_parser = subparsers.add_parser("role", help="Manage roles")
    role_subparsers = role_parser.add_subparsers(dest="role_command")

    # role add
    role_add_parser = role_subparsers.add_parser("add", help="Add a new role")
    role_add_parser.add_argument("name", help="Name of the role to add")

    # role remove
    role_remove_parser = role_subparsers.add_parser("remove", help="Remove a role")
    role_remove_parser.add_argument("name", help="Name of the role to remove")

    # role list (for convenience)
    role_subparsers.add_parser("list", help="List all available roles")

    # data command with subcommands
    data_parser = subparsers.add_parser("data", help="Data management commands")
    data_subparsers = data_parser.add_subparsers(dest="data_command")

    # data check
    data_check_parser = data_subparsers.add_parser(
        "check", help="Check validity of data files"
    )
    data_check_parser.add_argument(
        "target",
        nargs="?",
        help="Path to JSONL file or directory to check (default: check all configured paths)",
    )
    data_check_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed error traces",
    )

    # data print
    data_print_parser = data_subparsers.add_parser(
        "print", help="Print enums, data types, and data in human-readable form"
    )
    data_print_parser.add_argument(
        "target",
        nargs="?",
        help="Path to JSONL file or directory to print (default: print all configured paths)",
    )
    data_print_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed error traces",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed error traces",
    )

    parser.add_argument(
        "-w",
        "--working-directory",
        default=".",
        help="The working directory for projects (default: current directory)",
    )

    args = parser.parse_args()

    # Load standard modules before processing commands
    load_standard_modules()

    if args.version:
        print(get_version())
        sys.exit(0)

    # Common argument handling
    working_dir = Path(args.working_directory).resolve()

    # Initialize auth config path
    from engn.core.auth import set_config_path

    set_config_path(working_dir / "engn.jsonl")

    if args.command == "proj":
        if args.proj_command == "new":
            try:
                project.create_new_project(args.name, working_dir)
                print(f"Created new project: {args.name}")
                sys.exit(0)
            except Exception as e:
                print_error(str(e), verbose=args.verbose)
                sys.exit(1)

        elif args.proj_command == "clone":
            try:
                project.clone_project(args.url, working_dir, args.name)
                print(f"Cloned project from {args.url}")
                sys.exit(0)
            except Exception as e:
                print_error(str(e), verbose=args.verbose)
                sys.exit(1)

        elif args.proj_command == "delete":
            if not args.yes:
                confirm = input(
                    f"Are you sure you want to delete project '{args.name}'? (y/N): "
                )
                if confirm.lower() != "y":
                    print("Deletion cancelled.")
                    sys.exit(0)

            if project.delete_project(args.name, working_dir):
                print(f"Deleted project: {args.name}")
                sys.exit(0)
            else:
                print_error(f"Project '{args.name}' not found.", verbose=args.verbose)
                sys.exit(1)

        elif args.proj_command == "init":
            # If path looks like a simple name, try resolving it in working_dir
            # Otherwise, resolve it relative to current working directory
            target_path = Path(args.path)
            if not target_path.is_absolute() and len(target_path.parts) == 1:
                target_path = working_dir / args.path
            else:
                target_path = Path.cwd() / args.path

            if not target_path.exists():
                print_error(
                    f"Directory '{target_path}' not found.", verbose=args.verbose
                )
                sys.exit(1)

            project.init_project_structure(target_path)
            print(f"Initialized engn project in {target_path}")
            sys.exit(0)

        elif args.proj_command == "list":
            projects = project.list_projects(working_dir)
            if not projects:
                print("No projects found.")
            else:
                for p in projects:
                    print(p)
            sys.exit(0)

        elif args.proj_command == "status":
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

        elif args.proj_command == "check":
            target = Path(args.target).resolve() if args.target else None
            run_check(target, working_dir, args.verbose)
            sys.exit(0)

        else:
            proj_parser.print_help()
            sys.exit(0)

    elif args.command == "user":
        if args.user_command == "add":
            # Prompt for email
            email = input("Email: ").strip()
            if not email:
                print("Error: Email cannot be empty.")
                sys.exit(1)

            # Check if user already exists
            if get_user_by_email(email):
                print(f"Error: User with email '{email}' already exists.")
                sys.exit(1)

            # Prompt for password with confirmation
            password = prompt_for_password()

            # Parse roles
            roles = [Role(r) for r in args.role] if args.role else [Role.USER]

            try:
                user = create_user(email, password, args.name, roles)
                print(f"Created user: {user.email}")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)

        elif args.user_command == "remove":
            if remove_user(args.email):
                print(f"Removed user: {args.email}")
                sys.exit(0)
            else:
                print(f"Error: User '{args.email}' not found.")
                sys.exit(1)

        elif args.user_command == "add-role":
            role = Role(args.role)
            if add_role_to_user(args.email, role):
                print(f"Added role '{role.value}' to user '{args.email}'.")
                sys.exit(0)
            else:
                print(f"Error: User '{args.email}' not found.")
                sys.exit(1)

        elif args.user_command == "remove-role":
            role = Role(args.role)
            if remove_role_from_user(args.email, role):
                print(f"Removed role '{role.value}' from user '{args.email}'.")
                sys.exit(0)
            else:
                print(f"Error: User '{args.email}' not found.")
                sys.exit(1)

        elif args.user_command == "list":
            users = list_users()
            if not users:
                print("No users found.")
            else:
                for u in users:
                    roles_str = ", ".join(r.value for r in u.roles)
                    print(f"{u.email} ({u.name or 'No name'}) - Roles: {roles_str}")
            sys.exit(0)

        else:
            user_parser.print_help()
            sys.exit(0)

    elif args.command == "role":
        if args.role_command == "add":
            print(
                f"Error: Cannot add role '{args.name}'. Roles are defined in the "
                "Role enum and require code changes to add new roles."
            )
            print(f"Available roles: {', '.join(r.value for r in Role)}")
            sys.exit(1)

        elif args.role_command == "remove":
            print(
                f"Error: Cannot remove role '{args.name}'. Roles are defined in the "
                "Role enum and require code changes to remove roles."
            )
            print(f"Available roles: {', '.join(r.value for r in Role)}")
            sys.exit(1)

        elif args.role_command == "list":
            print("Available roles:")
            for role in get_all_roles():
                print(f"  - {role.value}")
            sys.exit(0)

        else:
            role_parser.print_help()
            sys.exit(0)

    elif args.command == "data":
        if args.data_command == "check":
            target = Path(args.target).resolve() if args.target else None
            run_check(target, working_dir, args.verbose)
            sys.exit(0)
        elif args.data_command == "print":
            target = Path(args.target).resolve() if args.target else None
            run_print(target, working_dir, args.verbose)
            sys.exit(0)
        else:
            data_parser.print_help()
            sys.exit(0)

    else:
        # No command provided
        parser.print_help()


if __name__ == "__main__":
    main()
