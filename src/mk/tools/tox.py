import os
import subprocess
from configparser import ConfigParser
from typing import List, Optional

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
        tox_cfg = subprocess.check_output(["tox", "--showconfig"], universal_newlines=True)
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
        subprocess.run(cmd, check=True)
