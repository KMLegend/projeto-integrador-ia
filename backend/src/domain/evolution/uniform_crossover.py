from dataclasses import dataclass

from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.plan_repair import PlanRepair
from domain.ports.random_source import RandomSource


@dataclass(frozen=True, slots=True)
class UniformCrossover:
    """Crossover uniforme por gene com corte em 0.5 (Secao 4.3)."""

    _random_source: RandomSource
    _repair: PlanRepair

    def combine(
        self,
        first: PurchasePlan,
        second: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> PurchasePlan:
        child_units = [
            self._select_gene(first, second, Position(idx)) for idx in range(scenario.size())
        ]
        unrepaired = PurchasePlan.of_units(child_units)
        return self._repair.repair(unrepaired, scenario)

    def _select_gene(
        self,
        first: PurchasePlan,
        second: PurchasePlan,
        pos: Position,
    ) -> int:
        if self._random_source.ratio() < 0.5:
            return first.quantity_at(pos).units_value()
        return second.quantity_at(pos).units_value()

    def random_index_below(
        self,
        limit: int,
    ) -> int:
        return self._random_source.integer_below(limit)
