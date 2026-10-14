import pytest
import redis

from application.decorators.throttled_evolution_observer import (
    ThrottleConfig,
    ThrottledEvolutionObserver,
)
from application.dto.optimization_outcome import OptimizationOutcome
from core.config import Settings
from core.container import (
    build_classify_risk_use_case,
    build_demand_forecaster,
    build_optimization_use_case,
    build_read_status_use_case,
    build_stock_history_repository,
    build_task_result_store,
)
from domain.errors.domain_errors import UnknownDatasetError
from domain.evolution.generation_report import GenerationReport
from domain.model.fitness_score import FitnessScore
from domain.model.task_id import TaskId
from infrastructure.messaging.redis_progress_publisher import RedisProgressPublisher
from infrastructure.persistence.redis_task_result_store import RedisTaskResultStore
from infrastructure.time.system_clock import SystemClock
from tests.doubles.recording_evolution_observer import RecordingEvolutionObserver


def test_container_resolves_known_and_unknown_dataset_references() -> None:
    repo = build_stock_history_repository("historico_mensal_v1")
    assert repo is not None

    with pytest.raises(UnknownDatasetError):
        build_stock_history_repository("invalid_erp_name")


def test_throttled_evolution_observer_always_includes_first_and_last_generations() -> None:
    recording = RecordingEvolutionObserver()
    config = ThrottleConfig(target_generations=100, every=10)
    throttled = ThrottledEvolutionObserver(recording, config)

    for gen in range(100):
        report = GenerationReport(gen, FitnessScore(float(gen)))
        throttled.on_generation(report)

    emitted_gens = [r.generation_number() for r in recording.reports()]

    # Obrigatorio: inclui geracao 0 (primeira)
    assert 0 in emitted_gens
    # Obrigatorio: inclui geracao 99 (ultima), mesmo 99 % 10 != 0
    assert 99 in emitted_gens
    # Inclui multiplos de 10
    assert 10 in emitted_gens
    assert 50 in emitted_gens
    assert 90 in emitted_gens
    # Nao inclui intermediarios
    assert 1 not in emitted_gens
    assert 15 not in emitted_gens


def test_redis_progress_publisher_does_not_crash_when_redis_unavailable() -> None:
    # URL invalida/inexistente para simular Redis indisponivel
    publisher = RedisProgressPublisher(
        task_id="test-task-no-redis",
        redis_url="redis://127.0.0.1:59999/0",
    )
    report = GenerationReport(0, FitnessScore(100.0))

    # Nao deve lancar excecao: deve capturar, logar e continuar
    publisher.on_generation(report)
    publisher.publish_terminal_state("completed")


def test_redis_task_result_store_save_and_find_with_real_redis() -> None:
    redis_url = "redis://localhost:6379/1"
    try:
        r = redis.Redis.from_url(redis_url)
        r.ping()
    except Exception:
        pytest.skip("Redis local nao disponivel para este teste")

    store = RedisTaskResultStore(redis_url=redis_url)
    task_id = TaskId.of("redis-test-task-888")
    outcome = OptimizationOutcome.processing(task_id.value_for_serialization())

    store.save(task_id, outcome)
    maybe = store.find(task_id)

    assert maybe.is_present()
    assert maybe.value().status == "PROCESSING"

    missing = store.find(TaskId.of("non-existent-task"))
    assert not missing.is_present()


def test_system_clock_returns_utc_datetime() -> None:
    clock = SystemClock()
    now = clock.now()
    assert now is not None
    assert now.tzinfo is not None


def test_container_builds_all_use_cases_without_error() -> None:
    settings = Settings(
        redis_url="redis://localhost:6379/0",
        redis_result_url="redis://localhost:6379/1",
        model_store_path="/tmp/test_container_model.joblib",
    )

    opt_use_case = build_optimization_use_case(settings)
    assert opt_use_case is not None

    status_use_case = build_read_status_use_case(settings)
    assert status_use_case is not None

    risk_use_case = build_classify_risk_use_case(settings)
    assert risk_use_case is not None
