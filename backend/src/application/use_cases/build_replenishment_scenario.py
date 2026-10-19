from typing import Any

from application.dto.dataset_context import DatasetContext
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

    def execute(self, cycle: ReplenishmentCycle) -> ReplenishmentScenario:
        return self.execute_with_context(cycle)[0]

    def execute_with_context(  # OC-8: Orquestrador do cenario com metadados do dataset
        self, cycle: ReplenishmentCycle
    ) -> tuple[ReplenishmentScenario, DatasetContext]:
        latest = self._repository.load_history().latest_per_product()
        forecasts = self._forecaster.forecast(latest)
        scenario = ReplenishmentScenario.of_items(
            [self._build_item(snap, cycle, forecasts) for snap in latest.snapshots()]
        )
        return scenario, self._context_for(latest)

    def _context_for(self, latest: Any) -> DatasetContext:
        names = {
            snap.sku().value_for_serialization(): snap.product_name() for snap in latest.snapshots()
        }
        return DatasetContext(model_mae=self._model_mae(), product_names=names)

    def _model_mae(self) -> float:
        provider = getattr(self._forecaster, "training_mae", None)
        return float(provider()) if callable(provider) else 0.0

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
