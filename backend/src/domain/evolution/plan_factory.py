from dataclasses import dataclass

from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.plan_repair import PlanRepair
from domain.ports.random_source import RandomSource


@dataclass(frozen=True, slots=True)
class PlanFactory:
    """Fabrica de planos de compra aleatorios e viaveis."""

    _random_source: RandomSource
    _repair: PlanRepair

    def random_plan(self, scenario: ReplenishmentScenario) -> PurchasePlan:
        units = [
            self._draw_gene_for_item(scenario, Position(idx)) for idx in range(scenario.size())
        ]
        unrepaired = PurchasePlan.of_units(units)
        return self._repair.repair(unrepaired, scenario)

    def _draw_gene_for_item(self, scenario: ReplenishmentScenario, pos: Position) -> int:
        required = scenario.item_at(pos).required_quantity().units_value()
        if required <= 0:
            return 0
        return self._random_source.integer_inclusive(0, required)
