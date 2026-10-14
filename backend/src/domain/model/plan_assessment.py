from dataclasses import dataclass

from domain.model.fitness_score import FitnessScore
from domain.model.purchase_plan import PurchasePlan


@dataclass(frozen=True, slots=True)
class PlanAssessment:
    """Avaliacao de um plano de compra associado ao seu score de fitness."""

    _plan: PurchasePlan
    _fitness: FitnessScore

    def plan(self) -> PurchasePlan:
        return self._plan

    def fitness(self) -> FitnessScore:
        return self._fitness

    def fitness_value(self) -> float:
        return self._fitness.value()

    def is_better_than(self, other: "PlanAssessment") -> bool:
        return self._fitness.is_better_than(other._fitness)

    def value_for_serialization(self) -> float:
        return self._fitness.value_for_serialization()
