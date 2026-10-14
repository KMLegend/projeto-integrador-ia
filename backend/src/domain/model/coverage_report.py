from dataclasses import dataclass

from domain.model.percentage import Percentage


@dataclass(frozen=True, slots=True)
class CoverageReport:
    """Relatorio de cobertura da demanda e produtos em risco (RN-07)."""

    _served_ratio: Percentage
    _items_at_risk: int

    def served_ratio(self) -> Percentage:
        return self._served_ratio

    def served_ratio_points(self) -> float:
        return self._served_ratio.points()

    def items_at_risk_count(self) -> int:
        return self._items_at_risk
