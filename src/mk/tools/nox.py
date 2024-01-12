"""
Implementation of the nox tool support.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from packaging.version import Version

from mk.exec import run_or_fail
from mk.tools import Action, Tool

# This is the first version to support --json
_MINIMUM_NOX_VERSION = Version("2023.04.22")


class NoxTool(Tool):
    name = "nox"

    def is_present(self, path: Path) -> bool:
        return (path / "noxfile.py").is_file()

    def actions(self) -> list[Action]:
        actions: list[Action] = []
        version: str = run_or_fail(["nox", "--version"], tee=False).stderr.strip()
        if Version(version) < _MINIMUM_NOX_VERSION:
            logging.warning(
                "Failed to retrieve nox sessions: "
                "nox version %s is too old. Minimum supported version is %s.",
                version,
                _MINIMUM_NOX_VERSION,
            )
            return []
        results = run_or_fail(["nox", "--list", "--json"], tee=False)
        data = json.loads(results.stdout)
        actions = [
            Action(session["session"], tool=self, description=session["description"])
            for session in data
        ]
        return actions

    def run(self, action: Action | None = None) -> None:
        cmd = ["nox"] if not action else ["nox", "-s", action.name]
        run_or_fail(cmd, tee=True)
