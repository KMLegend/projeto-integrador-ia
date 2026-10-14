from uuid import uuid4

from fastapi import APIRouter, status

from api.schemas.requests import OptimizeRequestSchema
from api.schemas.responses import OptimizeAcceptedResponse
from core.celery_app import celery_app

router = APIRouter(prefix="/api/v1", tags=["optimization"])


@router.post(
    "/optimize",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=OptimizeAcceptedResponse,
)
def trigger_optimization(payload: OptimizeRequestSchema) -> OptimizeAcceptedResponse:
    """Dispara o processo assincrono de otimizacao genetica."""
    task_id = str(uuid4())
    dict_payload = payload.model_dump()
    dict_payload["task_id"] = task_id

    celery_app.send_task(
        "optimization.run",
        args=[dict_payload],
        queue="optimization_queue",
        task_id=task_id,
    )

    return OptimizeAcceptedResponse(
        task_id=task_id,
        status="PROCESSING",
        message="Algoritmo genético iniciado em background.",
    )
