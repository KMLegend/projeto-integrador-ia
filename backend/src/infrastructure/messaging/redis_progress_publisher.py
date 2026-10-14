from __future__ import annotations

import json
import logging

import redis

from domain.evolution.generation_report import GenerationReport
from domain.ports.evolution_observer import EvolutionObserver

logger = logging.getLogger(__name__)


class RedisProgressPublisher(EvolutionObserver):
    """Publicador de progresso evolutivo via canal Pub/Sub do Redis."""

    def __init__(
        self,
        task_id: str,
        redis_client: redis.Redis[str] | None = None,
        redis_url: str = "redis://localhost:6379/0",
    ) -> None:
        self._task_id = task_id
        self._client: redis.Redis[str] = redis_client or redis.Redis.from_url(
            redis_url, decode_responses=True
        )

    def on_generation(self, report: GenerationReport) -> None:
        channel = f"progress:{self._task_id}"
        message = {
            "generation": report.generation_number(),
            "max_fitness": report.best_fitness().value_for_serialization(),
            "status": "evolving",
        }
        try:
            self._client.publish(channel, json.dumps(message))
        except Exception as err:
            logger.warning(
                "Falha ao publicar progresso no Redis para tarefa %s (%s). Continuando execucao.",
                self._task_id,
                err,
            )

    def publish_terminal_state(
        self,
        status: str,
        generation: int = -1,
        max_fitness: float = 0.0,
    ) -> None:
        channel = f"progress:{self._task_id}"
        message = {
            "generation": generation,
            "max_fitness": max_fitness,
            "status": status,
        }
        try:
            self._client.publish(channel, json.dumps(message))
        except Exception as err:
            logger.warning(
                "Falha ao publicar estado terminal no Redis para tarefa %s: %s",
                self._task_id,
                err,
            )
