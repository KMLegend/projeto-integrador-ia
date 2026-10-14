from collections.abc import Sequence
from dataclasses import dataclass

from domain.model.money import Money
from domain.model.position import MaybePosition, Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_item import ReplenishmentItem


@dataclass(frozen=True, slots=True)
class ReplenishmentScenario:
    """Cenario de reposicao de estoque - colecao de primeira classe."""

    _items: tuple[ReplenishmentItem, ...]

    @staticmethod
    def of_items(items: Sequence[ReplenishmentItem]) -> "ReplenishmentScenario":
        return ReplenishmentScenario(tuple(items))

    def size(self) -> int:
        return len(self._items)

    def item_at(self, position: Position) -> ReplenishmentItem:
        return self._items[position.index_value()]

    def required_quantities(self) -> tuple[Quantity, ...]:
        return tuple(item.required_quantity() for item in self._items)

    def required_total(self) -> Quantity:
        total = sum(item.required_quantity().units_value() for item in self._items)
        return Quantity.of(total)

    def total_cost_of(self, plan: PurchasePlan) -> Money:
        total_cents = sum(
            self._items[idx].cost_for(plan.quantity_at(Position(idx))).cents_for_computation()
            for idx in range(len(self._items))
        )
        return Money(total_cents)

    def cost_at(self, position: Position, quantity: Quantity) -> Money:
        return self._items[position.index_value()].cost_for(quantity)

    def most_expensive_position_among(self, positions: tuple[Position, ...]) -> MaybePosition:
        if not positions:
            return MaybePosition.absent()

        def key_func(p: Position) -> tuple[int, int]:
            price_cents = self._items[p.index_value()].unit_price().cents_for_computation()
            return (price_cents, -p.index_value())

        best = max(positions, key=key_func)
        return best.as_maybe()

    def positions_with_demand(self) -> tuple[Position, ...]:
        return tuple(Position(idx) for idx, item in enumerate(self._items) if item.has_demand())

    def total_required_cost(self) -> Money:
        total_cents = sum(
            item.full_replenishment_cost().cents_for_computation() for item in self._items
        )
        return Money(total_cents)
