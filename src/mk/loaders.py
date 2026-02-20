"""Wrappers for loading different configuration files."""

from pathlib import Path
from typing import Any

import tomllib


def load_toml(file: Path) -> dict[Any, Any]:
    """Load a TOML file if exists or return empty dictionary.

    Returns:
        dict: The loaded TOML data.

    Raises:
        TypeError: If the loaded data is not a dictionary.
    """
    if file.is_file():
        with open(file, "rb") as handle:
            result = tomllib.load(handle)
            if not isinstance(result, dict):
                msg = f"Expected dict, got {type(result)}"
                raise TypeError(msg)
            return result
    return {}
