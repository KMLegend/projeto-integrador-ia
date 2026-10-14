from typing import Protocol

from application.dto.optimization_outcome import MaybeOutcome, OptimizationOutcome
from domain.model.task_id import TaskId


class TaskResultStore(Protocol):
    """Porta para persistencia e consulta de resultados de otimizacao assincrona."""

    def save(self, task_id: TaskId, outcome: OptimizationOutcome) -> None:
        """Salva o resultado associado ao identificador da tarefa."""
        ...

    def find(self, task_id: TaskId) -> MaybeOutcome:
        """Busca o resultado pelo identificador da tarefa."""
        ...
