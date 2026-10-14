from dataclasses import dataclass

from domain.model.fitness_score import FitnessScore


@dataclass(frozen=True, slots=True)
class GenerationReport:
    """Relatorio de uma geracao evolutiva (ponto da curva de convergencia)."""

    _generation: int
    _best_fitness: FitnessScore

    def generation_number(self) -> int:
        return self._generation

    def best_fitness(self) -> FitnessScore:
        return self._best_fitness

    def fitness_value(self) -> float:
        return self._best_fitness.value()

    def value_for_serialization(self) -> dict[str, float | int]:
        return {
            "generation": self._generation,
            "max_fitness": self._best_fitness.value_for_serialization(),
        }
