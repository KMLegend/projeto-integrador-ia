from typing import Any

from domain.forecasting.stock_snapshot import StockSnapshot
from domain.model.catalog_item import CatalogItem
from domain.model.quantity import Quantity
from domain.model.replenishment_cycle import ReplenishmentCycle
from domain.model.replenishment_item import ReplenishmentItem
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.unit_price import UnitPrice
from domain.ports.demand_forecaster import DemandForecaster
from domain.ports.stock_history_repository import StockHistoryRepository


class BuildReplenishmentScenario:
    """Caso de uso para construcao do cenario de reposicao a partir de historico e previsao."""

    def __init__(
        self,
        repository: StockHistoryRepository,
        forecaster: DemandForecaster,
    ) -> None:
        self._repository = repository
        self._forecaster = forecaster

    def execute(
        self, cycle: ReplenishmentCycle
    ) -> ReplenishmentScenario:  # OC-8: Orquestrador do cenario
        snapshots = self._repository.load_history()
        latest = snapshots.latest_per_product()
        forecasts = self._forecaster.forecast(latest)
        return ReplenishmentScenario.of_items(
            [self._build_item(snap, cycle, forecasts) for snap in latest.snapshots()]
        )

    def _build_item(
        self,
        snap: StockSnapshot,
        cycle: ReplenishmentCycle,
        forecasts: Any,
    ) -> ReplenishmentItem:
        item = CatalogItem(snap.sku(), UnitPrice.from_reais(f"{snap.unit_price_float():.2f}"))
        req = self._calculate_net_required(snap, cycle, forecasts)
        return ReplenishmentItem(item, Quantity.of(req))

    @staticmethod
    def _calculate_net_required(
        snap: StockSnapshot,
        cycle: ReplenishmentCycle,
        forecasts: Any,
    ) -> int:
        forecast = forecasts.for_sku(snap.sku())
        demand = cycle.demand_for(forecast).units_value()
        return max(0, demand - snap.stock_on_hand())
