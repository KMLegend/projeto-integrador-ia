from dataclasses import dataclass

from domain.model.quantity import Quantity
from domain.model.stock_risk_level import StockRiskLevel
from domain.model.stock_risk_thresholds import StockRiskThresholds
from domain.policy.stock_risk_rules import ExcessRule, ShortageRule, StockRiskRule


@dataclass(frozen=True, slots=True)
class StockRiskClassifier:
    """Classificador de risco de estoque sem else (RN-06 e Regra 2 do Object Calisthenics)."""

    _rules: tuple[StockRiskRule, ...]

    @staticmethod
    def with_thresholds(thresholds: StockRiskThresholds) -> "StockRiskClassifier":
        return StockRiskClassifier(
            (
                ShortageRule(),
                ExcessRule(thresholds),
            )
        )

    @staticmethod
    def standard() -> "StockRiskClassifier":
        return StockRiskClassifier.with_thresholds(StockRiskThresholds.default())

    def classify(self, stock: Quantity, forecast: Quantity) -> StockRiskLevel:
        matched = (rule.level() for rule in self._rules if rule.matches(stock, forecast))
        return next(matched, StockRiskLevel.ADEQUATE)
