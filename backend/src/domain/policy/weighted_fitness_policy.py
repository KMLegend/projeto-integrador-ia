from dataclasses import dataclass

from domain.model.fitness_weights import FitnessWeights
from domain.model.plan_assessment import PlanAssessment
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.coverage_calculator import CoverageCalculator


@dataclass(frozen=True, slots=True)
class WeightedFitnessPolicy:
    """Calcula o fitness ponderado (served_ratio * 10 - items_at_risk * 5)."""

    _coverage_calculator: CoverageCalculator
    _weights: FitnessWeights

    @staticmethod
    def standard() -> "WeightedFitnessPolicy":
        return WeightedFitnessPolicy(CoverageCalculator(), FitnessWeights.default())

    def evaluate(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PlanAssessment:
        report = self._coverage_calculator.report_for(plan, scenario)
        score = self._weights.score(report)
        return PlanAssessment(plan, score)
