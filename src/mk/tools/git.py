"""Expose features related to git repositories."""
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from mk.ctx import ctx
from mk.exec import fail, run_or_fail
from mk.tools import Action, Tool


class GitTool(Tool):
    name = "git"

    def __init__(self):
        super().__init__(self)

    def run(self, action: Optional[Action] = None) -> None:
        if action and action.name == "up":
            self.up()
        else:
            raise NotImplementedError(f"Action {action} is not supported.")

    def is_present(self, path: Path) -> bool:
        if not shutil.which("gh"):
            logging.warning("Unable to find gh tool. See https://cli.github.com/")
            return False
        return True

    def actions(self) -> List[Action]:
        actions: List[Action] = []
        if ctx.runner.branch not in ["main", "master"]:
            if self.is_present(self.path):
                actions.append(
                    Action(
                        name="up",
                        description="Upload current change by creating or updating a CR/PR.",
                        tool=self,
                    )
                )
        else:
            logging.info(
                "Not adding 'up' action as it does not work when current branch is main/master"
            )
        return actions

    # pylint: disable=too-many-branches
    def up(self):
        repo = ctx.runner.repo
        if not repo or repo.is_dirty():
            logging.fatal("This action cannot be performed with dirty repos.")
            sys.exit(2)
        if (ctx.runner.root / ".gitreview").is_file():
            cmd = ["git", "review"]
            run_or_fail(cmd, tee=True)
        else:
            active_branch = str(repo.active_branch)
            tracking_branch = str(repo.active_branch.tracking_branch())  # can be None
            if active_branch in ["main", "master"]:
                fail(
                    "Uploading from default branch is not allowed in order to avoid accidents.",
                    2,
                )

            remotes = {r.name for r in repo.remotes}
            if not {"origin", "upstream"}.issubset(remotes):
                logging.debug(
                    "Assuring you have two remotes, your fork as [blue]origin[/] and [blue]upstream[/]"
                )
                run_or_fail(["gh", "repo", "fork", "--remote=true"], tee=True)
                remotes = {r.name for r in repo.remotes}
            if "upstream" not in remotes:
                fail("Failed to create upstream")

            if tracking_branch is None:
                logging.debug("We do not have atracking branch")
            else:
                logging.debug("Performing a git push")

            logging.debug("Doing a git push")
            run_or_fail(
                ["git", "push", "--force-with-lease", "-u", "origin", "HEAD"], tee=False
            )

            # github for the moment
            # https://github.com/cli/cli/issues/1718

            # --web option is of not use because it happens too soon, confusing github
            logging.debug("Tryging to detect if there are existing PRs open")
            result = run_or_fail(
                ["gh", "pr", "list", "-S", f"head:{repo.active_branch}"]
            )
            if result.returncode == 0:
                pr_list = []
                if result.stdout:
                    for line in result.stdout.splitlines():
                        pr_list.append(line.split("\t")[0])
                if len(pr_list) == 0:
                    logging.debug("Existing PR not found, creating one.")
                    commit = repo.head.commit
                    title = commit.summary
                    body = "\n".join(commit.message.splitlines()[2:])
                    cmd = [
                        "gh",
                        "pr",
                        "create",
                        "--fill",
                        "--draft",
                        "--title",
                        title,
                        "--body",
                        body,
                    ]
                    result = run_or_fail(cmd, tee=True)
                    logging.debug(result.stdout)
                elif len(pr_list) == 1:
                    logging.debug(
                        "PR #%s already exists, no need to create new one.", pr_list[0]
                    )
                else:
                    logging.warning(
                        "Unable to decide which PR to use when multiple are found: %s",
                        pr_list,
                    )
