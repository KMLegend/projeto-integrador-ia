from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class OptimizationOutcome:  # OC-8: DTO de saida com payload completo da otimizacao
    """Resultado imutavel da execucao da otimizacao genetica."""

    task_id: str
    status: str
    best_scenario_summary: Mapping[str, Any] | None = None
    items_to_buy: Sequence[Mapping[str, Any]] | None = None
    baseline_comparison: Mapping[str, Any] | None = None
    convergence_curve: Sequence[Mapping[str, Any]] | None = None
    model_metrics: Mapping[str, Any] | None = None
    error: Mapping[str, str] | None = None

    @staticmethod
    def processing(task_id: str) -> "OptimizationOutcome":
        return OptimizationOutcome(task_id=task_id, status="PROCESSING")

    @staticmethod
    def failed(task_id: str, code: str, message: str) -> "OptimizationOutcome":
        return OptimizationOutcome(
            task_id=task_id,
            status="FAILED",
            error={"code": code, "message": message},
        )

    @staticmethod
    def completed(  # noqa: PLR0913  # OC-8: Factory instanciando DTO imutavel com multiplos atributos
        task_id: str,
        best_scenario_summary: Mapping[str, Any],
        items_to_buy: Sequence[Mapping[str, Any]],
        baseline_comparison: Mapping[str, Any],
        convergence_curve: Sequence[Mapping[str, Any]],
        model_metrics: Mapping[str, Any],
    ) -> "OptimizationOutcome":
        return OptimizationOutcome(
            task_id=task_id,
            status="COMPLETED",
            best_scenario_summary=best_scenario_summary,
            items_to_buy=items_to_buy,
            baseline_comparison=baseline_comparison,
            convergence_curve=convergence_curve,
            model_metrics=model_metrics,
        )

    def to_status_view(self) -> "OptimizationStatusView":
        res = self._build_result_dict() if self.status == "COMPLETED" else None
        return OptimizationStatusView(
            task_id=self.task_id, status=self.status, result=res, error=self.error
        )

    def _build_result_dict(self) -> Mapping[str, Any]:  # OC-8: Montagem de dicionario de resultado
        return {
            "best_scenario_summary": self.best_scenario_summary,
            "items_to_buy": self.items_to_buy,
            "baseline_comparison": self.baseline_comparison,
            "convergence_curve": self.convergence_curve,
            "model_metrics": self.model_metrics,
        }


@dataclass(frozen=True, slots=True)
class MaybeOutcome:
    """Option type para busca de resultados no TaskResultStore."""

    _outcome: OptimizationOutcome | None

    @staticmethod
    def present(outcome: OptimizationOutcome) -> "MaybeOutcome":
        return MaybeOutcome(outcome)

    @staticmethod
    def empty() -> "MaybeOutcome":
        return MaybeOutcome(None)

    def is_present(self) -> bool:
        return self._outcome is not None

    def value(self) -> OptimizationOutcome:
        if self._outcome is None:
            raise ValueError("Outcome is not present in MaybeOutcome")
        return self._outcome


@dataclass(frozen=True, slots=True)
class OptimizationStatusView:  # OC-8: DTO de status para consulta
    """Visao simplificada de status/resultado de uma tarefa de otimizacao."""

    task_id: str
    status: str
    result: Mapping[str, Any] | None = None
    error: Mapping[str, str] | None = None
