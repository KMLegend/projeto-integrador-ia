from typing import Protocol


class RandomSource(Protocol):
    """Porta para geracao de aleatoriedade deterministica no motor evolutivo."""

    def ratio(self) -> float:
        """Devolve numero de ponto flutuante no intervalo [0.0, 1.0)."""
        ...

    def integer_below(
        self,
        exclusive_limit: int,
    ) -> int:
        """Devolve inteiro no intervalo [0, exclusive_limit)."""
        ...

    def integer_inclusive(
        self,
        minimum: int,
        maximum: int,
    ) -> int:
        """Devolve inteiro no intervalo [minimum, maximum]."""
        ...
