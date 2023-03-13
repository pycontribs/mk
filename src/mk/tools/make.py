import os
import re
from pathlib import Path
from typing import List, Optional

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class MakeTool(Tool):
    name = "make"

    def __init__(self):
        super().__init__(self)
        self.makefile = None

    def run(self, action: Optional[Action] = None) -> None:
        cmd = ["make"]
        if action:
            cmd.append(action.name)
        run_or_fail(cmd, tee=True)

    def is_present(self, path: Path) -> bool:
        for name in ["Makefile", "makefile", "GNUmakefile"]:
            makefile = os.path.join(path, name)
            if os.path.isfile(makefile):
                self.makefile = makefile
                return True
        return False

    def actions(self) -> List[Action]:
        actions = []

        with open(self.makefile, "r", encoding="utf-8") as file:
            for line in file.readlines():
                # Current implementation assumes that descriptions are added
                # using double ## after the target name.
                # Inspired by https://github.com/containers/podman/blob/master/Makefile#L127
                match = re.match(r"^([a-zA-Z_-]+):.*?## (.*)$$", line)
                if match:
                    target, description = match.groups()
                    actions.append(
                        Action(name=target, tool=self, description=description)
                    )
        return actions
