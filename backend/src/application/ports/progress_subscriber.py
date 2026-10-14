from collections.abc import AsyncGenerator
from typing import Any, Protocol


class ProgressSubscriber(Protocol):
    """Porta para streaming de eventos de progresso."""

    def stream_progress(self, task_id: str) -> AsyncGenerator[dict[str, Any], None]:
        """Produz gerador assincrono de mensagens de progresso para a tarefa."""
        ...
