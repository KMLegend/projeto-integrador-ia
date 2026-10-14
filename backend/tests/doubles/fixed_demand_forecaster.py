from domain.forecasting.stock_snapshots import StockSnapshots
from domain.forecasting.weekly_demand_forecast import WeeklyDemandForecast
from domain.forecasting.weekly_demand_forecasts import WeeklyDemandForecasts
from domain.model.sku import Sku
from domain.ports.demand_forecaster import DemandForecaster


class FixedDemandForecaster(DemandForecaster):
    """Duble de DemandForecaster que devolve valores constantes sem usar sklearn."""

    def __init__(
        self,
        fixed_predictions: dict[str, int] | None = None,
        default_forecast: int = 50,
    ) -> None:
        self._predictions = fixed_predictions or {
            "ARROZ-5KG": 42,
            "CAFE-500G": 60,
            "DETERGENTE-500ML": 39,
            "FEIJAO-1KG": 46,
            "LEITE-UHT-1L": 81,
            "REFRIGERANTE-2L": 65,
        }
        self._default = default_forecast

    def forecast(self, snapshots: StockSnapshots) -> WeeklyDemandForecasts:
        latest = snapshots.latest_per_product()
        entries: list[tuple[Sku, WeeklyDemandForecast]] = []

        for snap in latest.snapshots():
            sku_str = snap.sku().value_for_serialization()
            units = self._predictions.get(sku_str, self._default)
            entries.append((snap.sku(), WeeklyDemandForecast.of(units)))

        return WeeklyDemandForecasts.of_entries(entries)
