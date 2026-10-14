from dataclasses import dataclass
from typing import Protocol

from domain.model.quantity import Quantity
from domain.model.stock_risk_level import StockRiskLevel
from domain.model.stock_risk_thresholds import StockRiskThresholds


class StockRiskRule(Protocol):
    """Regra de classificacao de risco de estoque."""

    def level(self) -> StockRiskLevel: ...

    def matches(self, stock: Quantity, forecast: Quantity) -> bool: ...


@dataclass(frozen=True, slots=True)
class ShortageRule:
    """Regra de possivel falta: estoque_atual < demanda_prevista."""

    def level(self) -> StockRiskLevel:
        return StockRiskLevel.SHORTAGE

    def matches(self, stock: Quantity, forecast: Quantity) -> bool:
        return stock.units_value() < forecast.units_value()


@dataclass(frozen=True, slots=True)
class ExcessRule:
    """Regra de possivel excesso: estoque_atual > 1.8 * demanda_prevista."""

    _thresholds: StockRiskThresholds

    def level(self) -> StockRiskLevel:
        return StockRiskLevel.EXCESS

    def matches(self, stock: Quantity, forecast: Quantity) -> bool:
        return stock.units_value() > (forecast.units_value() * self._thresholds.multiplier_value())
