"""Main module."""
import itertools
import logging
import os
from typing import List

import typer
from rich.console import Console
from rich.logging import RichHandler

from mk import __version__
from mk._typer import CustomTyper
from mk.ctx import ctx

app = CustomTyper()
handlers: List[logging.Handler]
console_err = Console(stderr=True)

if "_MK_COMPLETE" in os.environ:
    level = logging.CRITICAL
    handlers = [logging.NullHandler()]
else:
    level = logging.DEBUG
    handlers = [RichHandler(console=console_err, show_time=False, show_path=False, markup=True)]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=handlers,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mk {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    # click_ctx: typer.Context,
    # pylint: disable=unused-argument
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),  # noqa: B008
) -> None:
    return


@app.command()
def detect() -> None:
    """Display detected information about current project."""
    typer.echo("mk detect...")
    ctx.runner.info()


@app.command()
def up() -> None:
    """Upload current change by creating or updating a CR/PR."""
    typer.secho("mk up...", fg="yellow")
    ctx.runner.up()


def cli() -> None:

    existing_commands = []
    for command_info in app.registered_commands:
        command = typer.main.get_command_from_info(command_info=command_info)
        existing_commands.append(command.name)

    # command = get_command_from_info(command_info=command_info)

    for action in ctx.runner.actions:
        # Currently we rename action that overlap but in the future we may
        # want to allow one to shadow others or we may want to chain them
        # under a single name.
        action_name = action.name
        counter = itertools.count(2)
        while action_name in existing_commands:
            action_name = f"{action.name}{next(counter)}"

        if action_name != action.name:
            logging.warning(
                "Action [dim]%s[/] exposed by [dim]%s[/] renamed to [dim]%s[/] to avoid shadowing existing one.",
                action.name,
                action.tool,
                action_name,
            )
        app.command(name=action_name, short_help=action.description, help=action.description)(
            action.run
        )
        existing_commands.append(action_name)
    # breakpoint()
    app()


if __name__ == "__main__":
    cli()
