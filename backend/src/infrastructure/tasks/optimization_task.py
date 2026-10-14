import logging
from typing import Any

from application.dto.optimization_outcome import OptimizationOutcome
from application.dto.optimization_request import OptimizationRequest
from application.dto.outcome_mapper import OutcomeMapper
from core.celery_app import celery_app
from core.config import get_settings
from core.container import (
    build_evolution_observer,
    build_optimization_use_case,
    build_progress_publisher,
    build_task_result_store,
)
from domain.errors.domain_errors import DomainError
from domain.model.task_id import TaskId

logger = logging.getLogger(__name__)

ERROR_CODE_MAP: dict[str, str] = {
    "InvalidBudgetError": "INVALID_BUDGET",
    "InvalidCycleError": "INVALID_CYCLE",
    "InvalidParametersError": "INVALID_GA_PARAMETERS",
    "NegativeQuantityError": "INTERNAL_INVARIANT_VIOLATION",
    "TaskNotFoundError": "TASK_NOT_FOUND",
    "ModelNotAvailableError": "MODEL_UNAVAILABLE",
    "UnknownDatasetError": "UNKNOWN_DATASET",
}


@celery_app.task(  # type: ignore[untyped-decorator]
    name="optimization.run",
    queue="optimization_queue",
    bind=True,
    max_retries=0,
)
def run_optimization(self: Any, payload: dict[str, Any]) -> dict[str, Any]:
    task_id = self.request.id or str(payload.get("task_id", "default-task"))
    payload["task_id"] = task_id
    settings = get_settings()

    publisher = build_progress_publisher(settings, task_id)
    store = build_task_result_store(settings)
    store.save(TaskId.of(task_id), OptimizationOutcome.processing(task_id))

    try:
        request = OptimizationRequest.from_payload(payload)
        observer = build_evolution_observer(settings, task_id, request.generations)
        use_case = build_optimization_use_case(settings, request.dataset_reference)
        outcome = use_case.execute(request, observer)
        publisher.publish_terminal_state("completed", generation=request.generations)
        return OutcomeMapper.to_payload(outcome)
    except DomainError as err:
        err_type = type(err).__name__
        err_code = ERROR_CODE_MAP.get(err_type, "DOMAIN_ERROR")
        logger.warning("Erro de dominio na otimizacao %s: %s (%s)", task_id, err_code, err)
        failed_outcome = OptimizationOutcome.failed(task_id, err_code, str(err))
        store.save(TaskId.of(task_id), failed_outcome)
        publisher.publish_terminal_state("failed")
        return OutcomeMapper.to_payload(failed_outcome)
    except Exception as err:
        logger.exception("Erro inesperado na otimizacao %s: %s", task_id, err)
        failed_outcome = OptimizationOutcome.failed(
            task_id, "INTERNAL_ERROR", "Erro interno durante a otimizacao"
        )
        store.save(TaskId.of(task_id), failed_outcome)
        publisher.publish_terminal_state("failed")
        return OutcomeMapper.to_payload(failed_outcome)
