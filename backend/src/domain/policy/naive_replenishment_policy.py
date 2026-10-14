from dataclasses import dataclass

from domain.model.budget_constraint import BudgetConstraint
from domain.model.money import Money
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
        return self._repair.repair(self._naive_plan(scenario, budget), scenario)

    def _naive_plan(
        self, scenario: ReplenishmentScenario, budget: BudgetConstraint
    ) -> PurchasePlan:
        share = budget.share_among(scenario.size())
        units = tuple(self._units_at(share, scenario, Position(i)) for i in range(scenario.size()))
        return PurchasePlan.of_units(units)

    @staticmethod
    def _units_at(share: Money, scenario: ReplenishmentScenario, pos: Position) -> int:
        return share.units_affordable_at(scenario.item_at(pos).unit_price()).units_value()
