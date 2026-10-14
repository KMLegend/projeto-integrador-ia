from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CatalogProductIdentity:
    """Identidade basica de um produto do catalogo."""

    _sku: str
    _name: str

    def sku(self) -> str:
        return self._sku

    def name(self) -> str:
        return self._name


@dataclass(frozen=True, slots=True)
class CatalogProductBaseline:
    """Valores de referencia para simulacao sintetica."""

    _baseline_weekly_outflow: int
    _baseline_price: float

    def weekly_outflow(self) -> int:
        return self._baseline_weekly_outflow

    def price(self) -> float:
        return self._baseline_price


@dataclass(frozen=True, slots=True)
class CatalogProduct:
    """Produto do catalogo base para geracao de dataset sintetico."""

    _identity: CatalogProductIdentity
    _baseline: CatalogProductBaseline

    @staticmethod
    def create(
        sku: str,
        name: str,
        baseline_weekly_outflow: int,
        baseline_price: float,
    ) -> "CatalogProduct":
        return CatalogProduct(
            CatalogProductIdentity(sku, name),
            CatalogProductBaseline(baseline_weekly_outflow, baseline_price),
        )

    def sku(self) -> str:
        return self._identity.sku()

    def name(self) -> str:
        return self._identity.name()

    def baseline_weekly_outflow(self) -> int:
        return self._baseline.weekly_outflow()

    def baseline_price(self) -> float:
        return self._baseline.price()


BASE_CATALOG: tuple[CatalogProduct, ...] = (
    CatalogProduct.create("CAFE-500G", "Café 500g", 68, 18.90),
    CatalogProduct.create("ARROZ-5KG", "Arroz 5kg", 50, 29.90),
    CatalogProduct.create("FEIJAO-1KG", "Feijão 1kg", 48, 9.49),
    CatalogProduct.create("LEITE-UHT-1L", "Leite UHT 1L", 100, 5.79),
    CatalogProduct.create("DETERGENTE-500ML", "Detergente 500ml", 30, 3.39),
    CatalogProduct.create("REFRIGERANTE-2L", "Refrigerante 2L", 78, 10.49),
)
