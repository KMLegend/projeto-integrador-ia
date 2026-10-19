import json
import re
from datetime import UTC, datetime
from pathlib import Path

from application.dto.dataset_summary import DatasetSummary
from domain.errors.domain_errors import InvalidDatasetError
from infrastructure.dataset.csv_dataset_schema import CsvDatasetSchema

BUILTIN_REFERENCE = "historico_mensal_v1"
BUILTIN_SUMMARY = DatasetSummary(
    reference=BUILTIN_REFERENCE,
    rows=120,
    skus=6,
    uploaded_at="embutido",
    is_builtin=True,
)
REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class FilesystemDatasetCatalog:
    """Catalogo de datasets persistidos em volume compartilhado entre API e worker."""

    def __init__(self, store_path: Path | str) -> None:
        self._store_path = Path(store_path)

    def register(self, reference: str, content: str) -> DatasetSummary:
        self._ensure_valid_reference(reference)
        snapshots = CsvDatasetSchema.parse(content)
        self._store_path.mkdir(parents=True, exist_ok=True)
        self._csv_path(reference).write_text(content, encoding="utf-8")
        summary = DatasetSummary(
            reference=reference,
            rows=len(snapshots),
            skus=len({snap.sku().value_for_serialization() for snap in snapshots}),
            uploaded_at=datetime.now(UTC).isoformat(timespec="seconds"),
            is_builtin=False,
        )
        self._meta_path(reference).write_text(json.dumps(summary.to_dict()), encoding="utf-8")
        return summary

    def list_all(self) -> tuple[DatasetSummary, ...]:
        return (BUILTIN_SUMMARY, *sorted(self._uploaded(), key=lambda item: item.reference))

    def required_columns(self) -> tuple[str, ...]:
        return CsvDatasetSchema.required_columns()

    def path_for(self, reference: str) -> Path | None:
        candidate = self._csv_path(reference)
        return candidate if candidate.exists() else None

    def _uploaded(self) -> tuple[DatasetSummary, ...]:
        if not self._store_path.exists():
            return ()
        return tuple(self._summaries_from_disk())

    def _summaries_from_disk(self) -> list[DatasetSummary]:
        found: list[DatasetSummary] = []
        for meta in sorted(self._store_path.glob("*.json")):
            summary = self._read_summary(meta)
            if summary is not None:
                found.append(summary)
        return found

    @staticmethod
    def _read_summary(meta: Path) -> DatasetSummary | None:
        try:
            payload = json.loads(meta.read_text(encoding="utf-8"))
            return DatasetSummary(
                reference=str(payload["reference"]),
                rows=int(payload["rows"]),
                skus=int(payload["skus"]),
                uploaded_at=str(payload["uploaded_at"]),
                is_builtin=False,
            )
        except (OSError, ValueError, KeyError):
            return None

    def _csv_path(self, reference: str) -> Path:
        return self._store_path / f"{reference}.csv"

    def _meta_path(self, reference: str) -> Path:
        return self._store_path / f"{reference}.json"

    @staticmethod
    def _ensure_valid_reference(reference: str) -> None:
        if reference == BUILTIN_REFERENCE:
            raise InvalidDatasetError(
                f"'{BUILTIN_REFERENCE}' e o dataset embutido e nao pode ser sobrescrito."
            )
        if not REFERENCE_PATTERN.match(reference):
            raise InvalidDatasetError(
                "Nome do dataset deve ter de 1 a 64 caracteres entre letras, numeros, "
                "'.', '_' e '-', comecando por letra ou numero."
            )
