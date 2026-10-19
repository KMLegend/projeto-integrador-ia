from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from domain.forecasting.stock_snapshots import StockSnapshots
from domain.forecasting.weekly_demand_forecast import WeeklyDemandForecast
from domain.forecasting.weekly_demand_forecasts import WeeklyDemandForecasts
from domain.model.sku import Sku
from domain.ports.demand_forecaster import DemandForecaster


class LinearRegressionDemandForecaster(DemandForecaster):
    """Forecaster de demanda baseado em Regressão Linear com Scikit-Learn."""

    def __init__(self, model: LinearRegression, training_mae: float = 0.0) -> None:
        self._model = model
        self._training_mae = training_mae

    def training_mae(self) -> float:
        return self._training_mae

    @staticmethod
    def train(
        snapshots: StockSnapshots,
        random_state: int = 42,
    ) -> tuple["LinearRegressionDemandForecaster", float]:
        """Treina modelo com split 80/20 e random_state fixo, devolvendo modelo e MAE."""
        features = list(snapshots.features_matrix_rows())
        targets = list(snapshots.target_vector())

        x_train, x_test, y_train, y_test = train_test_split(
            features,
            targets,
            test_size=0.20,
            random_state=random_state,
        )

        model = LinearRegression()
        model.fit(x_train, y_train)

        predictions = model.predict(x_test)
        mae = float(mean_absolute_error(y_test, predictions))

        return LinearRegressionDemandForecaster(model, mae), mae

    def forecast(self, snapshots: StockSnapshots) -> WeeklyDemandForecasts:
        latest = snapshots.latest_per_product()
        entries: list[tuple[Sku, WeeklyDemandForecast]] = []

        for snap in latest.snapshots():
            feature_row = snap.features_row()
            raw_prediction = float(self._model.predict([feature_row])[0])
            forecast = WeeklyDemandForecast.from_prediction(raw_prediction)
            entries.append((snap.sku(), forecast))

        return WeeklyDemandForecasts.of_entries(entries)

    def underlying_model(self) -> LinearRegression:
        return self._model
