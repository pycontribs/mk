import os
from pathlib import Path
from typing import List, Optional

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class PreCommitTool(Tool):
    name = "pre-commit"

    def run(self, action: Optional[Action] = None):
        run_or_fail(["pre-commit", "run", "-a"], tee=True)

    def is_present(self, path: Path) -> bool:
        if os.path.isfile(os.path.join(path, ".pre-commit-config.yaml")):
            return True
        return False

    def actions(self) -> List[Action]:
        return [
            Action(name="lint", description="[dim]pre-commit run -a[/dim]", tool=self)
        ]
