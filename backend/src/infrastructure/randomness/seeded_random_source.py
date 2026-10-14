import random

from domain.ports.random_source import RandomSource


class SeededRandomSource(RandomSource):
    """Implementacao de RandomSource baseada no random.Random da biblioteca padrao."""

    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def ratio(self) -> float:
        return self._rng.random()

    def integer_below(
        self,
        exclusive_limit: int,
    ) -> int:
        return self._rng.randrange(0, exclusive_limit)

    def integer_inclusive(
        self,
        minimum: int,
        maximum: int,
    ) -> int:
        return self._rng.randint(minimum, maximum)
