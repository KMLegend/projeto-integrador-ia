from dataclasses import dataclass

from domain.errors.domain_errors import InvalidPercentageError
from domain.model.quantity import Quantity


@dataclass(frozen=True, slots=True)
class Percentage:
    _points: float

    def __post_init__(self) -> None:
        if self._points < 0.0:
            raise InvalidPercentageError(f"Percentual nao pode ser negativo: {self._points}")

    @staticmethod
    def zero() -> "Percentage":
        return Percentage(0.0)

    @staticmethod
    def hundred() -> "Percentage":
        return Percentage(100.0)

    @staticmethod
    def of(part: Quantity, whole: Quantity) -> "Percentage":
        if whole.is_zero():
            return Percentage.hundred()
        return Percentage((part.units_value() / whole.units_value()) * 100.0)

    def points(self) -> float:
        return self._points

    def times_weight(
        self,
        weight: float,
    ) -> float:
        return self._points * weight

    def value_for_serialization(self) -> float:
        return round(self._points, 4)
