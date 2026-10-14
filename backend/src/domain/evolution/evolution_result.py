from dataclasses import dataclass

from domain.evolution.generation_history import GenerationHistory
from domain.evolution.generation_report import GenerationReport
from domain.model.fitness_score import FitnessScore
from domain.model.plan_assessment import PlanAssessment
from domain.model.purchase_plan import PurchasePlan


@dataclass(frozen=True, slots=True)
class EvolutionResult:
    """Resultado da execucao evolutiva: melhor plano avaliado + historico."""

    _best_assessment: PlanAssessment
    _history: GenerationHistory

    def best_plan(self) -> PurchasePlan:
        return self._best_assessment.plan()

    def best_assessment(self) -> PlanAssessment:
        return self._best_assessment

    def best_fitness(self) -> FitnessScore:
        return self._best_assessment.fitness()

    def convergence_curve(self) -> tuple[GenerationReport, ...]:
        return self._history.reports()

    def history(self) -> GenerationHistory:
        return self._history
