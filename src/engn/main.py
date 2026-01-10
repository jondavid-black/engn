import argparse
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List

from pydantic import ValidationError

from engn.utils import get_version
from engn.config import ProjectConfig
from engn.data.storage import EngnDataModel


def init_project(target_path: Path) -> None:
    """Initialize a new engn project structure."""
    if not target_path.exists():
        target_path.mkdir(parents=True)

    # Create directories
    for dir_name in ["arch", "pm", "ux"]:
        (target_path / dir_name).mkdir(exist_ok=True)

    # Create engn.toml
    config_path = target_path / "engn.toml"
    with open(config_path, "w") as f:
        f.write('arch_path = "arch"\n')
        f.write('pm_path = "pm"\n')
        f.write('ux_path = "ux"\n')

    # Initialize beads if installed
    if shutil.which("bd"):
        subprocess.run(["bd", "init"], cwd=target_path, check=True)
        print("Initialized beads for issue tracking")
    else:
        print("Warning: 'bd' (beads) not found. Issue tracking not initialized.")

    print(f"Initialized engn project in {target_path}")


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

    # Init command
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

    if args.command == "init":
        # Resolve the path relative to current working directory
        target_path = Path.cwd() / args.path
        init_project(target_path)
        sys.exit(0)

    if args.command == "check":
        target = Path(args.target).resolve() if args.target else None
        run_check(target, working_dir)
        sys.exit(0)

    # No command provided
    parser.print_help()


if __name__ == "__main__":
    main()
