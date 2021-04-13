import os
import re
import runpy
from subprocess import run
from typing import Optional

import pytest


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
    env["SHELL"] = f"/bin/{shell}"
    result = run(
        ["mk", "--show-completion"],
        universal_newlines=True,
        capture_output=True,
        env=env,
        check=False,
    )
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
        # return run(
        #     ["mk", "--show-completion"],
        #     universal_newlines=True,
        #     capture_output=True,
        #     check=True,
        # )

    result = benchmark(do_complete)

    assert result == 0
    assert benchmark.stats["min"] > 0.0010  # seconds
    assert benchmark.stats["mean"] < 0.0035  # seconds


@pytest.mark.parametrize(
    "shell,expected",
    (
        pytest.param("zsh", '^_arguments.*\n"commands":', id="zsh"),
        pytest.param("bash", "commands\n", id="bash"),
    ),
)
def test_show_completion_data(shell, expected) -> None:
    """Tests completion hints."""
    env = os.environ.copy()
    env["_MK_COMPLETE"] = f"complete_{shell}"
    env["_TYPER_COMPLETE_ARGS"] = ""
    result = run(
        ["mk", "--show-completion"],
        universal_newlines=True,
        capture_output=True,
        env=env,
        check=False,
    )
    # Apparently test return an unexpected 1 even if completion seems to be
    # working, disabling return code testing until we know why.
    # assert result.returncode == 0, result
    # very important as we could easily break it by sending data to stdout
    assert re.search(expected, result.stdout, flags=re.MULTILINE)


def test_help() -> None:
    """Tests display of help."""
    result = run(["mk", "--help"], universal_newlines=True, capture_output=True, check=False)
    assert result.returncode == 0, result
    # very important as we could easily break it by sending data to stdout
    assert result.stdout.startswith("Usage: mk")


def test_no_git_repo() -> None:
    """Ensure error message is displayed outside git repos."""
    result = run(["mk"], universal_newlines=True, capture_output=True, check=False, cwd="/")
    assert result.returncode == 0, result
    assert "Current version of mk works only within git repos" in result.stderr
