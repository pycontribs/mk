import logging
import sys
from pathlib import Path
from typing import List, Optional

from mk.exec import run_or_fail
from mk.loaders import load_toml
from mk.tools import Action, Tool


class PyPackageTool(Tool):
    """Expose build, install and uninstall commands for python packages."""

    name = "pip"

    def __init__(self) -> None:
        super().__init__(self)
        self.pkg_name = ""

    def run(self, action: Optional[Action] = None) -> None:
        if not action:
            return
        if action.name in ["build", "install", "uninstall"]:
            cmd = action.args
            run_or_fail(cmd, tee=True)
            run_or_fail(f"{sys.executable} -m twine check dist/*", tee=True)
        else:
            raise NotImplementedError(f"Action {action.name} not implemented")

    def is_present(self, path: Path) -> bool:
        data = load_toml(path / "pyproject.toml")
        self.pkg_name = (
            data.get("project", {}).get("name", "")
            or data.get("tool", {})
            .get("flit", {})
            .get("metadata", {})
            .get("module", "")
            or data.get("tool", {}).get("poetry", {}).get("name", "")
        )
        if not self.pkg_name:
            if (path / "setup.py").exists():
                self.pkg_name = run_or_fail(
                    [sys.executable, "setup.py", "--name"], tee=False
                ).stdout.strip()
                return True
            if (path / "setup.cfg").exists():
                return True
            return False
        return True

    def actions(self) -> List[Action]:
        actions: List[Action] = []
        if not self.is_present(Path(".")):
            return actions

        actions.append(
            Action(
                name="install",
                tool=self,
                description="Use pip to install the current package for current user.",
                args=["pip3", "install", "-e", "."],
            )
        )
        if self.pkg_name:
            actions.append(
                Action(
                    name="uninstall",
                    tool=self,
                    description="Use pip to uninstall the current package.",
                    args=["pip3", "uninstall", self.pkg_name],
                )
            )
        try:
            # pylint: disable=import-outside-toplevel,unused-import
            import build  # noqa: F401

            actions.append(
                Action(
                    name="build",
                    tool=self,
                    description="Use python build to produce sdist and wheel, followed by twine check",
                    args=[
                        "python3",
                        "-m",
                        "build",
                        "--sdist",
                        "--wheel",
                        "--outdir",
                        "dist",
                    ],
                )
            )
        except ImportError:
            logging.warning(
                "Python 'build' package not found, unable to provide build action."
            )

        return actions
