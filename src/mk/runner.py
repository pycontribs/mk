import logging
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from mk.tools import Action

import pluggy
from diskcache import Cache
from git import Repo
from git.exc import GitError


class Runner:
    def __init__(self) -> None:
        self.root: Optional[Path] = None
        try:
            self.repo = Repo(".", search_parent_directories=True)
        except GitError:
            logging.fatal("Current version of mk works only within git repos.")
            self.repo = None
            return

        self.root = Path(self.repo.working_dir)
        self.cache = Cache(self.root / ".cache/mk/")

        if self.repo.is_dirty():
            logging.warning("Repo is dirty on %s", self.repo.active_branch)

    @cached_property
    def pm(self):
        """Plugin manager."""
        pm = pluggy.PluginManager("mk_tools")
        pm.load_setuptools_entrypoints("mk_tools")
        return pm

    @cached_property
    def actions(self) -> List["Action"]:
        """List of discovered actions."""
        if not self.root:
            return []

        _actions: List["Action"] = self.cache.get("actions", [])

        if not _actions:
            for _, cls_name in self.pm.list_name_plugin():
                # for c in Tool:
                c = cls_name()
                if c.is_present(self.root):
                    logging.debug("Detected %s !", c)
                    _actions.extend(c.actions())
                else:
                    logging.debug("%s not detected !", c)

        _actions.sort()
        self.cache.set("actions", _actions, expire=3600 * 24)

        return _actions

    def info(self) -> None:
        logging.info("Actions identified: %s", self.actions)
