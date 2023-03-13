"""Wrappers for loading different configuration files."""
from pathlib import Path

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore


def load_toml(file: Path) -> dict:
    """Load a TOML file if exists or return empty dictionary."""
    if file.is_file():
        with open(file, "rb") as handle:
            return tomllib.load(handle)
    return {}
