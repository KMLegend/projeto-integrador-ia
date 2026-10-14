import pytest

from domain.model.fitness_weights import FitnessWeights
from domain.model.plan_assessment import PlanAssessment
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.coverage_calculator import CoverageCalculator
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy
from domain.ports.fitness_policy import FitnessPolicy


@pytest.mark.parametrize("fitness_impl", [
    WeightedFitnessPolicy.standard(),
    WeightedFitnessPolicy(CoverageCalculator(), FitnessWeights(coverage=5.0, risk_penalty=2.0)),
])
def test_fitness_policy_contract_behavior(
    fitness_impl: FitnessPolicy,
    reference_scenario: ReplenishmentScenario,
) -> None:
    plan = PurchasePlan.of_units((0, 22, 0, 0, 98, 0))

    assessment = fitness_impl.evaluate(plan, reference_scenario)
    assert isinstance(assessment, PlanAssessment)
    assert assessment.plan() == plan

    # Funcao pura
    second = fitness_impl.evaluate(plan, reference_scenario)
    assert second.fitness_value() == assessment.fitness_value()
