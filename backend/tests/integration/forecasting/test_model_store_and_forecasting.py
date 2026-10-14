import joblib
from pathlib import Path
import tempfile
from sklearn.linear_model import LinearRegression

from domain.forecasting.feature_schema import FeatureSchema
from domain.forecasting.stock_snapshots import StockSnapshots
from infrastructure.dataset.simulated_stock_history_repository import (
    SimulatedStockHistoryRepository,
)
from infrastructure.forecasting.cached_demand_forecaster import CachedDemandForecaster
from infrastructure.forecasting.linear_regression_demand_forecaster import (
    LinearRegressionDemandForecaster,
)
from infrastructure.forecasting.model_store import ModelStore


def test_linear_regression_demand_forecaster_train_mae_below_6() -> None:
    repo = SimulatedStockHistoryRepository()
    snapshots = repo.load_history()

    forecaster, mae = LinearRegressionDemandForecaster.train(snapshots, random_state=42)

    assert mae <= 6.0
    # Valida previsoes no cenario mais recente
    forecasts = forecaster.forecast(snapshots)
    assert forecasts.size() == 6

    for _, forecast in forecasts.entries():
        assert forecast.units_value() >= 1


def test_cached_demand_forecaster_memoizes_predictions() -> None:
    repo = SimulatedStockHistoryRepository()
    snapshots = repo.load_history()

    base_forecaster, _ = LinearRegressionDemandForecaster.train(snapshots, random_state=42)
    cached = CachedDemandForecaster(base_forecaster)

    assert cached.cache_size() == 0

    forecasts_first = cached.forecast(snapshots)
    assert cached.cache_size() == 6

    forecasts_second = cached.forecast(snapshots)
    assert forecasts_first.entries() == forecasts_second.entries()


def test_model_store_train_and_save_and_lazy_load() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        model_file = Path(tmpdir) / "test_model.joblib"
        store = ModelStore(model_file)
        repo = SimulatedStockHistoryRepository()

        # Primeiro acesso: arquivo nao existe -> treina e persiste
        forecaster = store.get_or_train_forecaster(repo, seed=42)
        assert model_file.exists()

        # Segundo acesso: retorna do cache em processo
        forecaster_cached = store.get_or_train_forecaster(repo, seed=42)
        assert forecaster_cached is forecaster

        # Novo ModelStore apontando para o mesmo arquivo -> carrega do disco
        store2 = ModelStore(model_file)
        forecaster_loaded = store2.get_or_train_forecaster(repo, seed=42)
        assert isinstance(forecaster_loaded, LinearRegressionDemandForecaster)


def test_model_store_discards_incompatible_schema_and_retrains() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        model_file = Path(tmpdir) / "corrupt_model.joblib"

        # Salva payload com schema antigo/incompativel
        incompatible_payload = {
            "model": LinearRegression(),
            "features": ("wrong_feature_1",),
            "schema_version": "0.1-obsolete",
            "seed": 42,
            "train_mae": 99.0,
        }
        joblib.dump(incompatible_payload, model_file)

        store = ModelStore(model_file)
        repo = SimulatedStockHistoryRepository()

        # Deve descartar e retreinar com o schema atual
        forecaster = store.get_or_train_forecaster(repo, seed=42)
        assert forecaster is not None

        # Verifica que o arquivo foi sobrescrito com o schema valido
        reloaded = joblib.load(model_file)
        assert reloaded["schema_version"] == FeatureSchema.SCHEMA_VERSION
        assert tuple(reloaded["features"]) == FeatureSchema.ORDERED_NAMES
