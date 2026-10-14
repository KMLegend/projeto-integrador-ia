from dataclasses import dataclass

from domain.model.sku import Sku


@dataclass(frozen=True, slots=True)
class ProductInfo:
    """Informacoes de identificacao do produto."""

    _sku: Sku
    _name: str

    def sku(self) -> Sku:
        return self._sku

    def name(self) -> str:
        return self._name


@dataclass(frozen=True, slots=True)
class SnapshotIdentity:
    """Identidade temporal e cadastral do snapshot (OC-8)."""

    _product_info: ProductInfo
    _reference_date: str

    def sku(self) -> Sku:
        return self._product_info.sku()

    def product_name(self) -> str:
        return self._product_info.name()

    def reference_date(self) -> str:
        return self._reference_date


@dataclass(frozen=True, slots=True)
class SnapshotObservation:
    """Observacoes quantitativas e alvo de previsao (OC-8)."""

    _features: tuple[float, ...]
    _future_demand: int

    def features(self) -> tuple[float, ...]:
        return self._features

    def future_demand(self) -> int:
        return self._future_demand

    def stock_on_hand(self) -> int:
        return int(self._features[0])

    def unit_price(self) -> float:
        return self._features[3]


@dataclass(frozen=True, slots=True)
class StockSnapshot:
    """Snapshot semanal de estoque e vendas para regressao linear."""

    _identity: SnapshotIdentity
    _observation: SnapshotObservation

    @staticmethod
    def _raw(s: int, w: int, m: int, p: float, f: int) -> tuple[float, ...]:
        return (float(s), float(w), float(m), float(p), float(f))

    @staticmethod
    def create(  # noqa: PLR0913
        sku: str,
        product: str,
        reference_date: str,
        stock_on_hand: int,
        weekly_outflow: int,
        monthly_outflow: int,
        unit_price: float,
        promotion_flag: int,
        future_demand: int = 0,
    ) -> "StockSnapshot":
        ident = SnapshotIdentity(ProductInfo(Sku(sku), product), reference_date)
        raw = StockSnapshot._raw(
            stock_on_hand, weekly_outflow, monthly_outflow, unit_price, promotion_flag
        )
        return StockSnapshot(ident, SnapshotObservation(raw, future_demand))

    def sku(self) -> Sku:
        return self._identity.sku()

    def product_name(self) -> str:
        return self._identity.product_name()

    def reference_date(self) -> str:
        return self._identity.reference_date()

    def features(self) -> tuple[float, ...]:
        return self._observation.features()

    def future_demand(self) -> int:
        return self._observation.future_demand()

    def stock_on_hand(self) -> int:
        return self._observation.stock_on_hand()

    def unit_price(self) -> float:
        return self._observation.unit_price()

    def features_row(self) -> tuple[float, ...]:
        return self._observation.features()

    def unit_price_float(self) -> float:
        return self._observation.unit_price()
