from domain.forecasting.stock_snapshots import StockSnapshots
from domain.forecasting.weekly_demand_forecast import WeeklyDemandForecast
from domain.forecasting.weekly_demand_forecasts import WeeklyDemandForecasts
from domain.model.sku import Sku
from domain.ports.demand_forecaster import DemandForecaster


class CachedDemandForecaster(DemandForecaster):
    """Decorator de DemandForecaster que realiza cache em memoria por SKU (OCP)."""

    def __init__(self, inner: DemandForecaster) -> None:
        self._inner = inner
        self._cache: dict[str, WeeklyDemandForecast] = {}

    def forecast(self, snapshots: StockSnapshots) -> WeeklyDemandForecasts:
        latest = snapshots.latest_per_product()
        missing_snapshots = [
            snap
            for snap in latest.snapshots()
            if snap.sku().value_for_serialization() not in self._cache
        ]

        if missing_snapshots:
            new_forecasts = self._inner.forecast(StockSnapshots.of_snapshots(missing_snapshots))
            for sku, forecast in new_forecasts.entries():
                self._cache[sku.value_for_serialization()] = forecast

        entries: list[tuple[Sku, WeeklyDemandForecast]] = [
            (snap.sku(), self._cache[snap.sku().value_for_serialization()])
            for snap in latest.snapshots()
        ]
        return WeeklyDemandForecasts.of_entries(entries)

    def cache_size(self) -> int:
        return len(self._cache)

    def clear_cache(self) -> None:
        self._cache.clear()

    def training_mae(self) -> float:
        inner = getattr(self._inner, "training_mae", None)
        return float(inner()) if callable(inner) else 0.0
