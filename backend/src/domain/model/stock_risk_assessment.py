from dataclasses import dataclass

from domain.model.quantity import Quantity
from domain.model.sku import Sku
from domain.model.stock_risk_level import StockRiskLevel


@dataclass(frozen=True, slots=True)
class StockRiskAssessmentIdentity:
    """Identidade e niveis de estoque do produto para avaliacao de risco (OC-8)."""

    _sku: Sku
    _product_name: str
    _stock_on_hand: Quantity

    def sku(self) -> Sku:
        return self._sku

    def product_name(self) -> str:
        return self._product_name

    def stock_on_hand(self) -> Quantity:
        return self._stock_on_hand


@dataclass(frozen=True, slots=True)
class StockRiskAssessment:
    """Avaliacao de risco de estoque de um produto (RN-06)."""

    _identity: StockRiskAssessmentIdentity
    _risk_level: StockRiskLevel

    @staticmethod
    def create(
        sku: str,
        product_name: str,
        stock_on_hand: int,
        risk_level: StockRiskLevel,
    ) -> "StockRiskAssessment":
        return StockRiskAssessment(
            StockRiskAssessmentIdentity(Sku(sku), product_name, Quantity.of(stock_on_hand)),
            risk_level,
        )

    def sku(self) -> Sku:
        return self._identity.sku()

    def product_name(self) -> str:
        return self._identity.product_name()

    def stock_on_hand(self) -> Quantity:
        return self._identity.stock_on_hand()

    def risk_level(self) -> StockRiskLevel:
        return self._risk_level

    def value_for_serialization(self) -> dict[str, str | int]:
        return {
            "sku": self._identity.sku().value_for_serialization(),
            "product": self._identity.product_name(),
            "stock_on_hand": self._identity.stock_on_hand().units_value(),
            "risk_level": self._risk_level.name,
        }
