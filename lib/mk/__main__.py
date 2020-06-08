"""Main module."""
import logging
import click
import subprocess
from mk import __version__
from mk.runner import Runner


logging.basicConfig(level=logging.DEBUG)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group()
@click.option("--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True)
def cli():
    """Run cli."""
    runner = Runner()
    click.secho(f"mk detected {runner.root} git repository", fg="green")

    # commands = {"lint": "pre-commit run -a"}


@cli.command()
def detect():
    click.secho("mk detect...", fg="yellow")


@cli.command()
def lint():
    click.secho("mk lint...", fg="yellow")
    subprocess.call(["pre-commit", "run", "-a"])
