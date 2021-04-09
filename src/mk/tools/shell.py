import glob
import os
import subprocess
from typing import List, Optional

from mk.tools import Action, Tool


class ShellTool(Tool):
    name = "shell"

    def run(self, action: Optional[Action] = None) -> None:
        if action and action.filename:
            subprocess.run([action.filename], check=True)

    def is_present(self, path: str) -> bool:
        if os.path.isdir(os.path.join(path, "tools")):
            return True
        return False

    def actions(self) -> List[Action]:
        actions: List[Action] = []
        for filename in glob.glob("tools/*.*"):
            if os.access(filename, os.X_OK):
                name = os.path.splitext(os.path.basename(filename))[0]
                actions.append(
                    Action(
                        name=name,
                        description="Run %s" % filename,
                        tool=self,
                        filename=filename,
                    )
                )
        return actions
