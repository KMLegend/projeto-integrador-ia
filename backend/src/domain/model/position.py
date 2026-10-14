from dataclasses import dataclass

from domain.errors.domain_errors import EmptyPositionError, InvalidPositionError


@dataclass(frozen=True, slots=True)
class Position:
    _index: int

    def __post_init__(self) -> None:
        if isinstance(self._index, bool) or not isinstance(self._index, int):
            raise InvalidPositionError("Indice de posicao deve ser inteiro")
        if self._index < 0:
            raise InvalidPositionError(f"Posicao nao pode ser negativa: {self._index}")

    def index_value(self) -> int:
        return self._index

    def as_maybe(self) -> "MaybePosition":
        return MaybePosition.present(self)

    def value_for_serialization(self) -> int:
        return self._index


@dataclass(frozen=True, slots=True)
class MaybePosition:
    _position: Position | None

    @staticmethod
    def present(position: Position) -> "MaybePosition":
        return MaybePosition(position)

    @staticmethod
    def absent() -> "MaybePosition":
        return MaybePosition(None)

    def is_absent(self) -> bool:
        return self._position is None

    def is_present(self) -> bool:
        return self._position is not None

    def value(self) -> Position:
        if self._position is None:
            raise EmptyPositionError("Tentativa de acessar valor de MaybePosition ausente")
        return self._position
