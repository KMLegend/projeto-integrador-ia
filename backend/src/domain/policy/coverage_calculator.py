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
        required_total = scenario.required_total()
        if required_total.is_zero() or scenario.size() == 0:
            return CoverageReport(Percentage.hundred(), 0)

        served_units = self._compute_served_units(plan, scenario)
        items_at_risk = self._count_items_at_risk(plan, scenario)
        served_ratio = Percentage.of(Quantity.of(served_units), required_total)
        return CoverageReport(served_ratio, items_at_risk)

    def _compute_served_units(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> int:
        return sum(
            min(
                plan.quantity_at(Position(idx)).units_value(),
                scenario.item_at(Position(idx)).required_quantity().units_value(),
            )
            for idx in range(scenario.size())
        )

    def _count_items_at_risk(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> int:
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
