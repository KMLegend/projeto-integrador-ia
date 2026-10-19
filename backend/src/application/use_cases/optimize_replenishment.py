from dataclasses import dataclass

from application.dto.optimization_outcome import OptimizationOutcome
from application.dto.optimization_presenter import OptimizationPresenter
from application.dto.optimization_request import OptimizationRequest
from application.ports.task_result_store import TaskResultStore
from application.use_cases.build_replenishment_scenario import BuildReplenishmentScenario
from application.use_cases.compare_replenishment_strategies import (
    CompareReplenishmentStrategies,
)
from domain.evolution.evolution_engine import EvolutionEngine
from domain.evolution.null_evolution_observer import NullEvolutionObserver
from domain.model.task_id import TaskId
from domain.ports.evolution_observer import EvolutionObserver


@dataclass(frozen=True, slots=True)
class OptimizationEngines:  # OC-8: Agrupador de servicos para o orquestrador
    """Servicos colaboradores para execucao da otimizacao."""

    build_scenario: BuildReplenishmentScenario
    evolution_engine: EvolutionEngine
    compare_strategies: CompareReplenishmentStrategies


class OptimizeReplenishment:
    """Caso de uso orquestrador do fluxo completo de otimizacao genetica."""

    def __init__(
        self,
        engines: OptimizationEngines,
        result_store: TaskResultStore,
    ) -> None:
        self._engines = engines
        self._result_store = result_store

    def execute(  # OC-8: Orquestrador do caso de uso de otimizacao genetica
        self,
        request: OptimizationRequest,
        observer: EvolutionObserver | None = None,
    ) -> OptimizationOutcome:
        scenario, context = self._engines.build_scenario.execute_with_context(
            request.to_replenishment_cycle()
        )
        obs = observer or NullEvolutionObserver()
        evolution_result = self._engines.evolution_engine.evolve(scenario, obs)
        comparison = self._engines.compare_strategies.execute(
            scenario, evolution_result.best_plan()
        )
        outcome = OptimizationPresenter.build_outcome(
            request, scenario, evolution_result, comparison, context
        )
        self._result_store.save(TaskId.of(request.task_id), outcome)
        return outcome
