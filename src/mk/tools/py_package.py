import os
import sys
from typing import List, Optional

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class PyPackageTool(Tool):
    """Expose build, install and uninstall commands for python packages."""

    name = "pip"

    def __init__(self) -> None:
        super().__init__(self)

    def run(self, action: Optional[Action] = None) -> None:
        if not action:
            return
        if action.name == "build":
            cmd = [sys.executable, "-m", "build", "--sdist", "--wheel", "--outdir", "dist"]
            run_or_fail(cmd, tee=True)
            run_or_fail(f"{sys.executable} -m twine check dist/*", tee=True)
        elif action.name == "install":
            cmd = [sys.executable, "-m", "pip", action.name, "-e", "."]
            run_or_fail(cmd, tee=True)
        elif action.name == "uninstall":
            pkg_name = run_or_fail([sys.executable, "setup.py", "--name"], tee=False).stdout
            cmd = [sys.executable, "-m", "pip", action.name, "-y", pkg_name]
            run_or_fail(cmd, tee=True)

    def is_present(self, path: str) -> bool:
        for name in ("setup.cfg", "setup.py", "pyproject.toml"):
            if os.path.isfile(name):
                return True
        return False

    def actions(self) -> List[Action]:
        actions = []

        for name in ("install", "uninstall"):
            description = f"Use pip to {name} current package"
            actions.append(Action(name=name, tool=self, description=description))
        actions.append(
            Action(
                name="build",
                tool=self,
                description="Use python build to produce sdist and wheel, followed by twine check",
            )
        )

        return actions
