from typing import Protocol

from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario


class PlanRepair(Protocol):
    """Porta para operador de reparo de planos de compra."""

    def repair(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        """Devolve um plano viavel respeitando necessidade liquida e orcamento."""
        ...
