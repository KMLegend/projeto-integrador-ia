from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from domain.forecasting.stock_snapshot import StockSnapshot


@dataclass(frozen=True, slots=True)
class StockSnapshots:
    """Colecao de primeira classe de snapshots de estoque."""

    _snapshots: tuple[StockSnapshot, ...]

    @staticmethod
    def of(snapshots: Iterable[StockSnapshot]) -> "StockSnapshots":
        return StockSnapshots(tuple(snapshots))

    @staticmethod
    def of_snapshots(snapshots: Iterable[StockSnapshot]) -> "StockSnapshots":
        return StockSnapshots.of(snapshots)

    def features_matrix_rows(self) -> tuple[tuple[float, ...], ...]:
        return tuple(snap.features() for snap in self._snapshots)

    def target_vector(self) -> tuple[int, ...]:
        return tuple(snap.future_demand() for snap in self._snapshots)

    def size(self) -> int:
        return len(self._snapshots)

    def snapshots(self) -> tuple[StockSnapshot, ...]:
        return self._snapshots

    def latest_per_product(self) -> "StockSnapshots":
        """Retorna o snapshot mais recente por produto, ordenado alfabeticamente por nome."""
        latest_dict = self._collect_latest_by_sku()
        return StockSnapshots(self._sort_by_product_name(latest_dict.values()))

    def _collect_latest_by_sku(self) -> dict[str, StockSnapshot]:
        latest: dict[str, StockSnapshot] = {}
        for snap in self._snapshots:
            self._update_if_later(latest, snap)
        return latest

    def _update_if_later(self, latest: dict[str, StockSnapshot], snap: StockSnapshot) -> None:
        key = snap.sku().value_for_serialization()
        if self._should_replace_snapshot(latest.get(key), snap):
            latest[key] = snap

    @staticmethod
    def _sort_by_product_name(snaps: Any) -> tuple[StockSnapshot, ...]:
        return tuple(sorted(snaps, key=lambda s: s.product_name()))

    @staticmethod
    def _should_replace_snapshot(
        current: StockSnapshot | None,
        candidate: StockSnapshot,
    ) -> bool:
        if current is None:
            return True
        return candidate.reference_date() > current.reference_date()
