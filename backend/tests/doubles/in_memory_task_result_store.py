from application.dto.optimization_outcome import MaybeOutcome, OptimizationOutcome
from application.ports.task_result_store import TaskResultStore
from domain.model.task_id import TaskId


class InMemoryTaskResultStore(TaskResultStore):
    """Duble de TaskResultStore em memoria para testes sem Redis."""

    def __init__(self) -> None:
        self._results: dict[str, OptimizationOutcome] = {}

    def save(self, task_id: TaskId, outcome: OptimizationOutcome) -> None:
        self._results[task_id.value_for_serialization()] = outcome

    def find(self, task_id: TaskId) -> MaybeOutcome:
        key = task_id.value_for_serialization()
        if key not in self._results:
            return MaybeOutcome.empty()
        return MaybeOutcome.present(self._results[key])

    def count(self) -> int:
        return len(self._results)
