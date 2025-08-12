"""Expose features related to git repositories."""

from __future__ import annotations

import datetime
import json
import os
from subprocess import run
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from typer_config.decorators import use_yaml_config

CFG_FILE = os.environ.get("MK_CONFIG_FILE", "~/.config/mk/mk.yml")


class TyperApp(typer.Typer):
    """Our App."""

    repos: list[str]


app = TyperApp()
console = Console()


@app.callback(invoke_without_command=True)
@use_yaml_config(
    default_value=os.path.expanduser(CFG_FILE),
    param_help=f"Configuration file ({CFG_FILE}).",
)
# https://github.com/tiangolo/typer/issues/533
def default(repos: Annotated[list[str], typer.Option()] = []) -> None:
    """Implicit entry point."""
    if repos is None:
        repos = []
    # breakpoint()
    app.repos = list(filter(lambda s: not s.startswith("_"), repos))


@app.command()
def drafts() -> None:
    """Pre helps you chain releases on github."""
    for repo in app.repos:
        repo_link = f"[markdown.link][link=https://github.com/{repo}]{repo}[/][/]"
        result = run(  # noqa: S602
            f'gh api repos/{repo}/releases --jq "[.[] | select(.draft)"]',
            text=True,
            shell=True,
            capture_output=True,
            check=True,
        )
        drafts_json = json.loads(result.stdout)
        if not drafts_json or (
            isinstance(drafts_json, dict) and drafts_json["message"] == "Not Found"
        ):
            console.print(f"🟢 {repo_link} [dim]has no draft release.[/]")
            continue
        for draft in drafts_json:
            created = datetime.datetime.fromisoformat(draft["created_at"]).replace(
                tzinfo=datetime.timezone.utc,
            )
            age = (datetime.datetime.now(tz=datetime.timezone.utc) - created).days
            if not draft["body"].strip():
                console.print(f"🟢 {repo_link} [dim]has an empty draft release.[/]")
                continue

            md = Panel(draft["body"].replace("\n\n", "\n").strip("\n"), box=box.MINIMAL)
            msg = (
                f"🟠 {repo_link} draft release "
                f"[link={draft['html_url']}][markdown.link]{draft['tag_name']}[/][/]"
                f" created [repr.number]{age}[/] days ago:\n"
            )
            console.print(msg, highlight=False, end="")
            console.print(md, style="dim")


@app.command()
def prs() -> None:
    """List pending pull-request."""
    # for user in TEAM:
    # --review-requested=@{user}
    # --owner=ansible --owner=ansible-community
    cmd = (
        "GH_PAGER= gh search prs --draft=false --state=open --limit=100 --sort=updated"
    )
    cmd += "".join(f" --repo={repo}" for repo in app.repos)
    cmd += (
        " --template '{{range .}}{{tablerow .repository.nameWithOwner (timeago .updatedAt) "
        '.title (hyperlink .url (printf "#%v" .number) ) }}{{end}}{{tablerender}}\' '
        "--json title,url,repository,updatedAt,number"
    )
    console.print(f"[dim]{cmd}[/]", highlight=False)
    os.system(cmd)  # noqa: S605


@app.command()
def alerts() -> None:
    """List open alerts."""
    for repo in app.repos:
        cmd = "GH_PAGER= gh "
        cmd += f"api /repos/{repo}/dependabot/alerts"
        cmd += " --jq='.[] | select(.state!=\"fixed\") | .html_url'"
        result = run(  # noqa: S602
            cmd,
            text=True,
            shell=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            console.print(
                f"[dim]{cmd}[/dim] failed with {result.returncode}\n"
                f"{result.stdout}\n\n{result.stderr}",
            )
        else:
            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(result.stderr)


if __name__ == "__main__":
    # execute only if run as a script
    app()
