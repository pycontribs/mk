from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class CMakeTool(Tool):
    name = "cmake"

    def __init__(self) -> None:
        super().__init__()
        self.configfile: str | None = None
        self._is_present: bool | None = None

    def run(self, action: Action | None = None) -> None:
        cmd = ["cmake"]
        if action:
            cmd.append(action.name)
        run_or_fail(cmd, tee=True)

    def is_present(self, path: Path) -> bool:
        if self._is_present is not None:
            return self._is_present
        self._is_present = False
        for name in ["CMakeLists.txt"]:
            configfile = os.path.join(path, name)
            if os.path.isfile(configfile):
                self.configfile = configfile
                if not shutil.which("cmake"):
                    logging.warning(
                        "Unable to find cmake tool. See https://cmake.org/download/",
                    )
                    self._is_present = False
                    break
                logging.warning(
                    "cmake is not fully supported yet by mk. See https://github.com/pycontribs/mk/issues/135",
                )
                self._is_present = True
                break
        return bool(self._is_present)

    def actions(self) -> list[Action]:
        actions = []
        if self.is_present(Path(".")):
            actions.append(Action(name=".", tool=self, description="Run 'cmake .'"))
        return actions
