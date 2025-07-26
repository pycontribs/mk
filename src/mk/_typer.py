from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from typer.core import TyperCommand
from typer.models import CommandFunctionType

if TYPE_CHECKING:
    from typing import Any, Callable

    from typer.core import TyperGroup


class CustomTyper(typer.Typer):
    def __init__(
        self,
        *args: Any,
        cls: type[TyperGroup] | None = None,
        context_settings: dict[str, Any] = {
            "help_option_names": ["-h", "--help"],
        },
        width: int = 80,
        **kwargs: Any,
    ) -> None:
        context_settings["max_content_width"] = width
        super().__init__(
            *args,
            cls=cls,
            context_settings=context_settings,
            no_args_is_help=True,
            **kwargs,
        )

    def command(
        self,
        *args: Any,
        cls: type[TyperCommand] | None = None,
        context_settings: dict[Any, Any] | None = {
            "help_option_names": ["-h", "--help"]
        },
        **kwargs: Any,
    ) -> Callable[[CommandFunctionType], CommandFunctionType]:
        return super().command(
            *args,
            cls=cls,
            context_settings=context_settings,
            **kwargs,
        )
