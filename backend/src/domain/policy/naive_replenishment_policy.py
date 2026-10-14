from dataclasses import dataclass

from domain.model.budget_constraint import BudgetConstraint
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.plan_repair import PlanRepair


@dataclass(frozen=True, slots=True)
class NaiveReplenishmentPolicy:
    """Politica de reposicao ingenua (baseline): divide igualmente entre os itens."""

    _repair: PlanRepair

    def build_plan(
        self,
        scenario: ReplenishmentScenario,
        budget: BudgetConstraint,
    ) -> PurchasePlan:
        if scenario.size() == 0:
            return PurchasePlan.of_units(())

        share = budget.share_among(scenario.size())
        units = tuple(
            share.units_affordable_at(scenario.item_at(Position(idx)).unit_price()).units_value()
            for idx in range(scenario.size())
        )
        unrepaired_plan = PurchasePlan.of_units(units)
        return self._repair.repair(unrepaired_plan, scenario)
