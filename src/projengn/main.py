import argparse
import sys
import flet as ft
from engn.utils import get_version


def flet_main(page: ft.Page):
    page.title = "ProjEngn"
    page.add(ft.Text("Welcome to ProjEngn - Program Management Tool"))


def main() -> None:
    parser = argparse.ArgumentParser(description="ProjEngn - Program Management Tool")
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
