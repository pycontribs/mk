import os
import sys
from typing import List, Optional

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class PyTestTool(Tool):
    """Expose test command if pytest config is detected."""

    name = "pytest"

    def __init__(self) -> None:
        super().__init__(self)

    def run(self, action: Optional[Action] = None) -> None:
        if not action:
            return
        if action.name == "test":
            cmd = [sys.executable, "-m", "pytest"]
            run_or_fail(cmd, tee=True)

    def is_present(self, path: str) -> bool:
        for name in ("pytest.ini",):
            if os.path.isfile(name):
                return True
        return False

    def actions(self) -> List[Action]:
        actions = []
        actions.append(
            Action(
                name="test",
                tool=self,
                description="Run pytest",
            )
        )

        return actions
