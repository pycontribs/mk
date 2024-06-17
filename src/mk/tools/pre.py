from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from mk.exec import run_or_fail
from mk.pre import CFG_FILE
from mk.tools import Action, Tool


class PreTool(Tool):
    name = "pre"

    def run(self, action: Action | None = None):
        if action:
            run_or_fail(["pre", action.name], tee=True)

    def is_present(self, path: Path) -> bool:
        if not os.path.exists(os.path.expanduser(CFG_FILE)):
            msg = f"Multi-repo feature was disabled because {CFG_FILE} was not found."
            logging.debug(msg)
            return False
        if not shutil.which("gh"):
            logging.warning("Unable to find gh tool. See https://cli.github.com/")
            return False
        return True

    def actions(self) -> list[Action]:
        # for command in app.registered_commands:
        #     print(command.name, command.short_help, command.short_help, command.epilog, command.short_help)
        # breakpoint()
        return [
            Action(name="prs", description="[dim]Show open PRs[/dim]", tool=self),
            Action(
                name="drafts",
                description="[dim]Show draft releases[/dim]",
                tool=self,
            ),
            Action(
                name="alerts",
                description="[dim]Show dependabot security alerts[/dim]",
                tool=self,
            ),
        ]
