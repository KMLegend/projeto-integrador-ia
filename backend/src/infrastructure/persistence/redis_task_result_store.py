from __future__ import annotations

import json
import logging

import redis

from application.dto.optimization_outcome import MaybeOutcome, OptimizationOutcome
from application.ports.task_result_store import TaskResultStore
from domain.model.task_id import TaskId

logger = logging.getLogger(__name__)


class RedisTaskResultStore(TaskResultStore):
    """Adaptador de persistencia de resultados de tarefas usando Redis."""

    def __init__(
        self,
        redis_client: redis.Redis[str] | None = None,
        redis_url: str = "redis://localhost:6379/1",
        ttl_seconds: int = 86400,
    ) -> None:
        self._client: redis.Redis[str] = redis_client or redis.Redis.from_url(
            redis_url, decode_responses=True
        )
        self._ttl_seconds = ttl_seconds

    def save(self, task_id: TaskId, outcome: OptimizationOutcome) -> None:
        key = f"result:{task_id.value_for_serialization()}"
        payload = {
            "task_id": outcome.task_id,
            "status": outcome.status,
            "best_scenario_summary": outcome.best_scenario_summary,
            "items_to_buy": outcome.items_to_buy,
            "baseline_comparison": outcome.baseline_comparison,
            "convergence_curve": outcome.convergence_curve,
            "model_metrics": outcome.model_metrics,
            "error": outcome.error,
        }
        try:
            self._client.set(key, json.dumps(payload), ex=self._ttl_seconds)
        except Exception as err:
            logger.error("Falha ao salvar resultado da tarefa %s no Redis: %s", key, err)

    def find(self, task_id: TaskId) -> MaybeOutcome:
        key = f"result:{task_id.value_for_serialization()}"
        try:
            raw = self._client.get(key)
            if not raw:
                return MaybeOutcome.empty()
            data = json.loads(str(raw))
            outcome = OptimizationOutcome(
                task_id=data["task_id"],
                status=data["status"],
                best_scenario_summary=data.get("best_scenario_summary"),
                items_to_buy=data.get("items_to_buy"),
                baseline_comparison=data.get("baseline_comparison"),
                convergence_curve=data.get("convergence_curve"),
                model_metrics=data.get("model_metrics"),
                error=data.get("error"),
            )
            return MaybeOutcome.present(outcome)
        except Exception as err:
            logger.error("Falha ao buscar resultado da tarefa %s no Redis: %s", key, err)
            return MaybeOutcome.empty()
