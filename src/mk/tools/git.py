import logging
import os
import re
import sys
import subprocess
from typing import List, Optional

from mk.exec import run, fail
from mk.tools import Action, Tool


class GitTool(Tool):
    name = "git"

    def __init__(self):
        super().__init__(self)

    def run(self, action: Optional[Action] = None) -> None:
        if action and action.name == 'up' and action.runner:
            self.up(runner=action.runner)
        else:
            raise NotImplementedError(f"Action {action} is not supported.")

    def is_present(self, path: str) -> bool:
        return True

    def actions(self) -> List[Action]:
        actions: List[Action] = []
        return actions

    def up(self, runner):
        if not runner.repo or runner.repo.is_dirty():
            logging.fatal("This action cannot be performed with dirty repos.")
            sys.exit(2)
        if (runner.root / ".gitreview").is_file():
            cmd = ["git", "review"]
        else:
            if runner.repo.active_branch in ["main", "master"]:
                fail(
                    "Uploading from default branch is not allowed in order to avoid accidents.", 2
                )
            run(["git", "push", "--force-with-lease", "-u", "origin", "HEAD"])
            # github for the moment
            # https://github.com/cli/cli/issues/1718

            # --web option is of not use because it happens to soon, confusing github
            cmd = ["gh", "pr", "create", "--fill"]  # {self.repo.active_branch}
        run(cmd)
