from fastapi import APIRouter, File, Form, UploadFile, status

from api.schemas.responses import DatasetListResponse, DatasetSummaryResponse
from application.use_cases.list_datasets import ListDatasets
from application.use_cases.register_dataset import RegisterDataset
from core.config import get_settings
from core.container import build_dataset_catalog
from domain.errors.domain_errors import InvalidDatasetError

router = APIRouter(prefix="/api/v1", tags=["datasets"])

MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def _decode(raw: bytes) -> str:
    if len(raw) > MAX_UPLOAD_BYTES:
        raise InvalidDatasetError("Arquivo acima do limite de 20 MB.")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as err:
        raise InvalidDatasetError("Arquivo nao esta em UTF-8.") from err


def _reference_from(name: str | None, upload: UploadFile) -> str:
    chosen = (name or "").strip() or (upload.filename or "").rsplit("/", 1)[-1]
    return chosen.removesuffix(".csv").strip()


@router.get("/datasets", response_model=DatasetListResponse)
def list_datasets() -> DatasetListResponse:
    """Lista os datasets disponiveis para otimizacao."""
    use_case = ListDatasets(build_dataset_catalog(get_settings()))
    summaries = use_case.execute()
    return DatasetListResponse(
        required_columns=list(use_case.required_columns()),
        datasets=[DatasetSummaryResponse(**summary.to_dict()) for summary in summaries],  # type: ignore[arg-type]
    )


@router.post(
    "/datasets",
    response_model=DatasetSummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset(
    file: UploadFile = File(...),  # noqa: B008
    reference: str | None = Form(default=None),  # noqa: B008
) -> DatasetSummaryResponse:
    """Recebe um CSV padronizado, valida o schema e registra o dataset."""
    content = _decode(await file.read())
    catalog = build_dataset_catalog(get_settings())
    summary = RegisterDataset(catalog).execute(_reference_from(reference, file), content)
    return DatasetSummaryResponse(**summary.to_dict())  # type: ignore[arg-type]
