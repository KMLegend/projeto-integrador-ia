from dataclasses import dataclass

from domain.evolution.evolution_operators import EvolutionOperators
from domain.evolution.evolution_result import EvolutionResult
from domain.evolution.evolution_settings import EvolutionSettings
from domain.evolution.generation_history import GenerationHistory
from domain.evolution.null_evolution_observer import NullEvolutionObserver
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.evolution_observer import EvolutionObserver

DEFAULT_OBSERVER: EvolutionObserver = NullEvolutionObserver()


@dataclass(frozen=True, slots=True)
class EvolutionEngine:
    """Motor evolutivo de Computacao Evolutiva (AG) com fidelidade ao notebook."""

    _settings: EvolutionSettings
    _operators: EvolutionOperators

    def evolve(
        self,
        scenario: ReplenishmentScenario,
        observer: EvolutionObserver = DEFAULT_OBSERVER,
    ) -> EvolutionResult:
        population = self._operators.create_initial_population(
            self._settings.population_size, scenario
        )
        history = GenerationHistory.empty()

        for gen in range(self._settings.generations):
            report = self._operators.evaluate_generation(population, scenario, gen)
            history = history.appended_with(report)
            observer.on_generation(report)
            parents = self._operators.select_parents(population, scenario)
            population = self._operators.breed_next_generation(
                parents,
                self._settings.population_size,
                self._settings.elite_size,
                scenario,
            )

        best_assessment = self._operators.best_assessment(population, scenario)
        return EvolutionResult(best_assessment, history)
