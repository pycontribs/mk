from __future__ import annotations

import os
import re
from pathlib import Path

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class JustTool(Tool):
    name = "just"

    def __init__(self) -> None:
        super().__init__(self)
        self.justfile: str | None = None

    def run(self, action: Action | None = None) -> None:
        cmd = ["just"]
        if action:
            cmd.append(action.name)
        run_or_fail(cmd, tee=True)

    def is_present(self, path: Path) -> bool:
        for name in ["Justfile", "justfile", "JUSTFILE", ".justfile"]:
            justfile = os.path.join(path, name)
            if os.path.isfile(justfile):
                self.justfile = justfile
                return True
        return False

    def actions(self) -> list[Action]:
        actions = []
        if not self.justfile:
            msg = "Justfile not found"
            raise RuntimeError(msg)
        # pylint: disable=duplicate-code
        with open(self.justfile, encoding="utf-8") as file:
            for line in file.readlines():
                # Current implementation assumes that descriptions are added
                # using double ## after the target name.
                # Inspired by https://github.com/containers/podman/blob/master/Makefile#L127
                match = re.match(r"^([a-zA-Z_-]+):.*?## (.*)$$", line)
                if match:
                    target, description = match.groups()
                    actions.append(
                        Action(name=target, tool=self, description=description),
                    )
        # pylint: enable=duplicate-code
        return actions
