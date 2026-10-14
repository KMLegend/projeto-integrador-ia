from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.model.fitness_score import FitnessScore

if TYPE_CHECKING:
    from domain.model.coverage_report import CoverageReport


@dataclass(frozen=True, slots=True)
class FitnessWeights:
    """Pesos da funcao fitness para cobertura e penalidade de risco (RN-07)."""

    coverage: float
    risk_penalty: float

    @staticmethod
    def default() -> "FitnessWeights":
        return FitnessWeights(coverage=10.0, risk_penalty=5.0)

    def score(self, coverage_report: "CoverageReport") -> FitnessScore:
        return FitnessScore(
            coverage_report.served_ratio_points() * self.coverage
            - coverage_report.items_at_risk_count() * self.risk_penalty
        )

    def coverage_weight(self) -> float:
        return self.coverage

    def risk_penalty_weight(self) -> float:
        return self.risk_penalty
