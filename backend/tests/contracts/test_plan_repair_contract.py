import pytest

from domain.model.budget_constraint import BudgetConstraint
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.ports.plan_repair import PlanRepair


@pytest.mark.parametrize("repair_impl", [
    BudgetAwarePlanRepair(BudgetConstraint.from_reais("1000.00")),
    BudgetAwarePlanRepair(BudgetConstraint.from_reais("500.00")),
])
def test_plan_repair_contract_always_produces_feasible_plan(
    repair_impl: PlanRepair,
    reference_scenario: ReplenishmentScenario,
) -> None:
    test_plans = [
        PurchasePlan.of_units((100, 100, 100, 100, 100, 100)),
        PurchasePlan.of_units((0, 48, 0, 0, 98, 0)),
        PurchasePlan.of_units((0, 0, 0, 0, 0, 0)),
        PurchasePlan.of_units((5, 10, 15, 20, 25, 30)),
    ]

    for plan in test_plans:
        repaired = repair_impl.repair(plan, reference_scenario)
        # 1. Idempotencia
        assert repair_impl.repair(repaired, reference_scenario) == repaired

        # 2. Respeita tetos de necessidade
        ceilings = reference_scenario.required_quantities()
        for idx in range(reference_scenario.size()):
            assert repaired.units_for_serialization()[idx] <= ceilings[idx].units_value()
            assert repaired.units_for_serialization()[idx] >= 0
