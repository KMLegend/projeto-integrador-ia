from dataclasses import dataclass

from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.plan_repair import PlanRepair
from domain.ports.random_source import RandomSource


@dataclass(frozen=True, slots=True)
class LocalShiftMutation:
    """Mutacao por perturbacao local (Secao 4.4)."""

    _random_source: RandomSource
    _repair: PlanRepair

    def mutate(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
        rate: float = 0.20,
        mutation_range: int = 10,
    ) -> PurchasePlan:
        if self._random_source.ratio() >= rate:
            return plan

        pos_index = self._random_source.integer_below(scenario.size())
        target_pos = Position(pos_index)
        variation = self._random_source.integer_inclusive(-mutation_range, mutation_range)

        current_units = plan.quantity_at(target_pos).units_value()
        new_units = max(0, current_units + variation)

        mutated = plan.with_quantity_at(target_pos, Quantity.of(new_units))
        return self._repair.repair(mutated, scenario)
