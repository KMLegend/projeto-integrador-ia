from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from typing import TYPE_CHECKING

from domain.errors.domain_errors import InvalidMoneyError, NegativeMoneyError

if TYPE_CHECKING:
    from domain.model.percentage import Percentage
    from domain.model.quantity import Quantity
    from domain.model.unit_price import UnitPrice


@dataclass(frozen=True, slots=True)
class Money:
    _cents: int

    def __post_init__(self) -> None:
        if isinstance(self._cents, bool) or not isinstance(self._cents, int):
            raise InvalidMoneyError("Centavos devem ser expressos em inteiro")
        if self._cents < 0:
            raise NegativeMoneyError(f"Valor monetario nao pode ser negativo: {self._cents}")

    @staticmethod
    def from_reais(amount: str | Decimal) -> "Money":
        if isinstance(amount, float):
            raise InvalidMoneyError("Construir Money a partir de float e proibido (D-03)")
        if not isinstance(amount, (str, Decimal)):
            raise InvalidMoneyError("Entrada deve ser str ou Decimal")
        decimal_val = Decimal(amount)
        cents = int((decimal_val * Decimal("100")).to_integral_value(rounding=ROUND_HALF_EVEN))
        return Money(cents)

    @staticmethod
    def zero() -> "Money":
        return Money(0)

    def plus(self, other: "Money") -> "Money":
        return Money(self._cents + other._cents)

    def minus(self, other: "Money") -> "Money":
        if self._cents < other._cents:
            msg = f"Subtracao resultaria em valor negativo: {self._cents} < {other._cents}"
            raise NegativeMoneyError(msg)
        return Money(self._cents - other._cents)

    def times(
        self,
        factor: int,
    ) -> "Money":
        if factor < 0:
            raise NegativeMoneyError("Fator multiplicativo nao pode ser negativo")
        return Money(self._cents * factor)

    def is_greater_than(self, other: "Money") -> bool:
        return self._cents > other._cents

    def is_zero(self) -> bool:
        return self._cents == 0

    def ratio_to(self, total: "Money") -> "Percentage":
        from domain.model.percentage import Percentage

        if total.is_zero():
            return Percentage.zero()
        return Percentage((self._cents / total._cents) * 100.0)

    def units_affordable_at(self, price: "UnitPrice") -> "Quantity":
        from domain.model.quantity import Quantity

        return Quantity(self._cents // price.cents_for_computation())

    def cents_for_computation(self) -> int:
        return self._cents

    def value_for_serialization(self) -> str:
        return f"{self._cents / 100:.2f}"
