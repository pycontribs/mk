import os
import subprocess
from typing import List, Optional, Any


class Action:
    def __init__(self, name: str, callable, args: Optional[List[Any]] = []) -> None:
        self.name = name
        self.callable = callable
        self.args = args
        # Python does not allow writing __doc__ and this is what click uses
        # for storing command names.
        # self.run.__doc__ = "bleah!"

    def run(self) -> None:
        self.callable(self.args)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class ToolRegistry(type):
    def __init__(cls, name, bases, nmspc) -> None:
        super(ToolRegistry, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, "registry"):
            cls.registry = set()
        cls.registry.add(cls)
        cls.registry -= set(bases)  # Remove base classes

    # Metamethods, called on class objects:
    def __iter__(cls):
        return iter(cls.registry)

    def __str__(cls) -> str:
        if cls in cls.registry:
            return cls.__name__
        return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])


class Tool(metaclass=ToolRegistry):
    def __init__(self, path=".") -> None:
        self.path = path

    @classmethod
    def is_present(cls, path: str) -> bool:
        return False

    def actions(self) -> List[Action]:
        return []

    def run(self, action: Optional[str] = None):
        pass


class PreCommitTool(Tool):
    def run(self, action: Optional[str] = None):
        subprocess.run(["pre-commit", "run", "-a"])

    @classmethod
    def is_present(cls, path: str) -> bool:
        if os.path.isfile(os.path.join(path, ".pre-commit-config.yaml")):
            return True
        return False

    def actions(self) -> List[Action]:
        return [Action("lint", self.run)]


class ToxTool(Tool):
    def is_present(path):
        if os.path.isfile(os.path.join(path, "tox.ini")):
            return True
        return False

    def actions(self) -> List[Action]:
        actions = subprocess.check_output(["tox", "-la"], universal_newlines=True).split()
        return [Action(name=a, callable=self.run, args=[a]) for a in actions]

    def run(self, action: Optional[str] = None):
        if not action:
            cmd = ["tox"]
        else:
            cmd = ["tox", "-e", action]
        subprocess.run(cmd)


class MakeTool(Tool):
    pass


class NpmTool(Tool):
    pass
