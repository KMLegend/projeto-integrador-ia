from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.model.position import Position
from domain.model.quantity import Quantity

if TYPE_CHECKING:
    from domain.model.replenishment_scenario import ReplenishmentScenario


@dataclass(frozen=True, slots=True)
class PurchasePlan:
    """Plano de compras (cromossomo) - colecao de primeira classe imutavel."""

    _quantities: tuple[Quantity, ...]

    @staticmethod
    def of_units(units: Sequence[int]) -> "PurchasePlan":
        return PurchasePlan(tuple(Quantity.of(u) for u in units))

    @staticmethod
    def empty_like(scenario: "ReplenishmentScenario") -> "PurchasePlan":
        return PurchasePlan(tuple(Quantity.zero() for _ in range(scenario.size())))

    def size(self) -> int:
        return len(self._quantities)

    def quantity_at(self, position: Position) -> Quantity:
        return self._quantities[position.index_value()]

    def with_quantity_at(self, position: Position, quantity: Quantity) -> "PurchasePlan":
        idx = position.index_value()
        new_quantities = list(self._quantities)
        new_quantities[idx] = quantity
        return PurchasePlan(tuple(new_quantities))

    def decremented_at(self, position: Position) -> "PurchasePlan":
        idx = position.index_value()
        new_quantities = list(self._quantities)
        new_quantities[idx] = self._quantities[idx].decremented()
        return PurchasePlan(tuple(new_quantities))

    def clamped_to(self, ceilings: tuple[Quantity, ...]) -> "PurchasePlan":
        clamped = tuple(
            q.limited_to(ceiling) for q, ceiling in zip(self._quantities, ceilings, strict=True)
        )
        return PurchasePlan(clamped)

    def non_empty_positions(self) -> tuple[Position, ...]:
        return tuple(Position(idx) for idx, q in enumerate(self._quantities) if not q.is_zero())

    def total_units(self) -> Quantity:
        total = sum(q.units_value() for q in self._quantities)
        return Quantity.of(total)

    def units_for_serialization(self) -> tuple[int, ...]:
        return tuple(q.units_value() for q in self._quantities)
