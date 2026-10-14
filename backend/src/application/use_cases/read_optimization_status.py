from application.dto.optimization_outcome import OptimizationStatusView
from application.ports.task_result_store import TaskResultStore
from domain.model.task_id import TaskId


class ReadOptimizationStatus:
    """Caso de uso para leitura do estado e resultado de uma tarefa de otimizacao."""

    def __init__(self, store: TaskResultStore) -> None:
        self._store = store

    def execute(self, task_id: TaskId) -> OptimizationStatusView:
        maybe = self._store.find(task_id)
        if not maybe.is_present():
            return OptimizationStatusView(
                task_id=task_id.value_for_serialization(),
                status="NOT_FOUND",
                error={
                    "code": "404",
                    "message": f"Tarefa {task_id.value_for_serialization()} nao encontrada",
                },
            )

        outcome = maybe.value()
        result_payload = None
        if outcome.status == "COMPLETED":
            result_payload = {
                "best_scenario_summary": outcome.best_scenario_summary,
                "items_to_buy": outcome.items_to_buy,
                "baseline_comparison": outcome.baseline_comparison,
                "convergence_curve": outcome.convergence_curve,
                "model_metrics": outcome.model_metrics,
            }

        return OptimizationStatusView(
            task_id=outcome.task_id,
            status=outcome.status,
            result=result_payload,
            error=outcome.error,
        )
