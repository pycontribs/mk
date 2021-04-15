import logging
import subprocess
import sys

import subprocess_tee


def fail(msg: str, code: int = 1) -> None:
    logging.error(msg)
    sys.exit(code)


def run(args, *, check=False, cwd=None, tee=False) -> subprocess.CompletedProcess:
    if isinstance(args, str):
        cmd = args
        shell = True
    else:
        cmd = " ".join(args)
        shell = False
    logging.info("Executing: %s", cmd)
    result = subprocess_tee.run(
        args,
        check=check,
        shell=shell,
        universal_newlines=True,
        cwd=cwd,
        tee=tee,
    )
    return result


def run_or_raise(*args, cwd=None, tee=False) -> subprocess.CompletedProcess:
    return run(*args, check=True, cwd=cwd, tee=tee)


def run_or_fail(*args, cwd=None, tee=False) -> subprocess.CompletedProcess:
    try:
        return run(*args, check=True, cwd=cwd, tee=tee)
    except subprocess.CalledProcessError as exc:
        msg = f"Received exit code {exc.returncode} from: {args}"
        if not tee:
            msg += f"\n{exc.stdout}\n{exc.stderr}"
        fail(
            msg,
            code=exc.returncode,
        )
        raise
