import pytest

from domain.evolution.evolution_engine import EvolutionEngine
from domain.evolution.evolution_operators import EvolutionOperators
from domain.evolution.evolution_settings import EvolutionSettings
from domain.evolution.generation_report import GenerationReport
from domain.model.budget_constraint import BudgetConstraint
from domain.model.catalog_item import CatalogItem
from domain.model.money import Money
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_item import ReplenishmentItem
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy
from domain.ports.evolution_observer import EvolutionObserver
from infrastructure.randomness.seeded_random_source import SeededRandomSource
from tests.doubles.greedy_cheapest_first_policy import GreedyCheapestFirstPolicy


class InvariantCheckingObserver:
    """Observer de teste para checar que todo relatorio e plano e viavel."""

    def __init__(self, budget: BudgetConstraint, scenario: ReplenishmentScenario) -> None:
        self.reports: list[GenerationReport] = []
        self.budget = budget
        self.scenario = scenario

    def on_generation(self, report: GenerationReport) -> None:
        self.reports.append(report)


def test_evolution_engine_reproduces_notebook_golden_values(reference_scenario: ReplenishmentScenario) -> None:
    settings = EvolutionSettings.notebook_defaults()
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    policy = WeightedFitnessPolicy.standard()
    random_source = SeededRandomSource(settings.random_seed)

    operators = EvolutionOperators.standard(
        random_source=random_source,
        repair=repair,
        policy=policy,
        parents_size=settings.parents_size,
    )
    engine = EvolutionEngine(settings, operators)

    observer = InvariantCheckingObserver(budget, reference_scenario)
    result = engine.evolve(reference_scenario, observer)

    # 1. Plano otimo encontrado
    assert result.best_plan().units_for_serialization() == (0, 22, 0, 0, 98, 0)

    # 2. Custo do plano
    cost = reference_scenario.total_cost_of(result.best_plan())
    assert cost == Money.from_reais("987.44")

    # 3. Fitness
    assert result.best_fitness().value() == pytest.approx(816.9178, abs=1e-4)

    # 4. Historico
    history = result.history()
    assert history.size() == settings.generations
    # history[0] reflete o melhor da populacao inicial
    assert history.at(0).fitness_value() <= history.at(-1).fitness_value()
    assert history.at(-1).fitness_value() == pytest.approx(816.9178, abs=1e-4)
    # history e nao-decrescente por causa do elitismo
    for i in range(1, history.size()):
        assert history.at(i).fitness_value() >= history.at(i - 1).fitness_value() - 1e-6

    # 5. Empata com o guloso (otimo global provado)
    greedy_plan = GreedyCheapestFirstPolicy().build_plan(reference_scenario, budget)
    greedy_fitness = policy.evaluate(greedy_plan, reference_scenario).fitness_value()
    assert result.best_fitness().value() == pytest.approx(greedy_fitness, abs=1e-4)


def test_evolution_engine_degenerate_case(reference_scenario: ReplenishmentScenario) -> None:
    settings = EvolutionSettings(
        population_size=2,
        generations=1,
        mutation_rate=0.20,
        parents_size=2,
        elite_size=2,
        mutation_range=10,
        random_seed=42,
    )
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    policy = WeightedFitnessPolicy.standard()
    random_source = SeededRandomSource(42)

    operators = EvolutionOperators.standard(random_source, repair, policy, parents_size=2)
    engine = EvolutionEngine(settings, operators)

    result = engine.evolve(reference_scenario)
    assert result.history().size() == 1
    assert result.best_plan().size() == 6


def test_evolution_engine_zero_demand_scenario() -> None:
    settings = EvolutionSettings.notebook_defaults()
    items = [
        ReplenishmentItem(CatalogItem(Sku("ARROZ-5KG"), UnitPrice.from_reais("29.89")), Quantity.zero()),
        ReplenishmentItem(CatalogItem(Sku("FEIJAO-1KG"), UnitPrice.from_reais("9.55")), Quantity.zero()),
    ]
    zero_scenario = ReplenishmentScenario.of_items(items)

    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    policy = WeightedFitnessPolicy.standard()
    random_source = SeededRandomSource(42)

    operators = EvolutionOperators.standard(random_source, repair, policy, parents_size=20)
    engine = EvolutionEngine(settings, operators)

    result = engine.evolve(zero_scenario)
    assert result.best_plan().units_for_serialization() == (0, 0)
    assert result.best_fitness().value() == 1000.0
