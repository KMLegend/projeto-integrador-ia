import asyncio
import contextlib
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from application.ports.progress_subscriber import ProgressSubscriber
from core.config import get_settings
from core.container import build_progress_subscriber, build_task_result_store
from domain.model.task_id import TaskId

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websockets"])


async def _stream_events(
    websocket: WebSocket, subscriber: ProgressSubscriber, task_id: str
) -> None:
    async for message in subscriber.stream_progress(task_id):
        if websocket.client_state.name != "CONNECTED":
            break
        await websocket.send_json(message)
        if message.get("status") in ("completed", "failed"):
            with contextlib.suppress(Exception):
                await websocket.close(code=1000)
            break


@router.websocket("/ws/v1/progress/{task_id}")
async def websocket_progress_endpoint(websocket: WebSocket, task_id: str) -> None:
    """Canal WebSocket para streaming em tempo real do progresso da otimizacao."""
    settings = get_settings()
    store = build_task_result_store(settings)
    maybe_outcome = store.find(TaskId.of(task_id))

    await websocket.accept()

    if not maybe_outcome.is_present():
        logger.warning("Conexao WebSocket rejeitada: tarefa %s nao encontrada.", task_id)
        await websocket.close(code=4404, reason="Task not found")
        return

    subscriber = build_progress_subscriber(settings)

    try:
        await _stream_events(websocket, subscriber, task_id)
    except (WebSocketDisconnect, asyncio.CancelledError):
        logger.info("Cliente desconectou do WebSocket da tarefa %s", task_id)
    except Exception as err:
        logger.error("Erro inesperado no WebSocket da tarefa %s: %s", task_id, err)
        with contextlib.suppress(Exception):
            await websocket.close(code=1011)
