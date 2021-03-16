"""Main module."""
import logging
import click
from rich.logging import RichHandler
import subprocess
from mk import __version__
from mk.runner import Runner


logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(show_time=False, show_path=False)],
)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group()
@click.option("--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.pass_context
def cli(ctx):
    """Run cli."""
    ctx.ensure_object(dict)
    runner = Runner()
    ctx.obj["runner"] = runner

    click.secho(f"mk detected {runner.root} git repository", fg="green")

    # commands = {"lint": "pre-commit run -a"}


@cli.command()
def detect():
    """Display detected information about current project."""
    click.secho("mk detect...", fg="yellow")


@cli.command()
def lint():
    """Perform linting."""
    click.secho("mk lint...", fg="yellow")
    subprocess.call(["pre-commit", "run", "-a"])


@cli.command()
@click.pass_context
def up(ctx):
    """Upload current change by creating or updating a CR/PR."""
    click.secho("mk up...", fg="yellow")
    ctx.obj["runner"].up()
    # import pdb; pdb.set_trace()
