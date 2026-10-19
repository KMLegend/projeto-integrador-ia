from uuid import uuid4

from fastapi import APIRouter, status

from api.schemas.requests import OptimizeRequestSchema
from api.schemas.responses import OptimizeAcceptedResponse
from application.dto.optimization_outcome import OptimizationOutcome
from core.celery_app import celery_app
from core.config import Settings, get_settings
from core.container import (
    BUILTIN_DATASET_REFERENCES,
    build_dataset_catalog,
    build_task_result_store,
)
from domain.errors.domain_errors import UnknownDatasetError
from domain.model.task_id import TaskId

router = APIRouter(prefix="/api/v1", tags=["optimization"])


def _ensure_known_dataset(reference: str, settings: Settings) -> None:
    """Valida a referencia na borda: embutidos ou datasets carregados (D-16, D-18)."""
    if reference in BUILTIN_DATASET_REFERENCES:
        return
    if build_dataset_catalog(settings).path_for(reference) is not None:
        return
    raise UnknownDatasetError(f"Dataset desconhecido: '{reference}'")


@router.post(
    "/optimize",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=OptimizeAcceptedResponse,
)
def trigger_optimization(payload: OptimizeRequestSchema) -> OptimizeAcceptedResponse:
    """Dispara o processo assincrono de otimizacao genetica."""
    settings = get_settings()
    _ensure_known_dataset(payload.dataset_reference, settings)

    task_id = str(uuid4())
    dict_payload = payload.model_dump()
    dict_payload["task_id"] = task_id

    store = build_task_result_store(settings)
    store.save(TaskId.of(task_id), OptimizationOutcome.processing(task_id))

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
