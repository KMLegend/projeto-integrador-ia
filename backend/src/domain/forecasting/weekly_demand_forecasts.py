from collections.abc import Sequence
from dataclasses import dataclass

from domain.forecasting.weekly_demand_forecast import WeeklyDemandForecast
from domain.model.sku import Sku


@dataclass(frozen=True, slots=True)
class WeeklyDemandForecasts:
    """Colecao de previsoes de demanda semanal por produto."""

    _entries: tuple[tuple[Sku, WeeklyDemandForecast], ...]

    @staticmethod
    def of_entries(entries: Sequence[tuple[Sku, WeeklyDemandForecast]]) -> "WeeklyDemandForecasts":
        return WeeklyDemandForecasts(tuple(entries))

    def size(self) -> int:
        return len(self._entries)

    def for_sku(self, sku: Sku) -> WeeklyDemandForecast:
        for item_sku, forecast in self._entries:
            if item_sku.matches(sku):
                return forecast
        raise KeyError(f"Previsao nao encontrada para SKU: {sku.value_for_serialization()}")

    def entries(self) -> tuple[tuple[Sku, WeeklyDemandForecast], ...]:
        return self._entries
