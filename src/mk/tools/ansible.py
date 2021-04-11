import glob
import os
from typing import List, Optional

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class AnsibleTool(Tool):
    name = "ansible"

    def run(self, action: Optional[Action] = None):
        if action and action.filename:
            run_or_fail(["ansible-playbook", action.filename], tee=True)

    def is_present(self, path: str) -> bool:
        if os.path.isdir(os.path.join(path, "playbooks")):
            return True
        return False

    def actions(self) -> List[Action]:
        actions: List[Action] = []
        for filename in glob.glob("playbooks/*.yml"):
            name = os.path.splitext(os.path.basename(filename))[0]
            actions.append(
                Action(
                    name=name,
                    description="Run ansible-playbook %s" % filename,
                    tool=self,
                    filename=filename,
                )
            )
        return actions
