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

    def _fit_to_budget(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        while self._budget.is_exceeded_by(scenario.total_cost_of(plan)):
            most_expensive = scenario.most_expensive_position_among(plan.non_empty_positions())
            if most_expensive.is_absent():
                return plan
            plan = plan.decremented_at(most_expensive.value())
        return plan
