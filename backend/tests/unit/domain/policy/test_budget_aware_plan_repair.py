import random

from domain.model.budget_constraint import BudgetConstraint
from domain.model.money import Money
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair


def test_repair_idempotence(reference_scenario: ReplenishmentScenario) -> None:
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)

    # Plano excedendo orcamento e teto: 50 unidades de tudo
    initial_plan = PurchasePlan.of_units((50, 50, 50, 50, 50, 50))
    repaired_once = repair.repair(initial_plan, reference_scenario)
    repaired_twice = repair.repair(repaired_once, reference_scenario)

    assert repaired_once == repaired_twice
    assert not budget.is_exceeded_by(reference_scenario.total_cost_of(repaired_once))


def test_repair_removes_most_expensive_item_first(reference_scenario: ReplenishmentScenario) -> None:
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)

    # Demanda: Cafe=48 (R$ 18.78), Leite=98 (R$ 5.86). Custo total = R$ 1475.72
    # Atendendo tudo estoura o orcamento em R$ 475.72
    plan_with_all_demands = PurchasePlan.of_units((0, 48, 0, 0, 98, 0))
    repaired = repair.repair(plan_with_all_demands, reference_scenario)

    # Como o Cafe e mais caro (18.78 vs 5.86), remove 26 unidades de Cafe (26 * 18.78 = 488.28)
    # Restam 22 de Cafe e 98 de Leite -> Custo R$ 987.44 <= 1000.00
    assert repaired.units_for_serialization() == (0, 22, 0, 0, 98, 0)
    assert reference_scenario.total_cost_of(repaired) == Money.from_reais("987.44")


def test_budget_smaller_than_cheapest_item(reference_scenario: ReplenishmentScenario) -> None:
    # O item mais barato e o Detergente (R$ 3.07) ou Leite (R$ 5.86)
    # Com orcamento de R$ 1.00 nao cabe nada
    tiny_budget = BudgetConstraint.from_reais("1.00")
    repair = BudgetAwarePlanRepair(tiny_budget)

    plan = PurchasePlan.of_units((10, 10, 10, 10, 10, 10))
    repaired = repair.repair(plan, reference_scenario)
    assert repaired.units_for_serialization() == (0, 0, 0, 0, 0, 0)


def test_repair_property_1000_random_plans(reference_scenario: ReplenishmentScenario) -> None:
    rng = random.Random(42)
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    ceilings = reference_scenario.required_quantities()

    for _ in range(1000):
        random_units = tuple(rng.randint(0, 150) for _ in range(reference_scenario.size()))
        plan = PurchasePlan.of_units(random_units)
        repaired = repair.repair(plan, reference_scenario)

        # Invariante 2: nenhum purchase_quantity e negativo
        for idx in range(reference_scenario.size()):
            assert repaired.quantity_at(Position(idx)).units_value() >= 0

        # Invariante 3: nenhum purchase_quantity excede required_quantity
        for idx in range(reference_scenario.size()):
            assert repaired.quantity_at(Position(idx)).units_value() <= ceilings[idx].units_value()

        # Invariante 4: total_cost <= budget_limit
        cost = reference_scenario.total_cost_of(repaired)
        assert not budget.is_exceeded_by(cost)
