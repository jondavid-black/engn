import argparse
import sys
import flet as ft
from engn.utils import get_version


def flet_main(page: ft.Page):
    page.title = "SysEngn"
    page.add(ft.Text("Welcome to SysEngn - Model-Based System Engineering"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SysEngn - Model-Based System Engineering Tool"
    )
    parser.add_argument(
        "--version", action="store_true", help="Show the version and exit"
    )

    args = parser.parse_args()

    if args.version:
        print(get_version())
        sys.exit(0)

    ft.app(target=flet_main)


if __name__ == "__main__":
    main()
