import os
import subprocess
from typing import List, Optional, Any


class Action:
    def __init__(self, name: str, tool: "Tool", args: Optional[List[Any]] = []) -> None:
        self.name = name
        self.description: str = f"... (from {tool})"
        self.tool = tool
        self.args = args
        # Python does not allow writing __doc__ and this is what click uses
        # for storing command names.
        # self.run.__doc__ = "bleah!"

    def run(self) -> None:
        self.tool.run(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class ToolRegistry(type):
    def __init__(cls, name, bases, nmspc) -> None:
        super(ToolRegistry, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, "registry"):
            cls.registry = set()
        cls.registry.add(cls())
        cls.registry -= set(bases)  # Remove base classes

    # Metamethods, called on class objects:
    def __iter__(cls):
        return iter(cls.registry)

    def __str__(cls) -> str:
        if cls in cls.registry:
            return cls.__name__
        return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])


class Tool(metaclass=ToolRegistry):
    name = "tool-name"

    def __init__(self, path=".") -> None:
        self.path = path

    # pylint: disable=unused-argument
    def is_present(self, path: str) -> bool:
        return False

    def actions(self) -> List[Action]:
        return []

    def run(self, action: Optional[str] = None):
        pass

    def __repr__(self):
        return self.name

    def __rich__(self):
        return f"[magenta]{self.name}[/]"


class PreCommitTool(Tool):
    name = "pre-commit"

    def run(self, action: Optional[str] = None):
        subprocess.run(["pre-commit", "run", "-a"], check=True)

    def is_present(self, path: str) -> bool:
        if os.path.isfile(os.path.join(path, ".pre-commit-config.yaml")):
            return True
        return False

    def actions(self) -> List[Action]:
        return [Action(name="lint", tool=self)]


class ToxTool(Tool):
    name = "tox"

    def is_present(self, path: str) -> bool:
        if os.path.isfile(os.path.join(path, "tox.ini")):
            return True
        return False

    def actions(self) -> List[Action]:
        # -a is not supported by tox4!
        actions = subprocess.check_output(["tox", "-l"], universal_newlines=True).split()
        return [Action(name=a, tool=self, args=[a]) for a in actions]

    def run(self, action: Optional[str] = None) -> None:
        if not action:
            cmd = ["tox"]
        else:
            cmd = ["tox", "-e", action]
        subprocess.run(cmd, check=True)


class MakeTool(Tool):
    name = "make"


class NpmTool(Tool):
    name = "npm"
