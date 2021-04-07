import json
import subprocess
from typing import List

from mk.tools import Action, Tool


class NpmTool(Tool):
    name = "npm"

    def __init__(self, path=".") -> None:
        super().__init__(path=path)
        cmd = ("git", "ls-files", "**/package.json")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        if result.returncode != 0 or not result.stdout:
            self.present = False
            return
        self._actions: List[Action] = []
        for line in result.stdout.split():
            # we consider only up to one level deep files
            if line.count("/") > 1:
                continue
            cwd = line.split("/")[0]
            with open(line, "r") as package_json:
                x = json.load(package_json)["scripts"]
                for k in x.keys():
                    self._actions.append(
                        Action(
                            name=k,
                            tool=self,
                            # description=cp[section]["description"],
                            args=[k],
                            cwd=cwd,
                        )
                    )
        self.present = bool(self._actions)

    def is_present(self, path: str) -> bool:
        return self.present

    def actions(self) -> List[Action]:
        return self._actions

    def run(self, action: Action = None) -> None:
        if not action:
            cmd = ["npm", "run"]
            cwd = None
        else:
            cmd = ["npm", "run", action.name]
            cwd = action.cwd
        subprocess.run(cmd, check=True, cwd=cwd)
