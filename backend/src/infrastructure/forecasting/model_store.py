import logging
from pathlib import Path

import joblib
from sklearn.linear_model import LinearRegression

from domain.forecasting.feature_schema import FeatureSchema
from domain.forecasting.stock_snapshots import StockSnapshots
from domain.ports.stock_history_repository import StockHistoryRepository
from infrastructure.forecasting.linear_regression_demand_forecaster import (
    LinearRegressionDemandForecaster,
)

logger = logging.getLogger(__name__)


class ModelStore:
    """Gerenciador de persistencia lazy e cache em processo do modelo preditivo."""

    def __init__(self, model_path: Path | str) -> None:
        self._model_path = Path(model_path)
        self._cached_forecaster: LinearRegressionDemandForecaster | None = None

    def get_or_train_forecaster(
        self,
        repository: StockHistoryRepository,
        seed: int = 42,
    ) -> LinearRegressionDemandForecaster:
        if self._cached_forecaster is not None:
            return self._cached_forecaster

        loaded = self.load()
        if loaded is not None:
            self._cached_forecaster = loaded
            return loaded

        logger.info("Modelo nao encontrado ou incompativel. Treinando novo modelo...")
        forecaster, _ = self.train_and_save(repository.load_history(), seed=seed)
        return forecaster

    def load(self) -> LinearRegressionDemandForecaster | None:
        if not self._model_path.exists():
            return None

        try:
            payload = joblib.load(self._model_path)
            if not self._is_payload_valid(payload):
                logger.warning("Artefato de modelo incompativel com schema atual. Descartando.")
                return None
            return LinearRegressionDemandForecaster(
                payload["model"], float(payload.get("train_mae", 0.0))
            )
        except Exception as err:
            logger.warning("Falha ao carregar artefato de modelo (%s). Descartando.", err)
            return None

    def train_and_save(
        self,
        snapshots: StockSnapshots,
        seed: int = 42,
    ) -> tuple[LinearRegressionDemandForecaster, float]:
        forecaster, mae = LinearRegressionDemandForecaster.train(snapshots, random_state=seed)

        payload = {
            "model": forecaster.underlying_model(),
            "features": FeatureSchema.ORDERED_NAMES,
            "schema_version": FeatureSchema.SCHEMA_VERSION,
            "seed": seed,
            "train_mae": mae,
        }

        self._model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(payload, self._model_path)
        self._cached_forecaster = forecaster
        return forecaster, mae

    @staticmethod
    def _is_payload_valid(payload: object) -> bool:
        if not isinstance(payload, dict):
            return False
        if payload.get("schema_version") != FeatureSchema.SCHEMA_VERSION:
            return False
        if tuple(payload.get("features", ())) != FeatureSchema.ORDERED_NAMES:
            return False
        return isinstance(payload.get("model"), LinearRegression)


def main() -> None:
    import argparse

    from core.config import get_settings
    from infrastructure.dataset.simulated_stock_history_repository import (
        SimulatedStockHistoryRepository,
    )

    parser = argparse.ArgumentParser(description="Treina e persiste o modelo de demanda.")
    parser.add_argument("--train", action="store_true", help="Executa o treino")
    parser.add_argument("--path", type=str, default=None, help="Caminho do artefato")
    args = parser.parse_args()

    settings = get_settings()
    path = Path(args.path or settings.model_store_path)
    store = ModelStore(path)
    repo = SimulatedStockHistoryRepository()
    _, mae = store.train_and_save(repo.load_history(), seed=settings.default_random_seed)
    print(f"Modelo treinado com sucesso! MAE: {mae:.4f} salvo em {path}")


if __name__ == "__main__":
    main()
