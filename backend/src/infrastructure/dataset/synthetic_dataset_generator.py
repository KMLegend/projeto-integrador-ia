import math
from collections.abc import Sequence
from datetime import date, timedelta

import numpy as np

from domain.forecasting.stock_snapshot import StockSnapshot
from domain.forecasting.stock_snapshots import StockSnapshots
from infrastructure.dataset.product_catalog import BASE_CATALOG, CatalogProduct


class SyntheticDatasetGenerator:
    """Gerador reproduzivel de dataset sintetico para previsao de demanda."""

    def __init__(self, seed: int = 42) -> None:
        self._seed = seed

    def generate(
        self,
        catalog: Sequence[CatalogProduct] = BASE_CATALOG,
        weeks_count: int = 20,
        start_date: date = date(2026, 2, 18),
    ) -> StockSnapshots:
        np.random.seed(self._seed)
        snapshots: list[StockSnapshot] = []

        for product in catalog:
            for week_idx in range(weeks_count):
                snap = self._generate_row(product, week_idx, start_date)
                snapshots.append(snap)

        return StockSnapshots.of_snapshots(snapshots)

    @staticmethod
    def _generate_row(
        product: CatalogProduct,
        week_idx: int,
        start_date: date,
    ) -> StockSnapshot:
        ref_date = (start_date + timedelta(days=7 * week_idx)).isoformat()
        base_out = product.baseline_weekly_outflow()
        base_price = product.baseline_price()

        promo = 1 if np.random.random() < 0.20 else 0
        season = 1.0 + 0.08 * math.sin(2.0 * math.pi * week_idx / 10.0)
        price_promo_mult = 0.90 if promo == 1 else 1.0
        price = round(base_price * price_promo_mult * float(np.random.normal(1.0, 0.01)), 2)

        outflow_promo_mult = 1.15 if promo == 1 else 1.0
        noise = float(np.random.normal(0.0, 4.0))
        wo = max(1, round(base_out * season * outflow_promo_mult + noise))
        mo = max(wo, round(wo * 4.0 + float(np.random.normal(0.0, 10.0))))
        soh = max(0, round(wo * float(np.random.uniform(2.0, 6.0))))
        fd = max(
            1,
            round(
                0.55 * wo
                + 0.35 * (mo / 4.0)
                + 0.10 * base_out * promo
                + 0.15 * base_out * (base_price - price) / base_price
                + float(np.random.normal(0.0, 5.0))
            ),
        )

        return StockSnapshot.create(
            product.sku(),
            product.name(),
            ref_date,
            soh,
            wo,
            mo,
            price,
            promo,
            fd,
        )
