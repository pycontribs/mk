from mk.runner import Runner
from typing import Optional


class Context:
    def __init__(self) -> None:
        self._runner: Optional[Runner] = None

    @property
    def runner(self) -> Runner:
        if not self._runner:
            from mk.runner import Runner

            self._runner = Runner()
        return self._runner


ctx = Context()
