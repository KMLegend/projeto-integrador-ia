import pytest

from domain.evolution.local_shift_mutation import LocalShiftMutation
from domain.model.budget_constraint import BudgetConstraint
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.ports.mutation_strategy import MutationStrategy
from tests.doubles.scripted_random_source import ScriptedRandomSource


@pytest.mark.parametrize("mutation_impl", [
    LocalShiftMutation(
        ScriptedRandomSource(ratios=[0.05], integers=[1, 5]),
        BudgetAwarePlanRepair(BudgetConstraint.from_reais("1000.00")),
    ),
    LocalShiftMutation(
        ScriptedRandomSource(ratios=[0.90]),
        BudgetAwarePlanRepair(BudgetConstraint.from_reais("1000.00")),
    ),
])
def test_mutation_strategy_contract_produces_valid_plan(
    mutation_impl: MutationStrategy,
    reference_scenario: ReplenishmentScenario,
) -> None:
    plan = PurchasePlan.of_units((0, 20, 0, 0, 90, 0))
    mutated = mutation_impl.mutate(plan, reference_scenario)

    assert isinstance(mutated, PurchasePlan)
    assert mutated.size() == plan.size()
