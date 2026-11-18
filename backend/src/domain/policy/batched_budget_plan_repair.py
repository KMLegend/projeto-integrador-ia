from dataclasses import dataclass

from domain.model.budget_constraint import BudgetConstraint
from domain.model.money import Money
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_scenario import ReplenishmentScenario


@dataclass(frozen=True, slots=True)
class BatchedBudgetPlanRepair:
    """Reparo equivalente ao `BudgetAwarePlanRepair`, com custo independente do volume (D-19).

    O reparo ingenuo remove uma unidade por vez e recalcula o custo total a cada iteracao:
    `O(unidades removidas x itens)`. Com milhares de SKUs isso estoura o tempo do worker.
    Aqui o custo e mantido de forma incremental e as unidades do item mais caro saem de uma vez.

    A equivalencia vale porque remover unidades de um item nao altera preco algum: o item mais
    caro continua sendo o mais caro ate zerar, entao remover N unidades dele de uma vez produz
    o mesmo plano que remover N vezes uma unidade.
    """

    _budget: BudgetConstraint

    def repair(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        return self._fit_to_budget(plan.clamped_to(scenario.required_quantities()), scenario)

    def _fit_to_budget(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        total = scenario.total_cost_of(plan)
        for position in self._by_descending_price(plan, scenario):
            if not self._budget.is_exceeded_by(total):
                return plan
            plan, total = self._drain(plan, scenario, position, total)
        return plan

    @staticmethod
    def _by_descending_price(
        plan: PurchasePlan, scenario: ReplenishmentScenario
    ) -> tuple[Position, ...]:
        return tuple(sorted(plan.non_empty_positions(), key=scenario.price_rank_of, reverse=True))

    def _drain(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
        position: Position,
        total: Money,
    ) -> tuple[PurchasePlan, Money]:
        price = scenario.unit_price_at(position)
        held = plan.quantity_at(position)
        excess = total.minus(self._budget.limit_money())
        removed = held.limited_to(excess.units_needed_at(price))
        kept = Quantity.of(held.units_value() - removed.units_value())
        return plan.with_quantity_at(position, kept), total.minus(price.total_for(removed))
