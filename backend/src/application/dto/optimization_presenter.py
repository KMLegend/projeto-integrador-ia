from typing import Any

from application.dto.dataset_context import DatasetContext
from application.dto.optimization_outcome import OptimizationOutcome
from application.dto.optimization_request import OptimizationRequest
from domain.forecasting.feature_schema import FeatureSchema
from domain.model.position import Position
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario


class OptimizationPresenter:
    """Apresentador e montador de payloads de resultado da otimizacao."""

    @staticmethod
    def build_outcome(  # OC-8: Metodo de apresentacao agrupando secoes do payload
        request: OptimizationRequest,
        scenario: ReplenishmentScenario,
        evolution_result: Any,
        comparison: Any,
        context: DatasetContext | None = None,
    ) -> OptimizationOutcome:
        return OptimizationOutcome.completed(
            task_id=request.task_id,
            best_scenario_summary=OptimizationPresenter.build_summary(
                request, scenario, comparison.optimized
            ),
            items_to_buy=OptimizationPresenter.build_items_to_buy(
                evolution_result.best_plan(), scenario, context
            ),
            baseline_comparison=comparison.to_dict(),
            convergence_curve=[
                r.value_for_serialization() for r in evolution_result.convergence_curve()
            ],
            model_metrics=OptimizationPresenter.build_model_metrics(context),
        )

    @staticmethod
    def build_model_metrics(context: DatasetContext | None = None) -> dict[str, Any]:
        mae = round(context.model_mae, 2) if context is not None else 0.0
        return {"mae": mae, "features": list(FeatureSchema.ORDERED_NAMES)}

    @staticmethod
    def build_summary(  # OC-8: Montagem de dicionario de resumo com 8 campos de KPI
        request: OptimizationRequest,
        scenario: ReplenishmentScenario,
        best: Any,
    ) -> dict[str, Any]:
        usage = OptimizationPresenter._calc_usage(best.total_cost, request.budget_limit)
        return {
            "total_cost": best.total_cost,
            "budget_limit": request.budget_limit,
            "budget_usage_ratio": usage,
            "served_quantity": best.served_quantity,
            "required_total": scenario.required_total().units_value(),
            "served_ratio": best.served_ratio,
            "items_at_risk": best.items_at_risk,
            "fitness": best.fitness,
        }

    @staticmethod
    def _calc_usage(cost: float, limit: float) -> float:
        return round((cost / limit) * 100.0, 1) if limit > 0 else 0.0

    @staticmethod
    def build_items_to_buy(  # OC-8: Compreensao de lista e ordenacao decrescente
        plan: PurchasePlan,
        scenario: ReplenishmentScenario,
        context: DatasetContext | None = None,
    ) -> list[dict[str, Any]]:
        items = [
            OptimizationPresenter._create_item_line(
                Position(i), plan.quantity_at(Position(i)).units_value(), scenario, context
            )
            for i in range(scenario.size())
            if plan.quantity_at(Position(i)).units_value() > 0
        ]
        return sorted(items, key=lambda item: item["line_cost"], reverse=True)

    @staticmethod
    def _create_item_line(  # OC-8: Montagem de dicionario de linha de compra
        pos: Position,
        qty: int,
        scenario: ReplenishmentScenario,
        context: DatasetContext | None = None,
    ) -> dict[str, Any]:
        item = scenario.item_at(pos)
        sku = item.sku().value_for_serialization()
        req = item.required_quantity().units_value()
        unit_cost = float(item.unit_price().value_for_serialization())
        return {
            "sku": sku,
            "product": context.name_for(sku) if context is not None else sku,
            "quantity": qty,
            "unit_cost": unit_cost,
            "required_quantity": req,
            "uncovered_quantity": max(0, req - qty),
            "line_cost": round(qty * unit_cost, 2),
        }
