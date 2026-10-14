from dataclasses import dataclass
from typing import Any

from domain.model.budget_constraint import BudgetConstraint
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.coverage_calculator import CoverageCalculator
from domain.policy.naive_replenishment_policy import NaiveReplenishmentPolicy
from domain.ports.fitness_policy import FitnessPolicy


@dataclass(frozen=True, slots=True)
class StrategyAssessment:  # OC-8: DTO de avaliacao de estrategia
    """Avaliacao consolidada de uma estrategia de compras para exposicao em relatorios."""

    total_cost: float
    served_quantity: int
    served_ratio: float
    items_at_risk: int
    fitness: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cost": self.total_cost,
            "served_quantity": self.served_quantity,
            "served_ratio": self.served_ratio,
            "items_at_risk": self.items_at_risk,
            "fitness": self.fitness,
        }


@dataclass(frozen=True, slots=True)
class StrategyComparison:  # OC-8: DTO do comparativo baseline vs otimizado
    """Comparativo entre a solucao baseline e o plano otimizado pelo AG."""

    baseline: StrategyAssessment
    optimized: StrategyAssessment

    def to_dict(self) -> dict[str, dict[str, Any]]:
        return {
            "baseline": self.baseline.to_dict(),
            "optimized": self.optimized.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class ComparisonPolicies:  # OC-8: Agrupador de politicas de avaliacao
    """Politicas necessarias para avaliacao de estrategias."""

    fitness_policy: FitnessPolicy
    naive_policy: NaiveReplenishmentPolicy
    coverage_calculator: CoverageCalculator


class CompareReplenishmentStrategies:
    """Caso de uso para avaliar e contrastar a baseline e a solucao otimizada."""

    def __init__(
        self,
        policies: ComparisonPolicies,
        budget: BudgetConstraint,
    ) -> None:
        self._policies = policies
        self._budget = budget

    def execute(
        self,
        scenario: ReplenishmentScenario,
        optimized: PurchasePlan,
    ) -> StrategyComparison:
        baseline_plan = self._policies.naive_policy.build_plan(scenario, self._budget)
        baseline_assessment = self._assess_plan(baseline_plan, scenario)
        optimized_assessment = self._assess_plan(optimized, scenario)
        return StrategyComparison(baseline_assessment, optimized_assessment)

    def _assess_plan(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> StrategyAssessment:
        cost = float(scenario.total_cost_of(plan).value_for_serialization())
        report = self._policies.coverage_calculator.report_for(plan, scenario)

        served_units = sum(
            min(
                plan.quantity_at(Position(idx)).units_value(),
                scenario.item_at(Position(idx)).required_quantity().units_value(),
            )
            for idx in range(scenario.size())
        )

        served_ratio = round(report.served_ratio().points(), 1)
        items_at_risk = report.items_at_risk_count()
        fitness = round(self._policies.fitness_policy.evaluate(plan, scenario).fitness_value(), 2)

        return StrategyAssessment(
            total_cost=cost,
            served_quantity=served_units,
            served_ratio=served_ratio,
            items_at_risk=items_at_risk,
            fitness=fitness,
        )
