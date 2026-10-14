from typing import Any

from domain.model.position import Position
from domain.model.replenishment_scenario import ReplenishmentScenario


class ScenarioMapper:
    """Mapeador para conversao do agregado ReplenishmentScenario em estruturas de dados."""

    @staticmethod
    def to_items_list(scenario: ReplenishmentScenario) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for idx in range(scenario.size()):
            item = scenario.item_at(Position(idx))
            items.append(
                {
                    "sku": item.sku().value_for_serialization(),
                    "unit_price": float(item.unit_price().value_for_serialization()),
                    "required_quantity": item.required_quantity().units_value(),
                }
            )
        return items
