from pathlib import Path

from domain.errors.domain_errors import InvalidDatasetError
from domain.forecasting.stock_snapshots import StockSnapshots
from domain.ports.stock_history_repository import StockHistoryRepository
from infrastructure.dataset.csv_dataset_schema import CsvDatasetSchema


class CsvStockHistoryRepository(StockHistoryRepository):
    """Adaptador que carrega historico de estoque a partir de um arquivo CSV."""

    def __init__(self, csv_path: Path | str) -> None:
        self._csv_path = Path(csv_path)

    def load_history(self) -> StockSnapshots:
        return StockSnapshots.of(CsvDatasetSchema.parse(self._read_text()))

    def _read_text(self) -> str:
        if not self._csv_path.exists():
            raise InvalidDatasetError(f"Arquivo de dataset nao encontrado: {self._csv_path}")
        return self._csv_path.read_text(encoding="utf-8-sig")
