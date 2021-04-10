import logging
import os
import re
import sys
import subprocess
from typing import List, Optional

from mk.exec import fail, run
from mk.tools import Action, Tool


class GitTool(Tool):
    name = "git"

    def __init__(self):
        super().__init__(self)

    def run(self, action: Optional[Action] = None) -> None:
        if action and action.name == "up" and action.runner:
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
            run(cmd)
        else:
            if runner.repo.active_branch in ["main", "master"]:
                fail(
                    "Uploading from default branch is not allowed in order to avoid accidents.", 2
                )
            run(["git", "push", "--force-with-lease", "-u", "origin", "HEAD"])
            # github for the moment
            # https://github.com/cli/cli/issues/1718

            # --web option is of not use because it happens to soon, confusing github
            # environ={'PAGER': 'cat'}
            logging.debug("Tryging to detect if there are existing PRs open")
            os.environ['GITPAGER'] = 'cat'
            result = subprocess.run(
                ["gh", "pr", "list", "-S", f"head:{runner.repo.active_branch}"],
                check=False,
                stdin=subprocess.DEVNULL,
                env=os.environ,
                universal_newlines=True,
                capture_output=True)
            if result.returncode == 0:
                print(result)
                pr_list = []
                for line in result.stdout.splitlines():
                    pr_list.append(line.split('\t')[0])
                if len(pr_list) == 0:
                    logging.debug("Existing PR not found, creating one.")
                    cmd = ["gh", "pr", "create", "--fill"]  # {self.repo.active_branch}
                    run(cmd, environ={'PAGER': 'cat'})
                elif len(pr_list) == 1:
                    logging.debug("PR#%s already exists, no need to update.", pr_list[0])
                else:
                    logging.warning("Unable to decide which PR to use when multiple are found: %s", pr_list)
