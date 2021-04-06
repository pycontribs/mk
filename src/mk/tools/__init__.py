from typing import Any, List, Optional


class Action:

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name: str,
        tool: "Tool",
        description: Optional[str] = None,
        cwd: Optional[str] = None,
        args: Optional[List[Any]] = [],
    ) -> None:
        self.name = name
        self.description: str = (description or "...") + f" (from {tool})"
        self.tool = tool
        self.cwd = cwd
        self.args = args
        # Python does not allow writing __doc__ and this is what click uses
        # for storing command names.
        # self.run.__doc__ = "bleah!"

    def run(self) -> None:
        self.tool.run(self)

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

    def run(self, action: Optional[Action] = None):
        pass

    def __repr__(self):
        return self.name

    def __rich__(self):
        return f"[magenta]{self.name}[/]"
