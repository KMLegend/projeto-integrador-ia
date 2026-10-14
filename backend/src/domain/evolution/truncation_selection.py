from dataclasses import dataclass

from domain.evolution.population import Population
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.fitness_policy import FitnessPolicy


@dataclass(frozen=True, slots=True)
class TruncationSelection:
    """Selecao por truncamento: ordena a populacao por fitness e retem os melhores."""

    _parents_size: int

    def select(
        self,
        population: Population,
        policy: FitnessPolicy,
        scenario: ReplenishmentScenario,
    ) -> Population:
        ranked = population.ranked_by(policy, scenario)
        return ranked.top(self._parents_size)
