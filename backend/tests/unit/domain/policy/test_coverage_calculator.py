import pytest

from domain.model.catalog_item import CatalogItem
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_item import ReplenishmentItem
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice
from domain.policy.coverage_calculator import CoverageCalculator


def test_coverage_calculator_on_reference_scenario(reference_scenario: ReplenishmentScenario) -> None:
    calculator = CoverageCalculator()

    # Plano otimo: [0, 22, 0, 0, 98, 0] -> atende 120 de 146 (82.1918%), so Cafe fica em risco
    plan = PurchasePlan.of_units((0, 22, 0, 0, 98, 0))
    report = calculator.report_for(plan, reference_scenario)

    assert report.served_ratio_points() == pytest.approx(82.1918, abs=1e-4)
    assert report.items_at_risk_count() == 1


def test_edge_case_zero_need_scenario() -> None:
    calculator = CoverageCalculator()
    items = [
        ReplenishmentItem(CatalogItem(Sku("ARROZ-5KG"), UnitPrice.from_reais("29.89")), Quantity.zero()),
        ReplenishmentItem(CatalogItem(Sku("FEIJAO-1KG"), UnitPrice.from_reais("9.55")), Quantity.zero()),
    ]
    scenario = ReplenishmentScenario.of_items(items)
    plan = PurchasePlan.of_units((0, 0))

    report = calculator.report_for(plan, scenario)
    assert report.served_ratio_points() == 100.0
    assert report.items_at_risk_count() == 0


def test_edge_case_empty_scenario() -> None:
    calculator = CoverageCalculator()
    scenario = ReplenishmentScenario.of_items([])
    plan = PurchasePlan.of_units(())

    report = calculator.report_for(plan, scenario)
    assert report.served_ratio_points() == 100.0
    assert report.items_at_risk_count() == 0


def test_edge_case_empty_plan_with_existing_need(reference_scenario: ReplenishmentScenario) -> None:
    calculator = CoverageCalculator()
    plan = PurchasePlan.empty_like(reference_scenario)

    report = calculator.report_for(plan, reference_scenario)
    assert report.served_ratio_points() == 0.0
    # No cenario de referencia ha 2 itens com necessidade: Cafe (48) e Leite (98)
    assert report.items_at_risk_count() == 2


def test_item_with_zero_demand_never_counts_as_at_risk(reference_scenario: ReplenishmentScenario) -> None:
    calculator = CoverageCalculator()
    # Atende totalmente o Cafe (48) e Leite (98), mantem 0 nos que tem necessidade 0
    full_plan = PurchasePlan.of_units((0, 48, 0, 0, 98, 0))

    report = calculator.report_for(full_plan, reference_scenario)
    assert report.served_ratio_points() == 100.0
    assert report.items_at_risk_count() == 0
