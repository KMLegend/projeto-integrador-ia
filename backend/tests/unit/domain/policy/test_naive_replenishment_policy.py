import pytest

from domain.model.budget_constraint import BudgetConstraint
from domain.model.money import Money
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.policy.coverage_calculator import CoverageCalculator
from domain.policy.naive_replenishment_policy import NaiveReplenishmentPolicy
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy


def test_naive_policy_reproduces_golden_values(reference_scenario: ReplenishmentScenario) -> None:
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    naive_policy = NaiveReplenishmentPolicy(repair)

    plan = naive_policy.build_plan(reference_scenario, budget)

    # 1. Plano exato
    assert plan.units_for_serialization() == (0, 8, 0, 0, 28, 0)

    # 2. Custo exato
    cost = reference_scenario.total_cost_of(plan)
    assert cost == Money.from_reais("314.32")

    # 3. Unidades totais
    assert plan.total_units().units_value() == 36

    # 4. Indicadores de cobertura
    calculator = CoverageCalculator()
    report = calculator.report_for(plan, reference_scenario)
    assert report.items_at_risk_count() == 2
    assert report.served_ratio_points() == pytest.approx(24.6575, abs=1e-4)

    # 5. Fitness
    fitness_policy = WeightedFitnessPolicy.standard()
    assessment = fitness_policy.evaluate(plan, reference_scenario)
    assert assessment.fitness_value() == pytest.approx(236.5753, abs=1e-4)
