from typing import Any

from application.dto.optimization_outcome import OptimizationOutcome


class OutcomeMapper:
    """Mapeador entre OptimizationOutcome e dicionarios serializaveis."""

    @staticmethod
    def to_payload(
        outcome: OptimizationOutcome,
    ) -> dict[str, Any]:  # OC-8: Serializador de DTO para dicionario
        return {
            "task_id": outcome.task_id,
            "status": outcome.status,
            "result": OutcomeMapper._build_result_field(outcome),
            "error": outcome.error,
        }

    @staticmethod
    def _build_result_field(
        outcome: OptimizationOutcome,
    ) -> dict[str, Any] | None:  # OC-8: Montador de secoes
        if outcome.status != "COMPLETED":
            return None
        return {
            "best_scenario_summary": outcome.best_scenario_summary,
            "items_to_buy": outcome.items_to_buy,
            "baseline_comparison": outcome.baseline_comparison,
            "convergence_curve": outcome.convergence_curve,
            "model_metrics": outcome.model_metrics,
        }
