import logging
import subprocess
import sys
from os import environ
from typing import Dict, Optional

import subprocess_tee


def fail(msg: str, code: int = 1) -> None:
    logging.error(msg)
    sys.exit(code)


def run(
    args,
    *,
    check=False,
    cwd=None,
    tee=False,
    env_overrides: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    env: Optional[Dict[str, str]] = None
    if env_overrides:
        env = environ.copy()
        env.update(env_overrides)

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
        env=env,
    )
    return result


def run_or_raise(*args, cwd=None, tee=False) -> subprocess.CompletedProcess:
    return run(*args, check=True, cwd=cwd, tee=tee)


def run_or_fail(
    *args, cwd=None, tee=False, env_overrides: Optional[Dict[str, str]] = None
) -> subprocess.CompletedProcess:
    try:
        return run(*args, check=True, cwd=cwd, tee=tee, env_overrides=env_overrides)
    except subprocess.CalledProcessError as exc:
        msg = f"Received exit code {exc.returncode} from: {args}"
        if not tee:
            msg += f"\n{exc.stdout}\n{exc.stderr}"
        fail(
            msg,
            code=exc.returncode,
        )
        raise
