from dataclasses import dataclass

from domain.model.sku import Sku


@dataclass(frozen=True, slots=True)
class ProductInfo:
    """Identificacao de produto para composicao OC-8."""

    _sku: Sku
    _name: str

    def sku(self) -> Sku:
        return self._sku

    def name(self) -> str:
        return self._name


@dataclass(frozen=True, slots=True)
class SnapshotIdentity:
    """Identidade do snapshot (produto + data de referencia) para cumprir OC-8."""

    _product: ProductInfo
    _reference_date: str

    def sku(self) -> Sku:
        return self._product.sku()

    def product_name(self) -> str:
        return self._product.name()

    def reference_date(self) -> str:
        return self._reference_date


@dataclass(frozen=True, slots=True)
class SnapshotObservation:
    """Medicoes do snapshot (features ordenadas + demanda futura) para cumprir OC-8."""

    _features: tuple[float, float, float, float, float]
    _future_demand: int

    def features_row(self) -> tuple[float, ...]:
        return self._features

    def future_demand(self) -> int:
        return self._future_demand

    def stock_on_hand(self) -> int:
        return int(self._features[0])

    def unit_price_value(self) -> float:
        return self._features[3]


@dataclass(frozen=True, slots=True)
class StockSnapshot:
    """Registro individual de historico de estoque com 2 atributos (OC-8)."""

    _identity: SnapshotIdentity
    _observation: SnapshotObservation

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
        identity = SnapshotIdentity(ProductInfo(Sku(sku), product), reference_date)
        observation = SnapshotObservation(
            (
                float(stock_on_hand),
                float(weekly_outflow),
                float(monthly_outflow),
                float(unit_price),
                float(promotion_flag),
            ),
            future_demand,
        )
        return StockSnapshot(identity, observation)

    def sku(self) -> Sku:
        return self._identity.sku()

    def product_name(self) -> str:
        return self._identity.product_name()

    def reference_date(self) -> str:
        return self._identity.reference_date()

    def stock_on_hand(self) -> int:
        return self._observation.stock_on_hand()

    def unit_price_float(self) -> float:
        return self._observation.unit_price_value()

    def features_row(self) -> tuple[float, ...]:
        return self._observation.features_row()

    def future_demand(self) -> int:
        return self._observation.future_demand()
