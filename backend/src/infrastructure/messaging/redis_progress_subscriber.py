import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class RedisProgressSubscriber:
    """Assinante assincrono de canal Pub/Sub do Redis para repasse via WebSocket."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        self._redis_url = redis_url

    @staticmethod
    def _extract_data(message: dict[str, Any]) -> tuple[dict[str, Any] | None, bool]:
        if message.get("type") != "message":
            return None, False
        data: dict[str, Any] = json.loads(str(message["data"]))
        return data, data.get("status") in ("completed", "failed")

    async def _listen_loop(
        self, pubsub: aioredis.client.PubSub
    ) -> AsyncGenerator[dict[str, Any], None]:
        async for message in pubsub.listen():
            data, is_done = self._extract_data(message)
            if data is not None:
                yield data
            if is_done:
                break

    async def stream_progress(self, task_id: str) -> AsyncGenerator[dict[str, Any], None]:
        client = aioredis.from_url(self._redis_url, decode_responses=True)
        pubsub = client.pubsub()
        channel = f"progress:{task_id}"

        try:
            await pubsub.subscribe(channel)
            async for item in self._listen_loop(pubsub):
                yield item
        except Exception as err:
            logger.warning("Subscriber pubsub encerrou com erro para tarefa %s: %s", task_id, err)
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await client.aclose()
