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
            return self._not_found_view(task_id)
        return maybe.value().to_status_view()

    @staticmethod
    def _not_found_view(task_id: TaskId) -> OptimizationStatusView:
        tid = task_id.value_for_serialization()
        err = {"code": "404", "message": f"Tarefa {tid} nao encontrada"}
        return OptimizationStatusView(task_id=tid, status="NOT_FOUND", error=err)
