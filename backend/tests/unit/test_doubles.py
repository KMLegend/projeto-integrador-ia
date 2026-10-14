from application.dto.optimization_outcome import OptimizationOutcome
from application.ports.task_result_store import TaskResultStore
from domain.evolution.generation_report import GenerationReport
from domain.forecasting.stock_snapshot import StockSnapshot
from domain.forecasting.stock_snapshots import StockSnapshots
from domain.model.fitness_score import FitnessScore
from domain.model.purchase_plan import PurchasePlan
from domain.model.task_id import TaskId
from domain.ports.demand_forecaster import DemandForecaster
from domain.ports.evolution_observer import EvolutionObserver
from tests.doubles.fixed_demand_forecaster import FixedDemandForecaster
from tests.doubles.in_memory_task_result_store import InMemoryTaskResultStore
from tests.doubles.recording_evolution_observer import RecordingEvolutionObserver


def test_fixed_demand_forecaster_implements_protocol() -> None:
    forecaster: DemandForecaster = FixedDemandForecaster({"CAFE-500G": 60})
    snap = StockSnapshot.create("CAFE-500G", "Café 500g", "2026-03-01", 100, 50, 200, 15.0, 0)
    snaps = StockSnapshots.of_snapshots([snap])

    forecasts = forecaster.forecast(snaps)
    assert forecasts.size() == 1
    assert forecasts.for_sku(snap.sku()).units_value() == 60


def test_recording_evolution_observer_implements_protocol() -> None:
    observer: EvolutionObserver = RecordingEvolutionObserver()
    report = GenerationReport(0, FitnessScore(100.5))

    observer.on_generation(report)
    assert isinstance(observer, RecordingEvolutionObserver)
    assert observer.reports_count() == 1
    assert observer.last_report() == report


def test_in_memory_task_result_store_implements_protocol() -> None:
    store: TaskResultStore = InMemoryTaskResultStore()
    task_id = TaskId.of("task-test-123")
    outcome = OptimizationOutcome.processing(task_id.value_for_serialization())

    store.save(task_id, outcome)
    maybe = store.find(task_id)

    assert maybe.is_present()
    assert maybe.value().status == "PROCESSING"

    missing = store.find(TaskId.of("missing-id"))
    assert not missing.is_present()
