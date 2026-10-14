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

    def execute(self, cycle: ReplenishmentCycle) -> ReplenishmentScenario:
        snapshots = self._repository.load_history()
        latest_snapshots = snapshots.latest_per_product()
        forecasts = self._forecaster.forecast(latest_snapshots)

        items: list[ReplenishmentItem] = []
        for snap in latest_snapshots.snapshots():
            sku = snap.sku()
            unit_price = UnitPrice.from_reais(f"{snap.unit_price_float():.2f}")
            forecast = forecasts.for_sku(sku)

            cycle_demand = cycle.demand_for(forecast).units_value()
            stock_on_hand = snap.stock_on_hand()
            net_required = max(0, cycle_demand - stock_on_hand)

            catalog_item = CatalogItem(sku, unit_price)
            item = ReplenishmentItem(catalog_item, Quantity.of(net_required))
            items.append(item)

        return ReplenishmentScenario.of_items(items)
