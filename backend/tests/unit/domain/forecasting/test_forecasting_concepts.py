import pytest

from domain.forecasting.feature_schema import FeatureSchema
from domain.forecasting.stock_snapshot import StockSnapshot
from domain.forecasting.stock_snapshots import StockSnapshots
from domain.forecasting.weekly_demand_forecast import InvalidForecastError, WeeklyDemandForecast
from domain.forecasting.weekly_demand_forecasts import WeeklyDemandForecasts
from domain.model.sku import Sku


def test_feature_schema_ordered_names_are_canonical() -> None:
    expected = (
        "stock_on_hand",
        "weekly_outflow",
        "monthly_outflow",
        "unit_price",
        "promotion_flag",
    )
    assert FeatureSchema.ORDERED_NAMES == expected


def test_weekly_demand_forecast_guarantees_minimum_one() -> None:
    # Arredondamento normal
    f1 = WeeklyDemandForecast.from_prediction(41.8)
    assert f1.units_value() == 42

    # Predicao proxima de zero ou negativa vira piso 1 (RN-02)
    f2 = WeeklyDemandForecast.from_prediction(0.2)
    assert f2.units_value() == 1

    f3 = WeeklyDemandForecast.from_prediction(-5.0)
    assert f3.units_value() == 1

    with pytest.raises(InvalidForecastError):
        WeeklyDemandForecast(0)

    with pytest.raises(InvalidForecastError):
        WeeklyDemandForecast(-1)


def test_stock_snapshots_latest_per_product_is_deterministic() -> None:
    s1 = StockSnapshot.create("CAFE-500G", "Café 500g", "2026-02-18", 100, 50, 200, 18.90, 0, 45)
    s2 = StockSnapshot.create("CAFE-500G", "Café 500g", "2026-02-25", 192, 60, 240, 18.78, 1, 60)
    s3 = StockSnapshot.create("ARROZ-5KG", "Arroz 5kg", "2026-02-18", 200, 40, 160, 29.90, 0, 40)
    s4 = StockSnapshot.create("ARROZ-5KG", "Arroz 5kg", "2026-02-25", 201, 42, 168, 29.89, 0, 42)

    snapshots = StockSnapshots.of_snapshots([s1, s3, s2, s4])
    latest = snapshots.latest_per_product()

    assert latest.size() == 2
    # Ordenacao alfabetica por nome: Arroz 5kg antes de Cafe 500g
    items = latest.snapshots()
    assert items[0].product_name() == "Arroz 5kg"
    assert items[0].reference_date() == "2026-02-25"
    assert items[1].product_name() == "Café 500g"
    assert items[1].reference_date() == "2026-02-25"

    features_matrix = latest.features_matrix_rows()
    assert len(features_matrix) == 2
    assert features_matrix[0] == (201.0, 42.0, 168.0, 29.89, 0.0)


def test_weekly_demand_forecasts_lookup() -> None:
    forecasts = WeeklyDemandForecasts.of_entries([
        (Sku("CAFE-500G"), WeeklyDemandForecast.of(60)),
        (Sku("LEITE-UHT-1L"), WeeklyDemandForecast.of(81)),
    ])
    assert forecasts.for_sku(Sku("CAFE-500G")).units_value() == 60
    assert forecasts.for_sku(Sku("LEITE-UHT-1L")).units_value() == 81

    with pytest.raises(KeyError):
        forecasts.for_sku(Sku("ARROZ-5KG"))
