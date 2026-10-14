from typing import TYPE_CHECKING, Protocol

from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.fitness_policy import FitnessPolicy

if TYPE_CHECKING:
    from domain.evolution.population import Population


class SelectionStrategy(Protocol):
    """Porta para estrategia de selecao de progenitores."""

    def select(
        self,
        population: "Population",
        policy: FitnessPolicy,
        scenario: ReplenishmentScenario,
    ) -> "Population": ...
