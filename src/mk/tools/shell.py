import glob
import os
from typing import List, Optional

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class ShellTool(Tool):
    name = "shell"

    def run(self, action: Optional[Action] = None) -> None:
        if action and action.filename:
            run_or_fail(action.filename, tee=True)

    def is_present(self, path: str) -> bool:
        return True

    def actions(self) -> List[Action]:
        actions: List[Action] = []
        exclude_list = ["setup.py"]
        for filename in [
            *glob.glob("*"),
            *glob.glob("tools/*.*"),
            *glob.glob("bin/*.*"),
            *glob.glob("scripts/*.*"),
        ]:
            if (
                os.path.isfile(filename)
                and os.access(filename, os.X_OK)
                and filename not in exclude_list
            ):
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
