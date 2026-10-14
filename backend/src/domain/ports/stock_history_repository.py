from typing import Protocol

from domain.forecasting.stock_snapshots import StockSnapshots


class StockHistoryRepository(Protocol):
    """Porta para carregamento de historico de snapshots de estoque."""

    def load_history(self) -> StockSnapshots:
        """Carrega e devolve os snapshots de historico."""
        ...
