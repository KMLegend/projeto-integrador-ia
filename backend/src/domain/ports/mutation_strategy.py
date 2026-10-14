from typing import Protocol

from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario


class MutationStrategy(Protocol):
    """Porta para estrategia de mutacao de planos de compra."""

    def mutate(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> PurchasePlan: ...
