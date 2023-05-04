from __future__ import annotations

import glob
import os
from pathlib import Path

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class AnsibleTool(Tool):
    name = "ansible"

    def run(self, action: Action | None = None):
        if action and action.filename:
            run_or_fail(
                ["ansible-playbook", "-vv", action.filename],
                tee=True,
                env_overrides={"ANSIBLE_FORCE_COLOR": "1"},
            )

    def is_present(self, path: Path) -> bool:
        if os.path.isdir(os.path.join(path, "playbooks")):
            return True
        return False

    def actions(self) -> list[Action]:
        actions: list[Action] = []
        for filename in glob.glob("playbooks/*.yml"):
            name = os.path.splitext(os.path.basename(filename))[0]
            actions.append(
                Action(
                    name=name,
                    description=f"[dim]ansible-playbook {filename}[/dim]",
                    tool=self,
                    filename=filename,
                ),
            )
        return actions
