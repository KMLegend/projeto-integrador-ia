from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.errors.domain_errors import (
    DomainError,
    InvalidBudgetError,
    InvalidCycleError,
    InvalidDatasetError,
    InvalidParametersError,
    ModelNotAvailableError,
    NegativeQuantityError,
    TaskNotFoundError,
    UnknownDatasetError,
)

EXCEPTION_MAPPINGS: dict[type[DomainError], tuple[int, str]] = {
    InvalidBudgetError: (422, "INVALID_BUDGET"),
    InvalidCycleError: (422, "INVALID_CYCLE"),
    InvalidParametersError: (422, "INVALID_GA_PARAMETERS"),
    UnknownDatasetError: (422, "UNKNOWN_DATASET"),
    InvalidDatasetError: (422, "INVALID_DATASET"),
    TaskNotFoundError: (404, "TASK_NOT_FOUND"),
    ModelNotAvailableError: (503, "MODEL_UNAVAILABLE"),
    NegativeQuantityError: (500, "INTERNAL_INVARIANT_VIOLATION"),
}


def register_exception_handlers(app: FastAPI) -> None:
    """Registra tratadores globais de excecao para padronizar respostas de erro da API."""

    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        status_code, error_code = EXCEPTION_MAPPINGS.get(
            type(exc),
            (500, "INTERNAL_ERROR"),
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": str(exc),
                }
            },
        )
