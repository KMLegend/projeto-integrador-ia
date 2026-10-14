from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StockRiskThresholds:
    """Parametros de politica para classificacao de risco de estoque (RN-06)."""

    excess_multiplier: float

    @staticmethod
    def default() -> "StockRiskThresholds":
        return StockRiskThresholds(excess_multiplier=1.8)

    def multiplier_value(self) -> float:
        return self.excess_multiplier
