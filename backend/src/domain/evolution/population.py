from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.fitness_policy import FitnessPolicy

if TYPE_CHECKING:
    from domain.model.plan_assessment import PlanAssessment


@dataclass(frozen=True, slots=True)
class Population:
    """Populacao de planos de compra - colecao de primeira classe."""

    _plans: tuple[PurchasePlan, ...]

    @staticmethod
    def of_plans(plans: Sequence[PurchasePlan]) -> "Population":
        return Population(tuple(plans))

    def size(self) -> int:
        return len(self._plans)

    def plan_at(
        self,
        index: int,
    ) -> PurchasePlan:
        return self._plans[index]

    def plans(self) -> tuple[PurchasePlan, ...]:
        return self._plans

    def ranked_by(
        self,
        policy: FitnessPolicy,
        scenario: ReplenishmentScenario,
    ) -> "Population":
        sorted_plans = sorted(
            self._plans,
            key=lambda plan: policy.evaluate(plan, scenario).fitness_value(),
            reverse=True,
        )
        return Population(tuple(sorted_plans))

    def top(
        self,
        count: int,
    ) -> "Population":
        return Population(self._plans[:count])

    def best(
        self,
        policy: FitnessPolicy,
        scenario: ReplenishmentScenario,
    ) -> "PlanAssessment":
        ranked = self.ranked_by(policy, scenario)
        best_plan = ranked.plan_at(0)
        return policy.evaluate(best_plan, scenario)

    def extended_with(
        self,
        other: "Population",
    ) -> "Population":
        return Population(self._plans + other._plans)
