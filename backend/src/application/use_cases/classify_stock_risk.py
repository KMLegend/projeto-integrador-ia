from typing import Any

from domain.forecasting.stock_snapshot import StockSnapshot
from domain.forecasting.stock_snapshots import StockSnapshots
from domain.model.quantity import Quantity
from domain.model.stock_risk_assessment import StockRiskAssessment
from domain.model.stock_risk_level import StockRiskLevel
from domain.policy.stock_risk_classifier import StockRiskClassifier
from domain.ports.demand_forecaster import DemandForecaster


class ClassifyStockRisk:
    """Caso de uso para classificar o risco de estoque por produto (RN-06)."""

    def __init__(
        self,
        forecaster: DemandForecaster,
        classifier: StockRiskClassifier,
    ) -> None:
        self._forecaster = forecaster
        self._classifier = classifier

    def execute(self, snapshots: StockSnapshots) -> tuple[StockRiskAssessment, ...]:
        latest = snapshots.latest_per_product()
        forecasts = self._forecaster.forecast(latest)
        return tuple(self._assess_snapshot(snap, forecasts) for snap in latest.snapshots())

    def _assess_snapshot(  # OC-8: Avaliacao de snapshot com classificacao de risco
        self, snap: StockSnapshot, forecasts: Any
    ) -> StockRiskAssessment:
        sku = snap.sku()
        forecast = forecasts.for_sku(sku)
        risk = self._classifier.classify(
            Quantity.of(snap.stock_on_hand()), Quantity.of(forecast.units_value())
        )
        return self._build_assessment(snap, risk)

    @staticmethod
    def _build_assessment(  # OC-8: Instanciacao de StockRiskAssessment
        snap: StockSnapshot, risk: StockRiskLevel
    ) -> StockRiskAssessment:
        return StockRiskAssessment.create(
            sku=snap.sku().value_for_serialization(),
            product_name=snap.product_name(),
            stock_on_hand=snap.stock_on_hand(),
            risk_level=risk,
        )
