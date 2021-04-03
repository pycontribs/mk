import logging
import subprocess
import sys
from pathlib import Path
from typing import List

import git

from mk.tools import Action, Tool


class Runner:
    def __init__(self) -> None:
        self.repo = git.Repo(".", search_parent_directories=True)
        self.root = Path(self.repo.working_dir)
        self.actions: List[Action] = []

        for c in Tool:
            if c.is_present(self.root):
                logging.info("Detected %s !", c)
                self.actions.extend(c.actions())
            else:
                logging.debug("%s not detected !", c)

        if self.repo.is_dirty():
            logging.warning("Repo is dirty on %s", self.repo.active_branch)

    def info(self) -> None:
        logging.info("Actions identified: %s", self.actions)

    def up(self):
        if self.repo.is_dirty():
            sys.exit(2)
        if (self.root / ".git-review").is_file():
            cmd = ["git", "review"]
        else:
            if self.repo.active_branch in ["main", "master"]:
                fail(
                    "Uploading from default branche is not allowed in order to avoid accidents.", 2
                )
            run(["git", "push", "--force-with-lease", "-u", "origin", "HEAD"])
            # github for the moment
            # https://github.com/cli/cli/issues/1718

            # --web option is of not use because it happens to soon, confusing github
            cmd = ["gh", "pr", "create", "--fill"]  # {self.repo.active_branch}
        run(cmd)


def fail(msg: str, code=1) -> None:
    logging.error(msg)
    sys.exit(code)


def run(*args) -> None:
    result = subprocess.run(*args, check=False)
    if result.returncode != 0:
        fail(
            f"Received exit code {result.returncode} from: {' '.join(result.args)}",
            code=result.returncode,
        )