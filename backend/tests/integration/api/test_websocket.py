import asyncio
from unittest.mock import MagicMock, patch
import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from application.dto.optimization_outcome import OptimizationOutcome
from core.config import get_settings
from core.container import build_task_result_store
from domain.model.task_id import TaskId
from main import app

client = TestClient(app)


def test_websocket_rejects_unknown_task_with_4404() -> None:
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/v1/progress/unknown-task-999") as ws:
            ws.receive_json()

    assert exc_info.value.code == 4404


def test_websocket_streams_messages_and_closes_at_terminal_state() -> None:
    settings = get_settings()
    store = build_task_result_store(settings)
    task_id = "ws-test-task-123"
    store.save(TaskId.of(task_id), OptimizationOutcome.processing(task_id))

    async def fake_stream(_task_id: str):
        yield {"generation": 0, "max_fitness": 777.67, "status": "evolving"}
        yield {"generation": 10, "max_fitness": 816.92, "status": "evolving"}
        yield {"generation": 100, "max_fitness": 816.92, "status": "completed"}

    mock_subscriber = MagicMock()
    mock_subscriber.stream_progress = fake_stream

    with patch(
        "api.websockets.progress_socket.build_progress_subscriber",
        return_value=mock_subscriber,
    ):
        with client.websocket_connect(f"/ws/v1/progress/{task_id}") as ws:
            msg1 = ws.receive_json()
            assert msg1["generation"] == 0
            assert msg1["status"] == "evolving"

            msg2 = ws.receive_json()
            assert msg2["generation"] == 10

            msg3 = ws.receive_json()
            assert msg3["status"] == "completed"
