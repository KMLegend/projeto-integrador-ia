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
        return self._apply_shift(plan, scenario, mutation_range)

    def _apply_shift(
        self, plan: PurchasePlan, scenario: ReplenishmentScenario, m_range: int
    ) -> PurchasePlan:
        pos = Position(self._random_source.integer_below(scenario.size()))
        delta = self._random_source.integer_inclusive(-m_range, m_range)
        new_q = Quantity.of(max(0, plan.quantity_at(pos).units_value() + delta))
        return self._repair.repair(plan.with_quantity_at(pos, new_q), scenario)
