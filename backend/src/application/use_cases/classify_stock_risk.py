from domain.forecasting.stock_snapshots import StockSnapshots
from domain.model.quantity import Quantity
from domain.model.stock_risk_assessment import StockRiskAssessment
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
        assessments: list[StockRiskAssessment] = []

        for snap in latest.snapshots():
            sku = snap.sku()
            forecast = forecasts.for_sku(sku)
            stock_qty = Quantity.of(snap.stock_on_hand())
            forecast_qty = Quantity.of(forecast.units_value())

            risk_level = self._classifier.classify(stock_qty, forecast_qty)
            assessments.append(
                StockRiskAssessment.create(
                    sku=sku.value_for_serialization(),
                    product_name=snap.product_name(),
                    stock_on_hand=snap.stock_on_hand(),
                    risk_level=risk_level,
                )
            )

        return tuple(assessments)
