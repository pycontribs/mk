"""Main module."""
import logging
import typer
from rich.logging import RichHandler
import subprocess
from mk.ctx import ctx
from mk import __version__

app = typer.Typer()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(show_time=False, show_path=False)],
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mk {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    )  # noqa: B008
) -> None:
    return


@app.command()
def detect() -> None:
    """Display detected information about current project."""
    typer.echo("mk detect...")
    ctx.runner.info()


@app.command()
def lint() -> None:
    """Perform linting."""
    typer.secho("mk lint...", fg="yellow")
    subprocess.call(["pre-commit", "run", "-a"])


@app.command()
def up() -> None:
    """Upload current change by creating or updating a CR/PR."""
    typer.secho("mk up...", fg="yellow")
    ctx.runner.up()


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
