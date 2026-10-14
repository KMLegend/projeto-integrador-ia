import json
from pathlib import Path
import pytest

from domain.model.catalog_item import CatalogItem
from domain.model.quantity import Quantity
from domain.model.replenishment_item import ReplenishmentItem
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.sku import Sku
from domain.model.unit_price import UnitPrice


@pytest.fixture
def reference_scenario() -> ReplenishmentScenario:
    fixture_path = Path(__file__).parent / "fixtures" / "reference_scenario.json"
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)

    items = []
    for raw in data["items"]:
        catalog_item = CatalogItem(
            Sku(raw["sku"]),
            UnitPrice.from_reais(raw["unit_price"]),
        )
        item = ReplenishmentItem(
            catalog_item,
            Quantity.of(raw["required_quantity"]),
        )
        items.append(item)

    return ReplenishmentScenario.of_items(items)
