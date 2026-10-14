from dataclasses import dataclass
from decimal import Decimal

from domain.model.money import Money
from domain.model.quantity import Quantity


@dataclass(frozen=True, slots=True)
class UnitPrice:
    _amount: Money

    @staticmethod
    def from_reais(amount: str | Decimal) -> "UnitPrice":
        return UnitPrice(Money.from_reais(amount))

    @staticmethod
    def from_money(money: Money) -> "UnitPrice":
        return UnitPrice(money)

    def total_for(self, quantity: Quantity) -> Money:
        return self._amount.times(quantity.units_value())

    def is_more_expensive_than(self, other: "UnitPrice") -> bool:
        return self._amount.is_greater_than(other._amount)

    def cents_for_computation(self) -> int:
        return self._amount.cents_for_computation()

    def value_for_serialization(self) -> str:
        return self._amount.value_for_serialization()
