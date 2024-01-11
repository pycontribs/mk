from __future__ import annotations

from mk.runner import Runner


class Context:
    def __init__(self) -> None:
        self._runner: Runner | None = None

    @property
    def runner(self) -> Runner:
        if not self._runner:
            self._runner = Runner()
        return self._runner


ctx = Context()
