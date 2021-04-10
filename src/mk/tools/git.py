import logging
import subprocess
import sys
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

    # pylint: disable=too-many-branches
    def up(self, runner):
        if not runner.repo or runner.repo.is_dirty():
            logging.fatal("This action cannot be performed with dirty repos.")
            sys.exit(2)
        if (runner.root / ".gitreview").is_file():
            cmd = ["git", "review"]
            run(cmd)
        else:
            active_branch = str(runner.repo.active_branch)
            tracking_branch = str(runner.repo.active_branch.tracking_branch())  # can be None
            if active_branch in ["main", "master"]:
                fail(
                    "Uploading from default branch is not allowed in order to avoid accidents.", 2
                )

            remotes = {r.name for r in runner.repo.remotes}
            if not {"origin", "upstream"}.issubset(remotes):
                logging.debug(
                    "Assuring you have two remotes, your fork as [blue]origin[/] and [blue]upstream[/]"
                )
                run(["gh", "repo", "fork", "--remote=true"])
                remotes = {r.name for r in runner.repo.remotes}
            if "upstream" not in remotes:
                fail("Failed to create upstream")

            if tracking_branch is None:
                logging.debug("We do not have atracking branch")
            else:
                logging.debug("Performing a git push")

            logging.debug("Doing a git push")
            run(["git", "push", "--force-with-lease", "-u", "origin", "HEAD"])

            # github for the moment
            # https://github.com/cli/cli/issues/1718

            # --web option is of not use because it happens too soon, confusing github
            logging.debug("Tryging to detect if there are existing PRs open")
            result = subprocess.run(
                ["gh", "pr", "list", "-S", f"head:{runner.repo.active_branch}"],
                check=False,
                stdin=subprocess.DEVNULL,
                universal_newlines=True,
                capture_output=True,
            )
            if result.returncode == 0:
                pr_list = []
                for line in result.stdout.splitlines():
                    pr_list.append(line.split("\t")[0])
                if len(pr_list) == 0:
                    logging.debug("Existing PR not found, creating one.")
                    commit = runner.repo.head.commit
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
                    result = run(cmd)
                    logging.debug(result.stdout)
                elif len(pr_list) == 1:
                    logging.debug("PR #%s already exists, no need to create new one.", pr_list[0])
                else:
                    logging.warning(
                        "Unable to decide which PR to use when multiple are found: %s", pr_list
                    )
