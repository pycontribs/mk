"""Main module."""
import argparse
import itertools
import logging
import os
import shlex
from typing import Any, Dict, List

import typer
from rich.console import Console
from rich.logging import RichHandler

from mk import __version__
from mk._typer import CustomTyper
from mk.ctx import ctx

handlers: List[logging.Handler]
console_err = Console(stderr=True)
app = CustomTyper(width=console_err.width, rich_markup_mode="rich")

if "_MK_COMPLETE" in os.environ:
    level = logging.CRITICAL
    handlers = [logging.NullHandler()]
else:
    level = logging.DEBUG
    handlers = [
        RichHandler(console=console_err, show_time=False, show_path=False, markup=False)
    ]

logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    handlers=handlers,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mk {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    click_ctx: typer.Context,
    # pylint: disable=unused-argument
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),  # noqa: B008
    verbose: int = typer.Option(
        0, "--verbose", "-v", count=True, help="Increase verbosity."
    ),
) -> None:
    # enforce coloring because some tools like npm may auto disable it due to
    # the lack of real tty.
    os.environ["FORCE_COLOR"] = os.environ.get("FORCE_COLOR", "true")

    # click_ctx.invoked_subcommand can be the command or None


@app.command()
def detect() -> None:
    """Display detected information about current project."""
    typer.echo("mk detect...")
    ctx.runner.info()


@app.command()
def commands() -> None:
    """List all commands available."""
    for action in ctx.runner.actions:
        print(action.name)


def cli() -> None:
    parser = argparse.ArgumentParser(
        description="Preprocess arguments to set log level.",
        add_help=False,
    )
    parser.add_argument(
        "-v", "--verbose", action="append_const", const=1, dest="verbosity"
    )
    opt, _ = parser.parse_known_args()
    opt.verbosity = 0 if opt.verbosity is None else sum(opt.verbosity)
    if opt.verbosity:
        log_level = logging.INFO if opt.verbosity == 1 else logging.DEBUG
        logging.getLogger().setLevel(log_level)
        logging.log(level=log_level, msg=f"Reconfigured logging level to {log_level}")

    existing_commands = []
    for command_info in app.registered_commands:
        command = typer.main.get_command_from_info(
            command_info, pretty_exceptions_short=False, rich_markup_mode="rich"
        )
        existing_commands.append(command.name)

    # command = get_command_from_info(command_info=command_info)

    action_map: Dict[str, Any] = {}
    for action in ctx.runner.actions:
        # Currently we rename action that overlap but in the future we may
        # want to allow one to shadow others or we may want to chain them
        # under a single name.
        action_name = action.name
        counter = itertools.count(2)
        while action_name in existing_commands:
            action_name = f"{action.name}{next(counter)}"
            action.name = action_name

        if action_name != action.name:
            logging.warning(
                "Action [dim]%s[/] exposed by [dim]%s[/] renamed to [dim]%s[/] to avoid shadowing existing one.",
                action.name,
                action.tool,
                action_name,
            )
        # panel = "Detected commands" if action.tool else ""
        panel = str(action.tool) or "foo"
        short_help = action.description or ""
        if action.tool:
            if action.args:
                short_help += f" [dim]({shlex.join(action.args)})[/dim]"
            else:
                short_help += f" [dim]{action.tool}[/dim]"
        app.command(
            name=action_name,
            short_help=short_help,
            help=action.description,
            rich_help_panel=panel,
        )(action.run)
        action_map[action_name] = action
        existing_commands.append(action_name)
    # Add aliases for 1-3 letter commands
    for alias_len in (1, 2, 3):
        for x, action in action_map.items():
            alias = x[0:alias_len]
            # pylint: disable=consider-iterating-dictionary
            if alias in action_map.keys():
                continue
            if sum(1 for name in action_map.keys() if name.startswith(alias)) == 1:
                app.command(
                    name=alias,
                    short_help=f"Alias for [dim]mk {x}[/dim]",
                    rich_help_panel="aliases",
                    hidden=bool(opt.verbosity < 1),
                )(action.run)

    app()


if __name__ == "__main__":
    cli()
