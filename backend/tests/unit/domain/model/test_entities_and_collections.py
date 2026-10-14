from domain.model.money import Money
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_item import ReplenishmentItem
from domain.model.replenishment_scenario import ReplenishmentScenario


def test_reference_scenario_fixture_values(reference_scenario: ReplenishmentScenario) -> None:
    assert reference_scenario.size() == 6
    assert reference_scenario.required_total() == Quantity.of(146)
    assert reference_scenario.total_required_cost() == Money.from_reais("1475.72")


def test_replenishment_item_structure_has_two_attributes(reference_scenario: ReplenishmentScenario) -> None:
    item = reference_scenario.item_at(Position(1))
    assert hasattr(item, "_catalog_item")
    assert hasattr(item, "_required_quantity")
    # Verifica que tem exatamente 2 atributos de instancia (regra 8 do Object Calisthenics)
    assert len(item.__slots__) == 2


def test_purchase_plan_immutability_and_operations(reference_scenario: ReplenishmentScenario) -> None:
    empty_plan = PurchasePlan.empty_like(reference_scenario)
    assert empty_plan.size() == 6
    assert empty_plan.total_units() == Quantity.zero()
    assert len(empty_plan.non_empty_positions()) == 0

    plan_with_units = empty_plan.with_quantity_at(Position(1), Quantity.of(22))
    assert plan_with_units is not empty_plan
    assert empty_plan.quantity_at(Position(1)) == Quantity.zero()
    assert plan_with_units.quantity_at(Position(1)) == Quantity.of(22)
    assert plan_with_units.total_units() == Quantity.of(22)

    decremented = plan_with_units.decremented_at(Position(1))
    assert decremented is not plan_with_units
    assert decremented.quantity_at(Position(1)) == Quantity.of(21)

    ceilings = reference_scenario.required_quantities()
    plan_over_ceiling = PurchasePlan.of_units((10, 100, 5, 0, 200, 0))
    clamped = plan_over_ceiling.clamped_to(ceilings)
    # ceilings: (0, 48, 0, 0, 98, 0)
    assert clamped.units_for_serialization() == (0, 48, 0, 0, 98, 0)


def test_replenishment_scenario_cost_and_positions(reference_scenario: ReplenishmentScenario) -> None:
    # Plano otimo: [0, 22, 0, 0, 98, 0] -> custo R$ 987,44
    optimal_plan = PurchasePlan.of_units((0, 22, 0, 0, 98, 0))
    cost = reference_scenario.total_cost_of(optimal_plan)
    assert cost == Money.from_reais("987.44")

    # Item mais caro entre os candidatos nao vazios: pos 1 (Cafe R$ 18.78) e pos 4 (Leite R$ 5.86)
    most_expensive = reference_scenario.most_expensive_position_among(optimal_plan.non_empty_positions())
    assert most_expensive.is_present()
    assert most_expensive.value() == Position(1)

    # Itens com demanda sao pos 1 (Cafe) e pos 4 (Leite)
    demands = reference_scenario.positions_with_demand()
    assert demands == (Position(1), Position(4))
