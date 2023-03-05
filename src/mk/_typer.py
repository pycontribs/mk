import typer


class CustomTyper(typer.Typer):
    def __init__(
        self,
        *args,
        cls=None,
        context_settings={
            "help_option_names": ["-h", "--help"],
        },
        width: int = 80,
        **kwargs,
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
        *args,
        cls=None,
        context_settings={"help_option_names": ["-h", "--help"]},
        **kwargs,
    ):
        return super().command(
            *args, cls=cls, context_settings=context_settings, **kwargs
        )
