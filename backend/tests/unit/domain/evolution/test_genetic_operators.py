from domain.evolution.local_shift_mutation import LocalShiftMutation
from domain.evolution.plan_factory import PlanFactory
from domain.evolution.population import Population
from domain.evolution.truncation_selection import TruncationSelection
from domain.evolution.uniform_crossover import UniformCrossover
from domain.model.budget_constraint import BudgetConstraint
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy
from tests.doubles.scripted_random_source import ScriptedRandomSource


def test_plan_factory_draws_within_required_and_repairs(reference_scenario: ReplenishmentScenario) -> None:
    # Cenario tem necessidades: 0, 48, 0, 0, 98, 0
    # Apenas itens 1 e 4 tem necessidade > 0
    # O scripted random source fornecera 30 para o item 1 e 50 para o item 4
    scripted_rng = ScriptedRandomSource(integers=[30, 50])
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    factory = PlanFactory(scripted_rng, repair)

    plan = factory.random_plan(reference_scenario)
    # Custo: 30 * 18.78 + 50 * 5.86 = 563.40 + 293.00 = 856.40 <= 1000.00
    assert plan.units_for_serialization() == (0, 30, 0, 0, 50, 0)


def test_uniform_crossover_gene_by_gene(reference_scenario: ReplenishmentScenario) -> None:
    # 6 genes no cenario. Sorteios de ratio:
    # pos 0: 0.1 (<0.5 -> primeiro)
    # pos 1: 0.8 (>=0.5 -> segundo)
    # pos 2: 0.3 (<0.5 -> primeiro)
    # pos 3: 0.7 (>=0.5 -> segundo)
    # pos 4: 0.2 (<0.5 -> primeiro)
    # pos 5: 0.9 (>=0.5 -> segundo)
    scripted_rng = ScriptedRandomSource(ratios=[0.1, 0.8, 0.3, 0.7, 0.2, 0.9])
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    crossover = UniformCrossover(scripted_rng, repair)

    parent_a = PurchasePlan.of_units((0, 20, 0, 0, 90, 0))
    parent_b = PurchasePlan.of_units((0, 10, 0, 0, 40, 0))

    # Filho esperado: [a[0]=0, b[1]=10, a[2]=0, b[3]=0, a[4]=90, b[5]=0]
    # Custo: 10 * 18.78 + 90 * 5.86 = 187.80 + 527.40 = 715.20 <= 1000.00
    child = crossover.combine(parent_a, parent_b, reference_scenario)
    assert child.units_for_serialization() == (0, 10, 0, 0, 90, 0)


def test_local_shift_mutation_triggers_and_applies_shift(reference_scenario: ReplenishmentScenario) -> None:
    # 1. Ratio para taxa de mutacao: 0.10 < 0.20 -> aciona
    # 2. Inteiro para posicao: 4 (Leite UHT 1L)
    # 3. Inteiro para variacao: +5 unidades
    scripted_rng = ScriptedRandomSource(ratios=[0.10], integers=[4, 5])
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    mutation = LocalShiftMutation(scripted_rng, repair)

    original_plan = PurchasePlan.of_units((0, 22, 0, 0, 90, 0))
    # Leite vai de 90 para 95 (teto e 98)
    # Custo: 22 * 18.78 + 95 * 5.86 = 413.16 + 556.70 = 969.86 <= 1000.00
    mutated = mutation.mutate(original_plan, reference_scenario)
    assert mutated.units_for_serialization() == (0, 22, 0, 0, 95, 0)


def test_local_shift_mutation_skips_when_ratio_above_rate(reference_scenario: ReplenishmentScenario) -> None:
    # Ratio 0.50 >= 0.20 -> nao muta
    scripted_rng = ScriptedRandomSource(ratios=[0.50])
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    mutation = LocalShiftMutation(scripted_rng, repair)

    original_plan = PurchasePlan.of_units((0, 22, 0, 0, 90, 0))
    mutated = mutation.mutate(original_plan, reference_scenario)
    assert mutated == original_plan


def test_truncation_selection(reference_scenario: ReplenishmentScenario) -> None:
    policy = WeightedFitnessPolicy.standard()
    plan_poor = PurchasePlan.of_units((0, 0, 0, 0, 0, 0))
    plan_mid = PurchasePlan.of_units((0, 8, 0, 0, 28, 0))
    plan_best = PurchasePlan.of_units((0, 22, 0, 0, 98, 0))

    population = Population.of_plans([plan_poor, plan_best, plan_mid])
    selection = TruncationSelection(_parents_size=2)

    parents = selection.select(population, policy, reference_scenario)
    assert parents.size() == 2
    assert parents.plan_at(0) == plan_best
    assert parents.plan_at(1) == plan_mid
