import hypothesis.strategies as st
from hypothesis import given, settings

from domain.evolution.evolution_engine import EvolutionEngine
from domain.evolution.evolution_operators import EvolutionOperators
from domain.evolution.evolution_settings import EvolutionSettings
from domain.model.budget_constraint import BudgetConstraint
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.policy.coverage_calculator import CoverageCalculator
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy
from infrastructure.randomness.seeded_random_source import SeededRandomSource

# Strategy for 6-item integer plan quantities
plan_quantities = st.lists(st.integers(min_value=0, max_value=300), min_size=6, max_size=6)


@given(units=plan_quantities)
@settings(max_examples=100)
def test_property_repair_viability(
    reference_scenario: ReplenishmentScenario, units: list[int]
) -> None:
    """1. Viabilidade: repair devolve plano dentro do orcamento e da necessidade."""
    constraint = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(constraint)
    plan = PurchasePlan.of_units(tuple(units))
    repaired = repair.repair(plan, reference_scenario)

    assert not constraint.is_exceeded_by(reference_scenario.total_cost_of(repaired))
    for idx in range(reference_scenario.size()):
        pos = Position(idx)
        required = reference_scenario.item_at(pos).required_quantity()
        assert not repaired.quantity_at(pos).is_greater_than(required)


@given(units=plan_quantities)
@settings(max_examples=100)
def test_property_repair_idempotence(
    reference_scenario: ReplenishmentScenario, units: list[int]
) -> None:
    """2. Idempotencia: repair(repair(p)) == repair(p)."""
    constraint = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(constraint)
    plan = PurchasePlan.of_units(tuple(units))
    repaired_once = repair.repair(plan, reference_scenario)
    repaired_twice = repair.repair(repaired_once, reference_scenario)

    assert repaired_once == repaired_twice


@given(units=plan_quantities)
@settings(max_examples=100)
def test_property_served_ratio_range(
    reference_scenario: ReplenishmentScenario, units: list[int]
) -> None:
    """3. Faixa de served_ratio: 0 <= served_ratio <= 100 para qualquer plano reparado."""
    constraint = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(constraint)
    plan = PurchasePlan.of_units(tuple(units))
    repaired = repair.repair(plan, reference_scenario)
    calculator = CoverageCalculator()
    report = calculator.report_for(repaired, reference_scenario)

    ratio = report.served_ratio_points()
    assert 0.0 <= ratio <= 100.0


@given(seed=st.integers(min_value=1, max_value=500))
@settings(max_examples=10)
def test_property_history_monotonicity(
    reference_scenario: ReplenishmentScenario, seed: int
) -> None:
    """4. Monotonicidade do historico: elitismo garante que best fitness nunca decresce."""
    random_source = SeededRandomSource(seed)
    constraint = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(constraint)
    policy = WeightedFitnessPolicy.standard()
    operators = EvolutionOperators.standard(
        random_source=random_source,
        repair=repair,
        policy=policy,
        parents_size=10,
    )
    # 5 generations, population 20 for fast property checking
    settings_obj = EvolutionSettings(20, 5, 0.20, 10, 2, 10, seed)
    engine = EvolutionEngine(settings_obj, operators)

    result = engine.evolve(reference_scenario)
    history = result.history().reports()

    for idx in range(len(history) - 1):
        assert history[idx].best_fitness().value() <= history[idx + 1].best_fitness().value()


@given(seed=st.integers(min_value=1, max_value=500))
@settings(max_examples=10)
def test_property_determinism_by_seed(reference_scenario: ReplenishmentScenario, seed: int) -> None:
    """5. Determinismo: mesma semente => mesmo resultado exato."""

    def run_with_seed() -> tuple[PurchasePlan, float]:
        random_source = SeededRandomSource(seed)
        constraint = BudgetConstraint.from_reais("1000.00")
        repair = BudgetAwarePlanRepair(constraint)
        policy = WeightedFitnessPolicy.standard()
        operators = EvolutionOperators.standard(
            random_source=random_source,
            repair=repair,
            policy=policy,
            parents_size=10,
        )
        settings_obj = EvolutionSettings(20, 5, 0.20, 10, 2, 10, seed)
        engine = EvolutionEngine(settings_obj, operators)
        res = engine.evolve(reference_scenario)
        return res.best_plan(), res.best_fitness().value_for_serialization()

    plan_1, fitness_1 = run_with_seed()
    plan_2, fitness_2 = run_with_seed()

    assert plan_1 == plan_2
    assert fitness_1 == fitness_2


@given(units=plan_quantities)
@settings(max_examples=50)
def test_property_evaluate_purity(
    reference_scenario: ReplenishmentScenario, units: list[int]
) -> None:
    """6. Pureza do evaluate: evaluate chamado repetidas vezes devolve o mesmo valor."""
    policy = WeightedFitnessPolicy.standard()
    plan = PurchasePlan.of_units(tuple(units))

    first_eval = policy.evaluate(plan, reference_scenario)
    for _ in range(5):
        repeat_eval = policy.evaluate(plan, reference_scenario)
        assert first_eval.fitness_value() == repeat_eval.fitness_value()
