from collections.abc import Sequence


class ScriptedRandomSource:
    """Duble de teste de RandomSource com valores pre-programados."""

    def __init__(
        self,
        ratios: Sequence[float] | None = None,
        integers: Sequence[int] | None = None,
    ) -> None:
        self._ratios = list(ratios or [])
        self._integers = list(integers or [])

    def ratio(self) -> float:
        if not self._ratios:
            raise RuntimeError("ScriptedRandomSource: sequencia de ratios esgotada")
        return self._ratios.pop(0)

    def integer_below(self, exclusive_limit: int) -> int:
        if not self._integers:
            raise RuntimeError("ScriptedRandomSource: sequencia de inteiros esgotada")
        val = self._integers.pop(0)
        return val % exclusive_limit

    def integer_inclusive(self, minimum: int, maximum: int) -> int:
        if not self._integers:
            raise RuntimeError("ScriptedRandomSource: sequencia de inteiros esgotada")
        return self._integers.pop(0)
