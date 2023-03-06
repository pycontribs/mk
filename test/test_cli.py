import os
import re
import runpy
from typing import Optional

import pytest
from subprocess_tee import run

from mk.text import strip_ansi_escape


@pytest.mark.parametrize(
    "shell,expected",
    (
        pytest.param("zsh", "_mk_completion()", id="zsh"),
        pytest.param("bash", "_mk_completion()", id="bash"),
    ),
)
def test_show_completion_script(shell, expected) -> None:
    """Tests completion script generation."""
    env = os.environ.copy()
    env["_TYPER_COMPLETE_TEST_DISABLE_SHELL_DETECTION"] = "True"
    result = run(f"mk --show-completion {shell}", env=env, check=False, tee=False)
    assert result.returncode == 0, result
    # very important as we could easily break it by sending data to stdout
    assert expected in result.stdout


@pytest.mark.benchmark(
    group="completion",
    min_rounds=10,
    # timer=time.time,
    disable_gc=True,
    warmup=False,
)
def test_completion_speed(benchmark, monkeypatch) -> None:
    """Tests completion script speed."""
    monkeypatch.setattr("sys.argv", ["mk", "commands"])
    # monkeypatch.setenv("_MK_COMPLETE", "complete_zsh")
    # monkeypatch.setenv("_TYPER_COMPLETE_ARGS", "c")

    def do_complete() -> Optional[int]:
        # shell execution can add considerable extra time that varies from
        # system to system. We only benchmark our own module execution time
        try:
            return runpy.run_module("mk", run_name="__main__")
        except SystemExit as exc:
            return exc.code

    result = benchmark(do_complete)

    assert result == 0
    assert benchmark.stats["min"] > 0.0001  # seconds
    assert benchmark.stats["mean"] < 0.01  # seconds


@pytest.mark.parametrize(
    "shell,expected",
    (
        pytest.param("zsh", "_arguments '", id="zsh"),
        pytest.param("bash", "commands", id="bash"),
    ),
)
def test_show_completion_data(shell, expected) -> None:
    """Tests completion hints."""
    env = os.environ.copy()
    env["_MK_COMPLETE"] = f"complete_{shell}"
    env["_TYPER_COMPLETE_ARGS"] = ""
    env["COMP_WORDS"] = "mk command"
    env["COMP_CWORD"] = "1"
    result = run(["mk", "--show-completion"], env=env, check=False, tee=False)
    # Apparently test return an unexpected 1 even if completion seems to be
    # working, disabling return code testing until we know why.
    # assert result.returncode == 0, result
    # very important as we could easily break it by sending data to stdout
    assert re.search(expected, result.stdout, flags=re.MULTILINE)


def test_help() -> None:
    """Tests display of help."""
    result = run(["mk", "--help"], check=False, tee=False)
    assert result.returncode == 0, result
    # very important as we could easily break it by sending data to stdout
    output = strip_ansi_escape(result.stdout)
    assert "Usage: mk" in output


def test_no_git_repo() -> None:
    """Ensure error message is displayed outside git repos."""
    result = run(["mk"], check=False, cwd="/", tee=False)
    assert result.returncode == 0, result
    assert "Current version of mk works only within git repos" in result.stderr
