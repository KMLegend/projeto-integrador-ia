import pytest

from domain.model.catalog_item import CatalogItem
from domain.model.money import Money
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_item import ReplenishmentItem
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy


def test_baseline_plan_golden_values(reference_scenario: ReplenishmentScenario) -> None:
    policy = WeightedFitnessPolicy.standard()
    baseline_plan = PurchasePlan.of_units((0, 8, 0, 0, 28, 0))

    assessment = policy.evaluate(baseline_plan, reference_scenario)

    assert assessment.fitness_value() == pytest.approx(236.5753, abs=1e-4)
    assert reference_scenario.total_cost_of(baseline_plan) == Money.from_reais("314.32")


def test_optimized_plan_golden_values(reference_scenario: ReplenishmentScenario) -> None:
    policy = WeightedFitnessPolicy.standard()
    optimized_plan = PurchasePlan.of_units((0, 22, 0, 0, 98, 0))

    assessment = policy.evaluate(optimized_plan, reference_scenario)

    assert assessment.fitness_value() == pytest.approx(816.9178, abs=1e-4)
    assert reference_scenario.total_cost_of(optimized_plan) == Money.from_reais("987.44")


def test_zero_need_scenario_yields_1000() -> None:
    policy = WeightedFitnessPolicy.standard()
    items = [
        ReplenishmentItem(CatalogItem(Sku("ARROZ-5KG"), UnitPrice.from_reais("29.89")), Quantity.zero()),
        ReplenishmentItem(CatalogItem(Sku("FEIJAO-1KG"), UnitPrice.from_reais("9.55")), Quantity.zero()),
    ]
    scenario = ReplenishmentScenario.of_items(items)
    plan = PurchasePlan.of_units((0, 0))

    assessment = policy.evaluate(plan, scenario)
    assert assessment.fitness_value() == 1000.0


def test_empty_plan_with_two_needed_items_yields_minus_10(reference_scenario: ReplenishmentScenario) -> None:
    policy = WeightedFitnessPolicy.standard()
    empty_plan = PurchasePlan.empty_like(reference_scenario)

    assessment = policy.evaluate(empty_plan, reference_scenario)
    # served_ratio = 0 -> 0 * 10 - 2 * 5 = -10
    assert assessment.fitness_value() == -10.0


def test_fitness_is_pure_function(reference_scenario: ReplenishmentScenario) -> None:
    policy = WeightedFitnessPolicy.standard()
    plan = PurchasePlan.of_units((0, 22, 0, 0, 98, 0))

    initial_assessment = policy.evaluate(plan, reference_scenario)
    for _ in range(1000):
        next_assessment = policy.evaluate(plan, reference_scenario)
        assert next_assessment.fitness_value() == initial_assessment.fitness_value()
