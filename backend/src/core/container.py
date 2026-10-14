from application.decorators.throttled_evolution_observer import (
    ThrottleConfig,
    ThrottledEvolutionObserver,
)
from application.ports.progress_publisher import ProgressPublisher
from application.ports.progress_subscriber import ProgressSubscriber
from application.ports.task_result_store import TaskResultStore
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
from core.config import Settings
from domain.errors.domain_errors import UnknownDatasetError
from domain.evolution.evolution_engine import EvolutionEngine
from domain.evolution.evolution_operators import EvolutionOperators
from domain.evolution.evolution_settings import EvolutionSettings
from domain.model.budget_constraint import BudgetConstraint
from domain.policy.budget_aware_plan_repair import BudgetAwarePlanRepair
from domain.policy.coverage_calculator import CoverageCalculator
from domain.policy.naive_replenishment_policy import NaiveReplenishmentPolicy
from domain.policy.stock_risk_classifier import StockRiskClassifier
from domain.policy.weighted_fitness_policy import WeightedFitnessPolicy
from domain.ports.demand_forecaster import DemandForecaster
from domain.ports.evolution_observer import EvolutionObserver
from domain.ports.stock_history_repository import StockHistoryRepository


def build_stock_history_repository(dataset_reference: str) -> StockHistoryRepository:
    """Resolve identificador logico para implementacao de repositorio (D-07)."""
    if dataset_reference in ("historico_mensal_v1", "default"):
        from infrastructure.dataset.simulated_stock_history_repository import (
            SimulatedStockHistoryRepository,
        )

        return SimulatedStockHistoryRepository()
    raise UnknownDatasetError(f"Referencia de dataset desconhecida: {dataset_reference}")


def build_demand_forecaster(settings: Settings) -> DemandForecaster:
    """Constroi o forecaster lazy com cache em processo e memoizacao por SKU."""
    from infrastructure.dataset.simulated_stock_history_repository import (
        SimulatedStockHistoryRepository,
    )
    from infrastructure.forecasting.cached_demand_forecaster import CachedDemandForecaster
    from infrastructure.forecasting.model_store import ModelStore

    store = ModelStore(settings.model_store_path)
    base_forecaster = store.get_or_train_forecaster(
        SimulatedStockHistoryRepository(),
        seed=settings.default_random_seed,
    )
    return CachedDemandForecaster(base_forecaster)


def build_task_result_store(settings: Settings) -> TaskResultStore:
    """Constroi o adaptador Redis para armazenamento de resultados."""
    from infrastructure.persistence.redis_task_result_store import RedisTaskResultStore

    return RedisTaskResultStore(redis_url=settings.redis_result_url)


def build_progress_publisher(settings: Settings, task_id: str) -> ProgressPublisher:
    """Constroi o publicador Pub/Sub no Redis."""
    from infrastructure.messaging.redis_progress_publisher import RedisProgressPublisher

    return RedisProgressPublisher(task_id=task_id, redis_url=settings.redis_url)


def build_progress_subscriber(settings: Settings) -> ProgressSubscriber:
    """Constroi o assinante Pub/Sub no Redis para WebSockets."""
    from infrastructure.messaging.redis_progress_subscriber import RedisProgressSubscriber

    return RedisProgressSubscriber(redis_url=settings.redis_url)


def build_evolution_observer(
    settings: Settings,
    task_id: str,
    generations: int,
) -> EvolutionObserver:
    """Constroi observer de progresso com throttle (inclui geracao 0 e ultima)."""
    publisher = build_progress_publisher(settings, task_id)
    config = ThrottleConfig(
        target_generations=generations,
        every=settings.progress_every_generations,
    )
    return ThrottledEvolutionObserver(publisher, config)


def build_optimization_use_case(
    settings: Settings,
    dataset_reference: str = "historico_mensal_v1",
) -> OptimizeReplenishment:
    """Composicao completa do caso de uso de otimizacao genetica."""
    from infrastructure.randomness.seeded_random_source import SeededRandomSource

    repository = build_stock_history_repository(dataset_reference)
    forecaster = build_demand_forecaster(settings)
    build_scenario = BuildReplenishmentScenario(repository, forecaster)

    random_source = SeededRandomSource(settings.default_random_seed)
    coverage_calc = CoverageCalculator()
    fitness_policy = WeightedFitnessPolicy.standard()
    budget = BudgetConstraint.from_reais(settings.default_budget_limit)
    repair = BudgetAwarePlanRepair(budget)

    operators = EvolutionOperators.standard(random_source, repair, fitness_policy)
    engine_settings = EvolutionSettings.notebook_defaults()
    engine = EvolutionEngine(engine_settings, operators)

    naive_policy = NaiveReplenishmentPolicy(repair)
    compare_policies = ComparisonPolicies(fitness_policy, naive_policy, coverage_calc)
    compare_strategies = CompareReplenishmentStrategies(compare_policies, budget)

    engines = OptimizationEngines(build_scenario, engine, compare_strategies)
    result_store = build_task_result_store(settings)
    return OptimizeReplenishment(engines, result_store)


def build_read_status_use_case(settings: Settings) -> ReadOptimizationStatus:
    """Composicao do caso de uso de leitura de status da tarefa."""
    return ReadOptimizationStatus(build_task_result_store(settings))


def build_classify_risk_use_case(settings: Settings) -> ClassifyStockRisk:
    """Composicao do caso de uso de classificacao de risco de estoque."""
    forecaster = build_demand_forecaster(settings)
    classifier = StockRiskClassifier.standard()
    return ClassifyStockRisk(forecaster, classifier)
