from importlib.metadata import version, PackageNotFoundError


def get_version() -> str:
    try:
        return version("engn")
    except PackageNotFoundError:
        return "Unknown (package not installed)"
