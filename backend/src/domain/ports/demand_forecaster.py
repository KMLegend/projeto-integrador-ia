from typing import Protocol

from domain.forecasting.stock_snapshots import StockSnapshots
from domain.forecasting.weekly_demand_forecasts import WeeklyDemandForecasts


class DemandForecaster(Protocol):
    """Porta para previsao de demanda semanal a partir de snapshots de historico."""

    def forecast(self, snapshots: StockSnapshots) -> WeeklyDemandForecasts:
        """Devolve a demanda semanal prevista para cada produto do historico."""
        ...
