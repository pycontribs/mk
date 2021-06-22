import os
import re
from configparser import ConfigParser
from typing import List, Optional

from mk.exec import run_or_fail
from mk.text import strip_ansi_escape
from mk.tools import Action, Tool


class ToxTool(Tool):
    name = "tox"

    def is_present(self, path: str) -> bool:
        if os.path.isfile(os.path.join(path, "tox.ini")):
            return True
        return False

    def actions(self) -> List[Action]:
        # -a is not supported by tox4!
        actions: List[Action] = []
        cp = ConfigParser(strict=False, interpolation=None)
        env_overrides = {"PY_COLORS": "0"}
        tox_cfg = run_or_fail(["tox", "--showconfig"], env_overrides=env_overrides).stdout

        # workaround for https://github.com/tox-dev/tox/issues/2030
        # we remove all lines starting with .tox from output
        tox_cfg = re.sub(r"\.tox.*\n?", "", strip_ansi_escape(tox_cfg), re.MULTILINE)

        # now tox_cfg should have a valid ini content
        cp.read_string(tox_cfg)
        for section in cp.sections():
            if section.startswith("testenv:"):
                _, env_name = section.split(":")
                # we ignore hidden envs like implicit .pkg:
                if not env_name.startswith("."):
                    actions.append(
                        Action(
                            name=env_name,
                            tool=self,
                            description=cp[section]["description"],
                            args=[env_name],
                        )
                    )

        return actions

    def run(self, action: Optional[Action] = None) -> None:
        if not action:
            cmd = ["tox"]
        else:
            cmd = ["tox", "-e", action.name]
        run_or_fail(cmd, tee=True)
