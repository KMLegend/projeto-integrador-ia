from dataclasses import dataclass

from domain.model.catalog_item import CatalogItem
from domain.model.money import Money
from domain.model.quantity import Quantity
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice


@dataclass(frozen=True, slots=True)
class ReplenishmentItem:
    """Item do cenario de reposicao com exatos 2 atributos (OC-8)."""

    _catalog_item: CatalogItem
    _required_quantity: Quantity

    def catalog_item(self) -> CatalogItem:
        return self._catalog_item

    def required_quantity(self) -> Quantity:
        return self._required_quantity

    def has_demand(self) -> bool:
        return not self._required_quantity.is_zero()

    def cost_for(self, quantity: Quantity) -> Money:
        return self._catalog_item.cost_for(quantity)

    def full_replenishment_cost(self) -> Money:
        return self._catalog_item.cost_for(self._required_quantity)

    def sku(self) -> Sku:
        return self._catalog_item.sku()

    def unit_price(self) -> UnitPrice:
        return self._catalog_item.unit_price()

    def is_more_expensive_than(self, other: "ReplenishmentItem") -> bool:
        return self._catalog_item.is_more_expensive_than(other._catalog_item)
