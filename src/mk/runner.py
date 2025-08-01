from __future__ import annotations

import hashlib
import logging
import sys

from mk.tools import Tool

try:
    from functools import cached_property
except ImportError:
    from cached_property import cached_property  # type: ignore

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mk.tools import Action

import pluggy
from diskcache import Cache
from git import Repo
from git.exc import GitError


class Runner:
    def __init__(self) -> None:
        self.root: Path | None = None
        try:
            self.repo = Repo(".", search_parent_directories=True)
        except GitError as exc:
            msg = "Current version of mk works only within git repos."
            logging.fatal(msg)
            raise RuntimeError(msg) from exc
        self.branch = ""
        if self.repo:
            try:
                self.branch = self.repo.active_branch.name
                logging.info("Detected active branch '%s'", self.branch)
            except TypeError:
                logging.warning("No branch detected.")

        self.root = Path(self.repo.working_dir)
        hash_key = f"{sys.version_info.major}{sys.version_info.minor}{self.root}"
        self.hash = hashlib.sha256(hash_key.encode("UTF-8")).hexdigest()[:5]
        self.cache = Cache(f"~/.cache/mk.{self.hash}/")

        if self.repo.is_dirty():
            logging.warning("Repo is dirty on %s", self.repo.active_branch)

    @cached_property
    def pm(self) -> pluggy.PluginManager:
        """Plugin manager."""
        pm = pluggy.PluginManager("mk_tools")
        pm.load_setuptools_entrypoints("mk_tools")
        return pm

    @cached_property
    def actions(self) -> list[Action]:
        """List of discovered actions."""
        if not self.root:
            return []

        result: list[Action] = []
        value = self.pm.list_name_plugin()  # pyright: ignore[reportAttributeAccessIssue]
        for _, cls_name in value:
            if not callable(cls_name):
                msg = f"Invalid plugin: {cls_name}"
                raise TypeError(msg)
            c = cls_name()
            if not isinstance(c, Tool):
                msg = f"Invalid plugin: {c}"
                raise TypeError(msg)
            if c.is_present(self.root):
                logging.debug("Detected %s !", c)
                result.extend(c.actions())
            else:
                logging.debug("%s not detected !", c)

        result.sort()
        self.cache.set("actions", result, expire=3600 * 24)

        return result

    def info(self) -> None:
        logging.info("Actions identified: %s", self.actions)
