from domain.forecasting.stock_snapshots import StockSnapshots
from domain.ports.stock_history_repository import StockHistoryRepository
from infrastructure.dataset.synthetic_dataset_generator import SyntheticDatasetGenerator


class SimulatedStockHistoryRepository(StockHistoryRepository):
    """Adaptador de repositorio que gera historico sintetico sob demanda."""

    def __init__(self, generator: SyntheticDatasetGenerator | None = None) -> None:
        self._generator = generator or SyntheticDatasetGenerator(seed=42)

    def load_history(self) -> StockSnapshots:
        return self._generator.generate()
