import pytest

from domain.evolution.uniform_crossover import UniformCrossover
from domain.model.budget_constraint import BudgetConstraint
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.ports.crossover_strategy import CrossoverStrategy
from tests.doubles.scripted_random_source import ScriptedRandomSource


@pytest.mark.parametrize("crossover_impl", [
    UniformCrossover(
        ScriptedRandomSource(ratios=[0.2] * 6),
        BudgetAwarePlanRepair(BudgetConstraint.from_reais("1000.00")),
    ),
    UniformCrossover(
        ScriptedRandomSource(ratios=[0.8] * 6),
        BudgetAwarePlanRepair(BudgetConstraint.from_reais("1000.00")),
    ),
])
def test_crossover_strategy_contract_produces_valid_plan(
    crossover_impl: CrossoverStrategy,
    reference_scenario: ReplenishmentScenario,
) -> None:
    p1 = PurchasePlan.of_units((0, 20, 0, 0, 90, 0))
    p2 = PurchasePlan.of_units((0, 10, 0, 0, 40, 0))

    child = crossover_impl.combine(p1, p2, reference_scenario)
    assert isinstance(child, PurchasePlan)
    assert child.size() == reference_scenario.size()
