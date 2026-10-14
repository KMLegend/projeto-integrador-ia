import pytest

from domain.evolution.population import Population
from domain.evolution.truncation_selection import TruncationSelection
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy
from domain.ports.selection_strategy import SelectionStrategy


@pytest.mark.parametrize("selection_impl", [
    TruncationSelection(_parents_size=2),
    TruncationSelection(_parents_size=5),
])
def test_selection_strategy_contract_returns_at_least_two_parents(
    selection_impl: SelectionStrategy,
    reference_scenario: ReplenishmentScenario,
) -> None:
    plans = [
        PurchasePlan.of_units((0, 0, 0, 0, 0, 0)),
        PurchasePlan.of_units((0, 8, 0, 0, 28, 0)),
        PurchasePlan.of_units((0, 10, 0, 0, 30, 0)),
        PurchasePlan.of_units((0, 15, 0, 0, 50, 0)),
        PurchasePlan.of_units((0, 22, 0, 0, 98, 0)),
    ]
    population = Population.of_plans(plans)
    policy = WeightedFitnessPolicy.standard()

    selected = selection_impl.select(population, policy, reference_scenario)
    assert selected.size() >= 2
    assert selected.size() <= population.size()
