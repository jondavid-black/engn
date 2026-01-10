import argparse
import sys
from engn.utils import get_version


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The Intelligent Engine for Building Systems"
    )
    parser.add_argument(
        "--version", action="store_true", help="Show the version and exit"
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

    print("Hello from engn!")


if __name__ == "__main__":
    main()
