import logging
import subprocess
import sys
from pathlib import Path
from typing import List

import pluggy
from git import Repo
from git.exc import GitError

from mk.tools import Action
from mk.tools.git import GitTool


class Runner:
    def __init__(self) -> None:
        self.actions: List[Action] = []
        try:
            self.repo = Repo(".", search_parent_directories=True)
        except GitError:
            logging.fatal("Current version of mk works only within git repos.")
            self.repo = None
            return

        self.root = Path(self.repo.working_dir)

        self.pm = pluggy.PluginManager("mk_tools")
        self.pm.load_setuptools_entrypoints("mk_tools")
        for _, cls_name in self.pm.list_name_plugin():
            # for c in Tool:
            c = cls_name()
            if c.is_present(self.root):
                logging.debug("Detected %s !", c)
                self.actions.extend(c.actions())
            else:
                logging.debug("%s not detected !", c)

        if self.repo.is_dirty():
            logging.warning("Repo is dirty on %s", self.repo.active_branch)

        # expos up command
        self.actions.append(
            Action(
                name="up",
                description="Upload current change by creating or updating a CR/PR.",
                tool=GitTool(),
                runner=self,
            )
        )

    def info(self) -> None:
        logging.info("Actions identified: %s", self.actions)


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
