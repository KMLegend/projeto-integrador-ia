import csv
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from domain.errors.domain_errors import InvalidDatasetError
from domain.forecasting.feature_schema import FeatureSchema
from domain.forecasting.stock_snapshot import StockSnapshot

IDENTIFIER_COLUMNS: tuple[str, ...] = ("reference_date", "sku", "product")
TARGET_COLUMN: str = "future_demand"
REQUIRED_COLUMNS: tuple[str, ...] = (
    *IDENTIFIER_COLUMNS,
    *FeatureSchema.ORDERED_NAMES,
    TARGET_COLUMN,
)

INTEGER_COLUMNS: tuple[str, ...] = (
    "stock_on_hand",
    "weekly_outflow",
    "monthly_outflow",
    "promotion_flag",
    TARGET_COLUMN,
)


@dataclass(frozen=True, slots=True)
class CsvDatasetSchema:
    """Valida e converte linhas de CSV em snapshots de dominio (padrao da Secao 2)."""

    @staticmethod
    def required_columns() -> tuple[str, ...]:
        return REQUIRED_COLUMNS

    @staticmethod
    def ensure_header(header: Sequence[str] | None) -> None:
        present = set(header or ())
        missing = [column for column in REQUIRED_COLUMNS if column not in present]
        if missing:
            raise InvalidDatasetError(
                f"Colunas obrigatorias ausentes: {', '.join(missing)}. "
                f"Esperado: {', '.join(REQUIRED_COLUMNS)}."
            )

    @staticmethod
    def parse(text: str) -> tuple[StockSnapshot, ...]:
        reader = csv.DictReader(text.splitlines())
        CsvDatasetSchema.ensure_header(reader.fieldnames)
        snapshots = tuple(CsvDatasetSchema._rows_to_snapshots(reader))
        if not snapshots:
            raise InvalidDatasetError("Dataset sem nenhuma linha de dados.")
        return snapshots

    @staticmethod
    def _rows_to_snapshots(reader: csv.DictReader) -> Iterator[StockSnapshot]:  # type: ignore[type-arg]
        for line_number, row in enumerate(reader, start=2):
            yield CsvDatasetSchema._to_snapshot(row, line_number)

    @staticmethod
    def _to_snapshot(row: dict[str, str], line_number: int) -> StockSnapshot:
        values = CsvDatasetSchema._numeric_values(row, line_number)
        return StockSnapshot.create(
            sku=CsvDatasetSchema._text(row, "sku", line_number),
            product=CsvDatasetSchema._text(row, "product", line_number),
            reference_date=CsvDatasetSchema._text(row, "reference_date", line_number),
            stock_on_hand=int(values["stock_on_hand"]),
            weekly_outflow=int(values["weekly_outflow"]),
            monthly_outflow=int(values["monthly_outflow"]),
            unit_price=values["unit_price"],
            promotion_flag=int(values["promotion_flag"]),
            future_demand=int(values[TARGET_COLUMN]),
        )

    @staticmethod
    def _numeric_values(row: dict[str, str], line_number: int) -> dict[str, float]:
        columns = (*FeatureSchema.ORDERED_NAMES, TARGET_COLUMN)
        return {name: CsvDatasetSchema._number(row, name, line_number) for name in columns}

    @staticmethod
    def _text(row: dict[str, str], column: str, line_number: int) -> str:
        value = (row.get(column) or "").strip()
        if not value:
            raise InvalidDatasetError(f"Linha {line_number}: coluna '{column}' vazia.")
        return value

    @staticmethod
    def _number(row: dict[str, str], column: str, line_number: int) -> float:
        raw = (row.get(column) or "").strip().replace(",", ".")
        parsed = CsvDatasetSchema._to_float(raw, column, line_number)
        CsvDatasetSchema._ensure_non_negative(parsed, column, line_number)
        CsvDatasetSchema._ensure_integral(parsed, column, line_number)
        return parsed

    @staticmethod
    def _to_float(raw: str, column: str, line_number: int) -> float:
        try:
            return float(raw)
        except ValueError as err:
            raise InvalidDatasetError(
                f"Linha {line_number}: coluna '{column}' nao e numerica ('{raw}')."
            ) from err

    @staticmethod
    def _ensure_non_negative(value: float, column: str, line_number: int) -> None:
        if value < 0:
            raise InvalidDatasetError(f"Linha {line_number}: '{column}' negativo ({value}).")

    @staticmethod
    def _ensure_integral(value: float, column: str, line_number: int) -> None:
        if column in INTEGER_COLUMNS and value != int(value):
            raise InvalidDatasetError(
                f"Linha {line_number}: '{column}' deve ser inteiro ({value})."
            )
