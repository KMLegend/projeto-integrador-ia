from collections.abc import Sequence
from dataclasses import dataclass

from domain.forecasting.stock_snapshot import StockSnapshot


@dataclass(frozen=True, slots=True)
class StockSnapshots:
    """Colecao de primeira classe de snapshots de historico de estoque."""

    _snapshots: tuple[StockSnapshot, ...]

    @staticmethod
    def of_snapshots(snapshots: Sequence[StockSnapshot]) -> "StockSnapshots":
        return StockSnapshots(tuple(snapshots))

    def size(self) -> int:
        return len(self._snapshots)

    def snapshots(self) -> tuple[StockSnapshot, ...]:
        return self._snapshots

    def latest_per_product(self) -> "StockSnapshots":
        """Retorna o snapshot mais recente por produto, ordenado alfabeticamente por nome."""
        latest_by_sku: dict[str, StockSnapshot] = {}

        for snap in self._snapshots:
            sku_str = snap.sku().value_for_serialization()
            if self._should_replace_snapshot(latest_by_sku.get(sku_str), snap):
                latest_by_sku[sku_str] = snap

        # Ordenacao estavel e deterministica por nome do produto
        sorted_latest = sorted(
            latest_by_sku.values(),
            key=lambda snap: snap.product_name(),
        )
        return StockSnapshots(tuple(sorted_latest))

    @staticmethod
    def _should_replace_snapshot(
        current: StockSnapshot | None,
        candidate: StockSnapshot,
    ) -> bool:
        if current is None:
            return True
        return candidate.reference_date() > current.reference_date()

    def features_matrix_rows(self) -> tuple[tuple[float, ...], ...]:
        return tuple(snap.features_row() for snap in self._snapshots)

    def target_vector(self) -> tuple[int, ...]:
        return tuple(snap.future_demand() for snap in self._snapshots)
