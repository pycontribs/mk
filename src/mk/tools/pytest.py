import os
import sys
from pathlib import Path
from typing import List, Optional

from mk.exec import run_or_fail
from mk.loaders import load_toml
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
        return

    def is_present(self, path: Path) -> bool:
        if os.path.isfile(path / "pytest.ini"):
            return True
        data = load_toml(path / "pyproject.toml")
        if data and data.get("tool", {}).get("pytest"):
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
