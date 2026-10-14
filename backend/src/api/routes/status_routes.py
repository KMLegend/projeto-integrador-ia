from fastapi import APIRouter

from api.schemas.responses import StatusResponseSchema
from core.config import get_settings
from core.container import build_read_status_use_case
from domain.errors.domain_errors import TaskNotFoundError
from domain.model.task_id import TaskId

router = APIRouter(prefix="/api/v1", tags=["status"])


@router.get("/status/{task_id}", response_model=StatusResponseSchema)
def read_task_status(task_id: str) -> StatusResponseSchema:
    """Consulta o status e o resultado de uma tarefa de otimizacao."""
    use_case = build_read_status_use_case(get_settings())
    status_view = use_case.execute(TaskId.of(task_id))

    if status_view.status == "NOT_FOUND":
        raise TaskNotFoundError(f"Tarefa {task_id} não encontrada.")

    return StatusResponseSchema(
        task_id=status_view.task_id,
        status=status_view.status,
        result=status_view.result,  # type: ignore[arg-type]
        error=dict(status_view.error) if status_view.error else None,
    )
