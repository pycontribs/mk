import logging
import subprocess
import sys
from typing import Any


def fail(msg: str, code: int = 1) -> None:
    logging.error(msg)
    sys.exit(code)


def run(*args) -> subprocess.CompletedProcess[Any]:
    result = subprocess.run(*args, capture_output=True, check=False, universal_newlines=True)  # type: ignore
    if result.returncode != 0:
        fail(
            f"Received exit code {result.returncode} from: {' '.join(result.args)}\n{result.stdout}\n{result.stderr}",
            code=result.returncode,
        )
    return result
