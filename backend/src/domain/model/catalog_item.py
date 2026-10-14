from dataclasses import dataclass

from domain.model.money import Money
from domain.model.quantity import Quantity
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice


@dataclass(frozen=True, slots=True)
class CatalogItem:
    """Item de catalogo com SKU e preco unitario (composicao OC-8)."""

    _sku: Sku
    _unit_price: UnitPrice

    def sku(self) -> Sku:
        return self._sku

    def unit_price(self) -> UnitPrice:
        return self._unit_price

    def cost_for(self, quantity: Quantity) -> Money:
        return self._unit_price.total_for(quantity)

    def is_more_expensive_than(self, other: "CatalogItem") -> bool:
        return self._unit_price.is_more_expensive_than(other._unit_price)
