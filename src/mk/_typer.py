import typer
from click_help_colors import HelpColorsCommand, HelpColorsGroup


class CustomHelpColorsGroup(HelpColorsGroup):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.help_headers_color = "blue"
        self.help_options_color = "yellow"


class CustomHelpColorsCommand(HelpColorsCommand):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.help_headers_color = "blue"
        self.help_options_color = "yellow"


class CustomTyper(typer.Typer):
    def __init__(
        self,
        *args,
        cls=CustomHelpColorsGroup,
        context_settings={"help_option_names": ["-h", "--help"]},
        **kwargs
    ) -> None:
        super().__init__(*args, cls=cls, context_settings=context_settings, **kwargs)

    def command(
        self,
        *args,
        cls=CustomHelpColorsCommand,
        context_settings={"help_option_names": ["-h", "--help"]},
        **kwargs
    ):
        return super().command(*args, cls=cls, context_settings=context_settings, **kwargs)
