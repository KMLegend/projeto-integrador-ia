from typing import Protocol

from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario


class CrossoverStrategy(Protocol):
    """Porta para estrategia de recombinacao (crossover) de planos."""

    def combine(
        self,
        first: PurchasePlan,
        second: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> PurchasePlan: ...
