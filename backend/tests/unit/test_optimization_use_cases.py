from application.dto.optimization_request import OptimizationRequest
from application.use_cases.build_replenishment_scenario import BuildReplenishmentScenario
from application.use_cases.classify_stock_risk import ClassifyStockRisk
from application.use_cases.compare_replenishment_strategies import (
    CompareReplenishmentStrategies,
    ComparisonPolicies,
)
from application.use_cases.optimize_replenishment import (
    OptimizationEngines,
    OptimizeReplenishment,
)
from application.use_cases.read_optimization_status import ReadOptimizationStatus
from domain.evolution.evolution_engine import EvolutionEngine
from domain.evolution.evolution_operators import EvolutionOperators
from domain.evolution.evolution_settings import EvolutionSettings
from domain.model.budget_constraint import BudgetConstraint
from domain.model.fitness_weights import FitnessWeights
from domain.model.money import Money
from domain.model.purchase_plan import PurchasePlan
from domain.model.stock_risk_level import StockRiskLevel
from domain.model.task_id import TaskId
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.policy.coverage_calculator import CoverageCalculator
from domain.policy.naive_replenishment_policy import NaiveReplenishmentPolicy
from domain.policy.stock_risk_classifier import StockRiskClassifier
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy
from infrastructure.dataset.simulated_stock_history_repository import (
    SimulatedStockHistoryRepository,
)
from infrastructure.randomness.seeded_random_source import SeededRandomSource
from tests.doubles.fixed_demand_forecaster import FixedDemandForecaster
from tests.doubles.in_memory_task_result_store import InMemoryTaskResultStore


def _build_test_engines() -> tuple[OptimizationEngines, InMemoryTaskResultStore]:
    repository = SimulatedStockHistoryRepository()
    forecaster = FixedDemandForecaster()
    build_scenario = BuildReplenishmentScenario(repository, forecaster)

    random_source = SeededRandomSource(42)
    coverage_calc = CoverageCalculator()
    fitness_policy = WeightedFitnessPolicy.standard()
    budget = BudgetConstraint.from_reais("1000.00")
    repair = BudgetAwarePlanRepair(budget)
    operators = EvolutionOperators.standard(random_source, repair, fitness_policy)
    settings = EvolutionSettings.notebook_defaults()
    evolution_engine = EvolutionEngine(settings, operators)

    naive_policy = NaiveReplenishmentPolicy(repair)
    compare_policies = ComparisonPolicies(fitness_policy, naive_policy, coverage_calc)
    compare_strategies = CompareReplenishmentStrategies(compare_policies, budget)

    engines = OptimizationEngines(build_scenario, evolution_engine, compare_strategies)
    store = InMemoryTaskResultStore()
    return engines, store


def test_optimize_replenishment_produces_exact_golden_outcomes() -> None:
    engines, store = _build_test_engines()
    orchestrator = OptimizeReplenishment(engines, store)

    request = OptimizationRequest(task_id="opt-task-001", random_seed=42)
    outcome = orchestrator.execute(request)

    assert outcome.status == "COMPLETED"
    assert outcome.task_id == "opt-task-001"

    # Verificacao do resumo do melhor cenario
    summary = outcome.best_scenario_summary
    assert summary is not None
    assert summary["total_cost"] == 987.44
    assert summary["budget_limit"] == 1000.00
    assert summary["budget_usage_ratio"] == 98.7
    assert summary["served_quantity"] == 120
    assert summary["required_total"] == 146
    assert summary["served_ratio"] == 82.2
    assert summary["items_at_risk"] == 1
    assert summary["fitness"] == 816.92

    # Verificacao dos itens a comprar (ordenados por line_cost decrescente)
    items_to_buy = outcome.items_to_buy
    assert items_to_buy is not None
    assert len(items_to_buy) == 2

    # Primeiro: Leite UHT 1L (custo 574.28)
    assert items_to_buy[0]["sku"] == "LEITE-UHT-1L"
    assert items_to_buy[0]["quantity"] == 98
    assert items_to_buy[0]["line_cost"] == 574.28
    assert items_to_buy[0]["uncovered_quantity"] == 0

    # Segundo: Café 500g (custo 413.16)
    assert items_to_buy[1]["sku"] == "CAFE-500G"
    assert items_to_buy[1]["quantity"] == 22
    assert items_to_buy[1]["line_cost"] == 413.16
    assert items_to_buy[1]["uncovered_quantity"] == 26

    # Verificacao do comparativo baseline vs otimizado
    comp = outcome.baseline_comparison
    assert comp is not None
    assert comp["baseline"]["total_cost"] == 314.32
    assert comp["baseline"]["served_quantity"] == 36
    assert comp["baseline"]["served_ratio"] == 24.7
    assert comp["baseline"]["items_at_risk"] == 2
    assert comp["baseline"]["fitness"] == 236.58

    assert comp["optimized"]["total_cost"] == 987.44
    assert comp["optimized"]["served_quantity"] == 120
    assert comp["optimized"]["served_ratio"] == 82.2
    assert comp["optimized"]["items_at_risk"] == 1
    assert comp["optimized"]["fitness"] == 816.92


def test_read_optimization_status_returns_view() -> None:
    engines, store = _build_test_engines()
    orchestrator = OptimizeReplenishment(engines, store)
    read_status = ReadOptimizationStatus(store)

    request = OptimizationRequest(task_id="task-view-123")
    orchestrator.execute(request)

    status_view = read_status.execute(TaskId.of("task-view-123"))
    assert status_view.status == "COMPLETED"
    assert status_view.task_id == "task-view-123"
    assert status_view.result is not None

    missing_view = read_status.execute(TaskId.of("unknown-task"))
    assert missing_view.status == "NOT_FOUND"
    assert missing_view.error is not None


def test_classify_stock_risk_use_case() -> None:
    repository = SimulatedStockHistoryRepository()
    forecaster = FixedDemandForecaster()
    classifier = StockRiskClassifier.standard()

    use_case = ClassifyStockRisk(forecaster, classifier)
    assessments = use_case.execute(repository.load_history())

    assert len(assessments) == 6
    risk_by_sku = {a.sku().value_for_serialization(): a.risk_level() for a in assessments}

    # Verifica que todos os produtos receberam classificacao de risco valida
    for level in risk_by_sku.values():
        assert level in (StockRiskLevel.ADEQUATE, StockRiskLevel.SHORTAGE, StockRiskLevel.EXCESS)
