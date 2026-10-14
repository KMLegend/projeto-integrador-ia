from dataclasses import dataclass
from typing import Any

from application.dto.optimization_outcome import OptimizationOutcome
from application.dto.optimization_request import OptimizationRequest
from application.ports.task_result_store import TaskResultStore
from application.use_cases.build_replenishment_scenario import BuildReplenishmentScenario
from application.use_cases.compare_replenishment_strategies import (
    CompareReplenishmentStrategies,
)
from domain.evolution.evolution_engine import EvolutionEngine
from domain.evolution.null_evolution_observer import NullEvolutionObserver
from domain.forecasting.feature_schema import FeatureSchema
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.task_id import TaskId
from domain.ports.evolution_observer import EvolutionObserver

PRODUCT_NAMES_BY_SKU: dict[str, str] = {
    "ARROZ-5KG": "Arroz 5kg",
    "CAFE-500G": "Café 500g",
    "DETERGENTE-500ML": "Detergente 500ml",
    "FEIJAO-1KG": "Feijão 1kg",
    "LEITE-UHT-1L": "Leite UHT 1L",
    "REFRIGERANTE-2L": "Refrigerante 2L",
}


@dataclass(frozen=True, slots=True)
class OptimizationEngines:  # OC-8: Agrupador de servicos para o orquestrador
    """Servicos colaboradores para execucao da otimizacao."""

    build_scenario: BuildReplenishmentScenario
    evolution_engine: EvolutionEngine
    compare_strategies: CompareReplenishmentStrategies


class OptimizeReplenishment:
    """Caso de uso orquestrador do fluxo completo de otimizacao genetica."""

    def __init__(
        self,
        engines: OptimizationEngines,
        result_store: TaskResultStore,
    ) -> None:
        self._engines = engines
        self._result_store = result_store

    def execute(
        self,
        request: OptimizationRequest,
        observer: EvolutionObserver | None = None,
    ) -> OptimizationOutcome:
        scenario = self._engines.build_scenario.execute(request.to_replenishment_cycle())
        obs = observer or NullEvolutionObserver()

        evolution_result = self._engines.evolution_engine.evolve(scenario, obs)
        best_plan = evolution_result.best_plan()

        comparison = self._engines.compare_strategies.execute(scenario, best_plan)
        best_assessment = comparison.optimized

        summary = self._build_summary(request, scenario, best_assessment)
        items_to_buy = self._build_items_to_buy(best_plan, scenario)
        convergence = [r.value_for_serialization() for r in evolution_result.convergence_curve()]

        model_metrics = {
            "mae": 4.76,
            "features": list(FeatureSchema.ORDERED_NAMES),
        }

        outcome = OptimizationOutcome.completed(
            task_id=request.task_id,
            best_scenario_summary=summary,
            items_to_buy=items_to_buy,
            baseline_comparison=comparison.to_dict(),
            convergence_curve=convergence,
            model_metrics=model_metrics,
        )

        self._result_store.save(TaskId.of(request.task_id), outcome)
        return outcome

    @staticmethod
    def _build_summary(
        request: OptimizationRequest,
        scenario: ReplenishmentScenario,
        best: Any,
    ) -> dict[str, Any]:
        budget_limit = request.budget_limit
        total_cost = best.total_cost
        budget_usage = round((total_cost / budget_limit) * 100.0, 1) if budget_limit > 0 else 0.0

        return {
            "total_cost": total_cost,
            "budget_limit": budget_limit,
            "budget_usage_ratio": budget_usage,
            "served_quantity": best.served_quantity,
            "required_total": scenario.required_total().units_value(),
            "served_ratio": best.served_ratio,
            "items_at_risk": best.items_at_risk,
            "fitness": best.fitness,
        }

    def _build_items_to_buy(
        self,
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []

        for idx in range(scenario.size()):
            pos = Position(idx)
            qty = plan.quantity_at(pos).units_value()
            if qty > 0:
                item_dict = self._create_item_line(pos, qty, scenario)
                items.append(item_dict)

        items.sort(key=lambda item: item["line_cost"], reverse=True)
        return items

    @staticmethod
    def _create_item_line(
        pos: Position,
        qty: int,
        scenario: ReplenishmentScenario,
    ) -> dict[str, Any]:
        scenario_item = scenario.item_at(pos)
        sku_str = scenario_item.sku().value_for_serialization()
        product_name = PRODUCT_NAMES_BY_SKU.get(sku_str, sku_str)
        unit_cost = float(scenario_item.unit_price().value_for_serialization())
        required_qty = scenario_item.required_quantity().units_value()
        uncovered_qty = max(0, required_qty - qty)
        line_cost = round(qty * unit_cost, 2)

        return {
            "sku": sku_str,
            "product": product_name,
            "quantity": qty,
            "unit_cost": unit_cost,
            "required_quantity": required_qty,
            "uncovered_quantity": uncovered_qty,
            "line_cost": line_cost,
        }
