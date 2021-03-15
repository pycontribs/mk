import logging
import git
from mk.tools import Tool


class Runner:
    def __init__(self):
        self.repo = git.Repo(".", search_parent_directories=True)
        self.root = self.repo.working_dir
        for c in Tool:
            if c.is_present(self.root):
                logging.info(f"Detected {c} !")
            else:
                logging.debug(f"{c} not detected !")
