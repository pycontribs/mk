from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(order=True)
class Action:
    name: str
    _name: str = field(default="undefined", init=False, compare=True, repr=False)

    tool: Tool | None = field(default=None, compare=False)
    description: str | None = field(default="...", compare=False)
    cwd: str | None = field(default=None, compare=False)
    filename: str | None = field(default=None, compare=False)
    args: list[Any] | None = field(default_factory=list, compare=False)

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


class Tool:
    name = "tool-name"

    def __init__(self, path=".") -> None:
        self.path = path

    # pylint: disable=unused-argument
    def is_present(self, path: Path) -> bool:
        """Return True if the tool configuration is present in the given path."""
        return False

    def actions(self) -> list[Action]:
        return []

    def run(self, action: Action | None = None):
        pass

    def __repr__(self) -> str:
        return self.name

    def __rich__(self):
        return f"[magenta]{self.name}[/]"
