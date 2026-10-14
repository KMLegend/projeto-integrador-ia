from domain.model.budget_constraint import BudgetConstraint
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.quantity import Quantity
from domain.model.replenishment_scenario import ReplenishmentScenario


class GreedyCheapestFirstPolicy:
    """Politica gulosa (do mais barato ao mais caro) para comprovar o otimo global."""

    def build_plan(
        self,
        scenario: ReplenishmentScenario,
        budget: BudgetConstraint,
    ) -> PurchasePlan:
        # Pega posicoes que tem demanda
        demand_positions = scenario.positions_with_demand()
        # Ordena por preco unitario crescente
        sorted_positions = sorted(
            demand_positions,
            key=lambda p: scenario.item_at(p).unit_price().cents_for_computation(),
        )

        remaining_cents = budget.limit_money().cents_for_computation()
        units_by_position = [0] * scenario.size()

        for pos in sorted_positions:
            idx = pos.index_value()
            item = scenario.item_at(pos)
            unit_price_cents = item.unit_price().cents_for_computation()
            needed_units = item.required_quantity().units_value()

            # Quantas unidades podemos comprar desse item
            affordable = remaining_cents // unit_price_cents
            to_buy = min(needed_units, affordable)
            units_by_position[idx] = to_buy
            remaining_cents -= to_buy * unit_price_cents

        return PurchasePlan.of_units(units_by_position)
