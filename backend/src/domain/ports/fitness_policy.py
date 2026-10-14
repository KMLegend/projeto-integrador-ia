from typing import Protocol

from domain.model.plan_assessment import PlanAssessment
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario


class FitnessPolicy(Protocol):
    """Porta para avaliacao de aptidao (fitness) de planos de compra."""

    def evaluate(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PlanAssessment:
        """Pontua um plano ja reparado. Funcao pura."""
        ...
