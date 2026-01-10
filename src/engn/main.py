import argparse
import sys
from pathlib import Path
from engn.utils import get_version


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

    print(f"Initialized engn project in {target_path}")


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

    if args.command == "init":
        # Resolve the path relative to current working directory
        target_path = Path.cwd() / args.path
        init_project(target_path)
        sys.exit(0)

    print("Hello from engn!")


if __name__ == "__main__":
    main()
