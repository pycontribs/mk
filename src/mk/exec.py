import logging
import subprocess
import sys


def fail(msg: str, code: int = 1) -> None:
    logging.error(msg)
    sys.exit(code)


def run(*args) -> None:
    result = subprocess.run(*args, check=False)
    if result.returncode != 0:
        fail(
            f"Received exit code {result.returncode} from: {' '.join(result.args)}",
            code=result.returncode,
        )
