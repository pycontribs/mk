import os
import subprocess
from typing import List, Optional

from mk.tools import Action, Tool


class PreCommitTool(Tool):
    name = "pre-commit"

    def run(self, action: Optional[Action] = None):
        subprocess.run(["pre-commit", "run", "-a"], check=True)

    def is_present(self, path: str) -> bool:
        if os.path.isfile(os.path.join(path, ".pre-commit-config.yaml")):
            return True
        return False

    def actions(self) -> List[Action]:
        return [Action(name="lint", tool=self)]
