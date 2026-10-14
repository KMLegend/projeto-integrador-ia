from dataclasses import dataclass

from domain.errors.domain_errors import NegativeQuantityError


@dataclass(frozen=True, slots=True)
class Quantity:
    _units: int

    def __post_init__(self) -> None:
        if isinstance(self._units, bool) or not isinstance(self._units, int):
            raise NegativeQuantityError("Unidades devem ser um inteiro")
        if self._units < 0:
            raise NegativeQuantityError(f"Quantidade nao pode ser negativa: {self._units}")

    @staticmethod
    def zero() -> "Quantity":
        return Quantity(0)

    @staticmethod
    def of(units: int) -> "Quantity":
        return Quantity(units)

    def plus(self, other: "Quantity") -> "Quantity":
        return Quantity(self._units + other._units)

    def minus(self, other: "Quantity") -> "Quantity":
        return Quantity(max(0, self._units - other._units))

    def limited_to(self, ceiling: "Quantity") -> "Quantity":
        return Quantity(min(self._units, ceiling._units))

    def decremented(self) -> "Quantity":
        return Quantity(max(0, self._units - 1))

    def is_zero(self) -> bool:
        return self._units == 0

    def is_greater_than(self, other: "Quantity") -> bool:
        return self._units > other._units

    def is_less_than(self, other: "Quantity") -> bool:
        return self._units < other._units

    def units_value(self) -> int:
        return self._units

    def value_for_serialization(self) -> int:
        return self._units
