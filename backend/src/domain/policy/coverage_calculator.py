from dataclasses import dataclass

from domain.model.coverage_report import CoverageReport
from domain.model.percentage import Percentage
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_scenario import ReplenishmentScenario


@dataclass(frozen=True, slots=True)
class CoverageCalculator:
    """Calcula cobertura da demanda e produtos em risco (RN-07)."""

    def report_for(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> CoverageReport:
        if scenario.required_total().is_zero() or scenario.size() == 0:
            return CoverageReport(Percentage.hundred(), 0)
        return self._build_report(plan, scenario)

    def _build_report(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> CoverageReport:
        served = self._compute_served_units(plan, scenario)
        ratio = Percentage.of(Quantity.of(served), scenario.required_total())
        return CoverageReport(ratio, self._count_items_at_risk(plan, scenario))

    def _compute_served_units(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> int:
        return sum(self._served_at(plan, scenario, Position(i)) for i in range(scenario.size()))

    def _served_at(self, plan: PurchasePlan, scenario: ReplenishmentScenario, pos: Position) -> int:
        p_val = plan.quantity_at(pos).units_value()
        r_val = scenario.item_at(pos).required_quantity().units_value()
        return min(p_val, r_val)

    def _count_items_at_risk(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> int:
        return sum(
            1 for idx in range(scenario.size()) if self._is_at_risk(plan, scenario, Position(idx))
        )

    def _is_at_risk(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
        pos: Position,
    ) -> bool:
        item = scenario.item_at(pos)
        if not item.has_demand():
            return False
        return plan.quantity_at(pos).is_less_than(item.required_quantity())
