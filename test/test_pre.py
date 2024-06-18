"""Tests"""

from typer.testing import CliRunner

from mk.pre import app

runner = CliRunner()


def test_main() -> None:
    """CLI Tests"""
    result = runner.invoke(app, ["--help", "--config=test/pre.yml"])
    assert result.exit_code == 0, result.stdout
    assert "Pre helps you chain releases on github." in result.stdout
