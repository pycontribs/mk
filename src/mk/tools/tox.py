"""Implementation of the tox tool support."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import tomllib

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class ToxTool(Tool):
    name = "tox"

    def is_present(self, path: Path) -> bool:
        pyproject = Path(path) / "pyproject.toml"
        if os.path.isfile(os.path.join(path, "tox.ini")):
            if not shutil.which("tox"):
                msg = "Tox config found but tox is not installed. Please install it with `uv pip install tox`."
                raise RuntimeError(msg)
            return True
        if pyproject.is_file():
            data = tomllib.loads(pyproject.read_text())
            if "tool" in data and "tox" in data["tool"]:
                return True
        return False

    def actions(self) -> list[Action]:
        actions: list[Action] = []
        result = run_or_fail(
            "uv tool run --with 'tox>=4.48.1' tox config --format=json --color=no -qq",
            tee=False,
        )
        data = json.loads(result.stdout)
        for name in data["env"]:
            description = data["env"][name].get("description", None)
            actions.append(Action(name=name, description=description, tool=self))
        return actions

    def run(self, action: Action | None = None) -> None:
        cmd = ["tox"] if not action else ["tox", "-e", action.name]
        run_or_fail(cmd, tee=True)
