from dataclasses import dataclass

from domain.evolution.evolution_operators import EvolutionOperators
from domain.evolution.evolution_result import EvolutionResult
from domain.evolution.evolution_settings import EvolutionSettings
from domain.evolution.generation_history import GenerationHistory
from domain.evolution.generation_report import GenerationReport
from domain.evolution.null_evolution_observer import NullEvolutionObserver
from domain.evolution.population import Population
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
        pop = self._operators.create_initial_population(self._settings.population_size, scenario)
        pop, history = self._run_generations(pop, scenario, observer)
        best = self._operators.best_assessment(pop, scenario)
        return EvolutionResult(best, history)

    def _step(
        self,
        pop: Population,
        scen: ReplenishmentScenario,
        gen: int,
        obs: EvolutionObserver,
    ) -> tuple[Population, GenerationReport]:
        rep = self._operators.evaluate_generation(pop, scen, gen)
        obs.on_generation(rep)
        return self._breed_next(pop, scen), rep

    def _breed_next(self, pop: Population, scen: ReplenishmentScenario) -> Population:
        parents = self._operators.select_parents(pop, scen)
        return self._operators.breed_next_generation(
            parents, self._settings.population_size, self._settings.elite_size, scen
        )

    def _run_generations(
        self,
        pop: Population,
        scen: ReplenishmentScenario,
        obs: EvolutionObserver,
    ) -> tuple[Population, GenerationHistory]:
        hist = GenerationHistory.empty()
        for gen in range(self._settings.generations):
            pop, rep = self._step(pop, scen, gen, obs)
            hist = hist.appended_with(rep)
        return pop, hist
