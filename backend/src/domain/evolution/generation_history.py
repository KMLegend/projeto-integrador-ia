from collections.abc import Sequence
from dataclasses import dataclass

from domain.evolution.generation_report import GenerationReport
from domain.model.fitness_score import FitnessScore


@dataclass(frozen=True, slots=True)
class GenerationHistory:
    """Historico completo da evolucao geracao a geracao - colecao de primeira classe."""

    _reports: tuple[GenerationReport, ...]

    @staticmethod
    def empty() -> "GenerationHistory":
        return GenerationHistory(())

    @staticmethod
    def of_reports(reports: Sequence[GenerationReport]) -> "GenerationHistory":
        return GenerationHistory(tuple(reports))

    def appended_with(self, report: GenerationReport) -> "GenerationHistory":
        return GenerationHistory(self._reports + (report,))

    def size(self) -> int:
        return len(self._reports)

    def at(
        self,
        index: int,
    ) -> GenerationReport:
        return self._reports[index]

    def best_fitness(self) -> FitnessScore:
        return self._reports[-1].best_fitness()

    def reports(self) -> tuple[GenerationReport, ...]:
        return self._reports
