from __future__ import annotations

import json
import logging
import os
import shutil
import sys
from pathlib import Path

from mk.exec import run_or_fail
from mk.tools import Action, Tool


class TaskfileTool(Tool):
    name = "taskfile"

    def __init__(self, path: str = ".") -> None:
        """Initialize."""
        super().__init__(path)
        self.executable = ""

    def is_present(self, path: Path) -> bool:
        valid_taskfiles = [
            "Taskfile.yml",
            "taskfile.yml",
            "Taskfile.yaml",
            "taskfile.yaml",
            "Taskfile.dist.yml",
            "taskfile.dist.yml",
            "Taskfile.dist.yaml",
            "taskfile.dist.yaml",
        ]

        for taskfile in valid_taskfiles:
            if os.path.isfile(os.path.join(path, taskfile)):
                # On some Linux distros might be exposed as taskfile in order to
                # avoid clashing with the other Task Warrior executable https://taskwarrior.org/
                self.executable = shutil.which(taskfile) or shutil.which("task") or ""
                if not self.executable:
                    logging.error(
                        "%s config found but the tool is not installed. See https://taskfile.dev/installation/",
                        taskfile,
                    )
                    sys.exit(1)
                return True
        return False

    def actions(self) -> list[Action]:
        actions: list[Action] = []
        tasks_json = (
            run_or_fail(
                ["task", "--list", "--json"],
                tee=False,
            ).stdout
            or ""
        )
        for task in json.loads(tasks_json)["tasks"]:
            desc = task["desc"]
            if task["summary"]:
                desc += "\n"
                desc += task["summary"]
            actions.append(
                Action(
                    name=task["name"],
                    tool=self,
                    description=desc,
                    args=[task["name"]],
                ),
            )
        return actions

    def run(self, action: Action | None = None) -> None:
        cmd = ["task"] if not action else ["task", action.name]
        run_or_fail(cmd, tee=True)
