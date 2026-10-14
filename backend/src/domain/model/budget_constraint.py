from dataclasses import dataclass
from decimal import Decimal

from domain.errors.domain_errors import InvalidBudgetError
from domain.model.money import Money


@dataclass(frozen=True, slots=True)
class BudgetConstraint:
    """Restricao orcamentaria de compras (RN-05)."""

    _limit: Money

    def __post_init__(self) -> None:
        if self._limit.is_zero() or self._limit.cents_for_computation() <= 0:
            raise InvalidBudgetError(
                "Orcamento limite deve ser estritamente maior que zero (RN-05)"
            )

    @staticmethod
    def from_money(limit: Money) -> "BudgetConstraint":
        return BudgetConstraint(limit)

    @staticmethod
    def from_reais(amount: str | Decimal) -> "BudgetConstraint":
        return BudgetConstraint(Money.from_reais(amount))

    def is_exceeded_by(self, cost: Money) -> bool:
        return cost.is_greater_than(self._limit)

    def share_among(
        self,
        count: int,
    ) -> Money:
        if count <= 0:
            return Money.zero()
        return Money(self._limit.cents_for_computation() // count)

    def limit_money(self) -> Money:
        return self._limit

    def value_for_serialization(self) -> float:
        return round(self._limit.cents_for_computation() / 100.0, 2)
