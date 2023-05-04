from __future__ import annotations

import os
from pathlib import Path

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class PreCommitTool(Tool):
    name = "pre-commit"

    def run(self, action: Action | None = None):
        run_or_fail(["pre-commit", "run", "-a"], tee=True)

    def is_present(self, path: Path) -> bool:
        if os.path.isfile(os.path.join(path, ".pre-commit-config.yaml")):
            return True
        return False

    def actions(self) -> list[Action]:
        return [
            Action(name="lint", description="[dim]pre-commit run -a[/dim]", tool=self),
        ]
