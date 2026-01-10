import argparse
import sys
from pathlib import Path

import flet as ft
from engn.utils import get_version


def flet_main(page: ft.Page):
    page.title = "ProjEngn"
    page.theme_mode = ft.ThemeMode.DARK
    page.add(ft.Text("Welcome to ProjEngn - Program Management Tool"))


def main() -> None:
    parser = argparse.ArgumentParser(description="ProjEngn - Program Management Tool")
    parser.add_argument(
        "--version", action="store_true", help="Show the version and exit"
    )
    parser.add_argument(
        "-w",
        "--working-directory",
        default=".",
        help="The working directory for projects (default: current directory)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    subparsers.add_parser("serve", help="Serve the application as a web app")

    args = parser.parse_args()

    if args.version:
        print(get_version())
        sys.exit(0)

    if args.command == "serve":
        ft.app(
            target=flet_main,
            view=ft.AppView.WEB_BROWSER,
            assets_dir=str(Path(__file__).parent.parent / "engn" / "assets"),
        )
    else:
        ft.app(
            target=flet_main,
            assets_dir=str(Path(__file__).parent.parent / "engn" / "assets"),
        )


if __name__ == "__main__":
    main()
