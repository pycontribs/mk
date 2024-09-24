from __future__ import annotations

import datetime
import json
import logging
import os
import re
import shutil
from pathlib import Path

from mk.exec import run_or_fail
from mk.pre import CFG_FILE
from mk.tools import Action, Tool


class PreTool(Tool):
    name = "pre"

    def run(self, action: Action | None = None):
        if action:
            if action.name in ["changelog"]:
                self.changelog()
                return
            run_or_fail(["pre", action.name], tee=True)

    def is_present(self, path: Path) -> bool:
        if not shutil.which("gh"):
            logging.warning("Unable to find gh tool. See https://cli.github.com/")
            return False
        return True

    def changelog(self) -> None:
        """Pre helps you generate changelog.md from github releases."""
        releases_json = run_or_fail(
            "gh api repos/{owner}/{repo}/releases",
        )
        drafts_json = json.loads(releases_json.stdout)
        result = """---\ntitle: Changelog\n---\n\n"""
        for release in drafts_json:
            logging.info("Processing release '%s'", release["tag_name"])
            result += f"# {release['tag_name']}"
            if release["draft"]:
                result += " (unreleased)"
            else:
                created = datetime.datetime.fromisoformat(
                    release["created_at"][:10],
                ).replace(
                    tzinfo=datetime.timezone.utc,
                )
                result += f" ({created.strftime('%Y-%m-%d')})"

            body = release["body"].strip()
            result += f"\n\n{body}\n\n"

        result = result.rstrip("\r\n") + "\n"
        result = result.replace("\r\n", "\n")
        result = re.sub(r"\n{3,}", "\n\n", result, re.MULTILINE)
        filename = os.environ.get("CHANGELOG_FILE", "CHANGELOG.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
            logging.info("Wrote CHANGELOG.md")

    def actions(self) -> list[Action]:
        actions = [
            Action(
                name="changelog",
                description="[dim]Generate a changelog.md based on github releases.[/dim]",
                tool=self,
            ),
        ]
        if not os.path.exists(os.path.expanduser(CFG_FILE)):
            msg = f"Multi-repo feature was disabled because {CFG_FILE} was not found."
            logging.debug(msg)
        else:
            actions.extend(
                [
                    Action(
                        name="prs",
                        description="[dim]Show open PRs[/dim]",
                        tool=self,
                    ),
                    Action(
                        name="drafts",
                        description="[dim]Show draft releases[/dim]",
                        tool=self,
                    ),
                    Action(
                        name="alerts",
                        description="[dim]Show dependabot security alerts[/dim]",
                        tool=self,
                    ),
                ],
            )
        return actions
