import os
import re
import subprocess
from typing import List, Optional

from mk.tools import Action, Tool


class MakeTool(Tool):
    name = "make"

    def run(self, action: Optional[Action] = None) -> None:
        cmd = ["make"]
        if action:
            cmd.append(action.name)
        subprocess.run(cmd, check=True)

    def is_present(self, path: str) -> bool:
        if os.path.isfile(os.path.join(path, "Makefile")):
            return True
        return False

    def actions(self) -> List[Action]:
        actions = []

        with open("Makefile", "r") as file:
            for line in file.readlines():
                # Current implementation assumes that descriptions are added
                # using double ## after the target name.
                # Inspired by https://github.com/containers/podman/blob/master/Makefile#L127
                match = re.match(r"^([a-zA-Z_-]+):.*?## (.*)$$", line)
                if match:
                    target, description = match.groups()
                    actions.append(Action(name=target, tool=self, description=description))
        return actions
