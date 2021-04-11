import logging
from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from mk.tools import Action

import pluggy
from git import Repo
from git.exc import GitError


class Runner:
    def __init__(self) -> None:
        self.actions: List["Action"] = []
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

        self.actions.sort()

    def info(self) -> None:
        logging.info("Actions identified: %s", self.actions)
