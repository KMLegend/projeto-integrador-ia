"""D-19: o reparo em lote precisa produzir exatamente o mesmo plano que o ingenuo."""

import json
import pathlib
import random

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from domain.model.budget_constraint import BudgetConstraint
from domain.model.catalog_item import CatalogItem
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_item import ReplenishmentItem
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice
from domain.policy.batched_budget_plan_repair import BatchedBudgetPlanRepair
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair

FIXTURE = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "reference_scenario.json"


def _reference_scenario() -> ReplenishmentScenario:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return ReplenishmentScenario.of_items(
        [
            ReplenishmentItem(
                CatalogItem(Sku(i["sku"]), UnitPrice.from_reais(i["unit_price"])),
                Quantity.of(int(i["required_quantity"])),
            )
            for i in data["items"]
        ]
    )


@pytest.fixture
def pair() -> tuple[BudgetAwarePlanRepair, BatchedBudgetPlanRepair, ReplenishmentScenario]:
    budget = BudgetConstraint.from_reais("1000.00")
    return BudgetAwarePlanRepair(budget), BatchedBudgetPlanRepair(budget), _reference_scenario()


@given(units=st.lists(st.integers(min_value=0, max_value=200), min_size=6, max_size=6))
@settings(max_examples=300, deadline=None)
def test_batched_repair_matches_naive_repair(units: list[int]) -> None:
    budget = BudgetConstraint.from_reais("1000.00")
    scenario = _reference_scenario()
    plan = PurchasePlan.of_units(tuple(units))
    assert (
        BudgetAwarePlanRepair(budget).repair(plan, scenario).units_for_serialization()
        == BatchedBudgetPlanRepair(budget).repair(plan, scenario).units_for_serialization()
    )


def test_batched_repair_matches_on_golden_plans(pair) -> None:  # type: ignore[no-untyped-def]
    naive, batched, scenario = pair
    for units in [(0, 8, 0, 0, 28, 0), (0, 22, 0, 0, 98, 0), (0, 0, 0, 0, 0, 0),
                  (99, 99, 99, 99, 99, 99), (48, 0, 0, 0, 98, 0)]:
        plan = PurchasePlan.of_units(units)
        assert (
            naive.repair(plan, scenario).units_for_serialization()
            == batched.repair(plan, scenario).units_for_serialization()
        )


def test_batched_repair_matches_under_tight_budgets() -> None:
    scenario = _reference_scenario()
    rng = random.Random(11)
    for reais in ["1.00", "50.00", "500.00", "987.44", "5000.00"]:
        budget = BudgetConstraint.from_reais(reais)
        naive, batched = BudgetAwarePlanRepair(budget), BatchedBudgetPlanRepair(budget)
        for _ in range(60):
            plan = PurchasePlan.of_units(tuple(rng.randint(0, 150) for _ in range(6)))
            assert (
                naive.repair(plan, scenario).units_for_serialization()
                == batched.repair(plan, scenario).units_for_serialization()
            ), f"divergiu com orcamento {reais}"
