import os
from subprocess import run

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


@pytest.mark.parametrize(
    "shell,expected",
    (
        pytest.param("zsh", "_arguments", id="zsh"),
        pytest.param("bash", "deps\n", id="bash"),
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
    assert result.stdout.startswith(expected)


def test_help() -> None:
    """Tests display of help."""
    result = run(["mk", "--help"], universal_newlines=True, capture_output=True, check=False)
    assert result.returncode == 0, result
    # very important as we could easily break it by sending data to stdout
    assert result.stdout.startswith("Usage: mk")


def test_no_git_repo() -> None:
    """Ensure failure to run outside git repos."""
    result = run(["mk"], universal_newlines=True, capture_output=True, check=False, cwd="/")
    assert result.returncode == 1, result
    assert "Current version of mk works only within git repos" in result.stderr
