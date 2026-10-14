from dataclasses import dataclass

from domain.model.budget_constraint import BudgetConstraint
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario


@dataclass(frozen=True, slots=True)
class BudgetAwarePlanRepair:
    """Reparo de plano sob restricao orcamentaria e limites de demanda (RN-04, RN-05)."""

    _budget: BudgetConstraint

    def repair(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        return self._fit_to_budget(plan.clamped_to(scenario.required_quantities()), scenario)

    def _decrement_most_expensive(
        self, plan: PurchasePlan, scenario: ReplenishmentScenario
    ) -> PurchasePlan | None:
        pos = scenario.most_expensive_position_among(plan.non_empty_positions())
        return None if pos.is_absent() else plan.decremented_at(pos.value())

    def _fit_to_budget(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        while self._budget.is_exceeded_by(scenario.total_cost_of(plan)) and (
            (next_p := self._decrement_most_expensive(plan, scenario)) is not None
        ):
            plan = next_p
        return plan
