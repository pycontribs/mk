from typing import Optional

from mk.runner import Runner


class Context:
    def __init__(self) -> None:
        self._runner: Optional[Runner] = None

    @property
    def runner(self) -> Runner:
        if not self._runner:
            self._runner = Runner()
        return self._runner


ctx = Context()
