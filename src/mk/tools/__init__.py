from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass(order=True)
class Action:
    name: str
    _name: str = field(default="undefined", init=False, compare=True, repr=False)

    tool: Optional["Tool"] = field(default=None, compare=False)
    description: Optional[str] = field(default="...", compare=False)
    cwd: Optional[str] = field(default=None, compare=False)
    filename: Optional[str] = field(default=None, compare=False)
    args: Optional[List[Any]] = field(default_factory=list, compare=False)

    # https://github.com/florimondmanca/www/issues/102#issuecomment-817279834
    @property  # type: ignore
    def name(self) -> str:  # pylint: disable=function-redefined
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    def run(self) -> None:
        if self.tool:
            self.tool.run(self)


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

    def run(self, action: Optional[Action] = None):
        pass

    def __repr__(self):
        return self.name

    def __rich__(self):
        return f"[magenta]{self.name}[/]"
