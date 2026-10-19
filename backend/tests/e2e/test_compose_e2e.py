import json
import os
import time

import httpx
import pytest
import websockets.exceptions
import websockets.sync.client

pytestmark = pytest.mark.e2e


def _probe_candidate() -> str | None:
    for candidate in ["http://localhost:8000", "http://api_backend:8000"]:
        try:
            if httpx.get(f"{candidate}/health", timeout=2.0).status_code == 200:
                return candidate
        except Exception:
            continue
    return None


def get_base_urls() -> tuple[str, str]:
    api_url = os.getenv("API_BASE_URL") or _probe_candidate() or "http://localhost:8000"
    ws_default = api_url.replace("http://", "ws://").replace("https://", "wss://")
    ws_url = os.getenv("WS_BASE_URL") or ws_default
    return api_url.rstrip("/"), ws_url.rstrip("/")


@pytest.fixture(scope="session", autouse=True)
def ensure_stack_available() -> None:
    """FIX 7: Pula a execucao caso o ambiente Docker Compose nao esteja acessivel."""
    api_url, _ = get_base_urls()
    try:
        res = httpx.get(f"{api_url}/health", timeout=2.0)
        if res.status_code != 200:
            pytest.skip(f"Stack Docker nao disponivel em {api_url} (HTTP {res.status_code})")
    except Exception as exc:
        pytest.skip(f"Stack Docker nao disponivel em {api_url}: {exc}")


def test_api_health_check_responds_healthy() -> None:
    """Criterio 3: curl localhost:8000/health -> 200 e status healthy."""
    api_url, _ = get_base_urls()
    response = httpx.get(f"{api_url}/health", timeout=10.0)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


def test_immediate_status_and_websocket_after_accepted() -> None:
    """FIX 1 & FIX 17: Tarefa imediatamente consultavel apos 202 com status PROCESSING."""
    api_url, base_ws = get_base_urls()
    start_resp = httpx.post(
        f"{api_url}/api/v1/optimize",
        json={"budget_limit": 1000.0, "dataset_reference": "default"},
        timeout=10.0,
    )
    assert start_resp.status_code == 202
    task_id = start_resp.json()["task_id"]
    assert task_id

    # Imediatamente consulta status sem sleep ou lacos
    status_resp = httpx.get(f"{api_url}/api/v1/status/{task_id}", timeout=2.0)
    assert status_resp.status_code == 200
    current_status = status_resp.json()
    assert current_status["status"] in ("PROCESSING", "COMPLETED")

    # Imediatamente conecta ao WebSocket sem fechar com 4404
    ws_url = f"{base_ws}/ws/v1/progress/{task_id}"
    with websockets.sync.client.connect(ws_url, close_timeout=5) as ws:
        msg = ws.recv(timeout=10.0)
        data = json.loads(msg)
        assert data.get("status") in ("evolving", "completed")


def test_unknown_dataset_returns_422_synchronously() -> None:
    """FIX 15(c): dataset_reference desconhecido rejeitado na borda com HTTP 422."""
    api_url, _ = get_base_urls()
    resp = httpx.post(
        f"{api_url}/api/v1/optimize",
        json={"budget_limit": 1000.0, "dataset_reference": "dataset_inexistente_xyz"},
        timeout=5.0,
    )
    assert resp.status_code == 422
    data = resp.json()
    assert data.get("error", {}).get("code") == "UNKNOWN_DATASET"


def test_nonexistent_task_returns_404_and_websocket_4404() -> None:
    """FIX 1: Tarefa inexistente devolve 404 no status e fecha WebSocket com 4404."""
    api_url, base_ws = get_base_urls()
    fake_id = "00000000-0000-0000-0000-000000000000"
    status_resp = httpx.get(f"{api_url}/api/v1/status/{fake_id}", timeout=2.0)
    assert status_resp.status_code == 404

    ws_url = f"{base_ws}/ws/v1/progress/{fake_id}"
    with websockets.sync.client.connect(ws_url, close_timeout=5) as ws:
        with pytest.raises(websockets.exceptions.ConnectionClosed) as exc_info:
            ws.recv(timeout=5.0)
        assert exc_info.value.rcvd.code == 4404


def test_end_to_end_optimization_pipeline_with_reference_scenario() -> None:
    """Criterios 4 e 5: POST /api/v1/optimize -> 202, COMPLETED em ate 60s com valores-ouro."""
    request_payload = {
        "budget_limit": 1000.0,
        "dataset_reference": "default",
        "ga_parameters": {
            "population_size": 60,
            "generations": 100,
            "mutation_rate": 0.20,
            "parents_size": 20,
            "elite_size": 2,
            "random_seed": 42,
        },
        "cycle_weeks": 4,
    }

    api_url, _ = get_base_urls()
    # 1. Enfileira a tarefa
    start_resp = httpx.post(
        f"{api_url}/api/v1/optimize",
        json=request_payload,
        timeout=10.0,
    )
    assert start_resp.status_code == 202
    start_data = start_resp.json()
    task_id = start_data["task_id"]
    assert task_id

    # 2. Aguarda conclusao da tarefa com polling (limite maximo de 60 segundos)
    deadline = time.time() + 60.0
    completed_data = None

    while time.time() < deadline:
        status_resp = httpx.get(
            f"{api_url}/api/v1/status/{task_id}",
            timeout=10.0,
        )
        assert status_resp.status_code == 200
        current_status = status_resp.json()

        if current_status["status"] == "COMPLETED":
            completed_data = current_status
            break
        if current_status["status"] == "FAILED":
            pytest.fail(f"Tarefa de otimizacao falhou: {current_status}")

        time.sleep(1.0)

    assert completed_data is not None, "A otimização não concluiu em até 60 segundos."

    # 3. Validação rigorosa dos valores-ouro e regras de negócio
    result = completed_data["result"]
    assert result is not None

    # D-01: projected_profit NUNCA deve ser emitido
    assert "projected_profit" not in str(completed_data)

    summary = result["best_scenario_summary"]
    assert summary["total_cost"] == 987.44
    assert summary["budget_limit"] == 1000.00
    assert summary["budget_usage_ratio"] == 98.7
    assert summary["served_quantity"] == 120
    assert summary["required_total"] == 146
    assert summary["served_ratio"] == 82.2
    assert summary["items_at_risk"] == 1
    assert summary["fitness"] == pytest.approx(816.92, abs=0.01)

    # Validacao do comparativo baseline vs otimizado
    comparison = result["baseline_comparison"]
    baseline = comparison["baseline"]
    assert baseline["total_cost"] == 314.32
    assert baseline["served_quantity"] == 36
    assert baseline["items_at_risk"] == 2
    assert baseline["fitness"] == pytest.approx(236.58, abs=0.01)

    # Validacao da lista de itens comprados
    items = result["items_to_buy"]
    assert len(items) == 2  # Leite (98) e Cafe (22)
    assert all(item["quantity"] > 0 for item in items)
    assert items[0]["line_cost"] >= items[1]["line_cost"]
    assert items[0]["sku"] == "LEITE-UHT-1L"
    assert items[1]["sku"] == "CAFE-500G"


def test_websocket_receives_progress_messages_with_increasing_generations() -> None:
    """Criterio 6: WebSocket recebe >= 2 mensagens de progresso com generation crescente."""
    request_payload = {
        "budget_limit": 1000.0,
        "dataset_reference": "default",
        "ga_parameters": {
            "population_size": 60,
            "generations": 100,
            "mutation_rate": 0.20,
            "parents_size": 20,
            "elite_size": 2,
            "random_seed": 42,
        },
    }

    api_url, base_ws = get_base_urls()
    start_resp = httpx.post(f"{api_url}/api/v1/optimize", json=request_payload, timeout=10.0)
    assert start_resp.status_code == 202
    task_id = start_resp.json()["task_id"]

    received_messages = []
    ws_url = f"{base_ws}/ws/v1/progress/{task_id}"

    try:
        with websockets.sync.client.connect(ws_url, close_timeout=15) as ws:
            for _ in range(15):
                try:
                    msg = ws.recv(timeout=10.0)
                    data = json.loads(msg)
                    received_messages.append(data)
                    if data.get("status") in ("completed", "failed"):
                        break
                except TimeoutError:
                    break
    except Exception as e:
        pytest.fail(f"Falha na conexao WebSocket {ws_url}: {e}")

    assert len(received_messages) >= 2, (
        f"Esperado >= 2 mensagens de progresso, recebido: {received_messages}"
    )
    generations = [m["generation"] for m in received_messages]
    assert generations == sorted(generations)
    assert received_messages[-1]["status"] == "completed"
    # FIX 3: Frame terminal completed possui fitness real > 0
    assert received_messages[-1]["max_fitness"] > 0.0


@pytest.mark.parametrize("budget_limit", [1.0, 100.0, 500.0, 1000.0])
def test_e2e_optimization_strictly_respects_budget_limit(budget_limit: float) -> None:
    """FIX 19: Otimizacao respeita estritamente o budget_limit (RN-05)."""
    api_url, _ = get_base_urls()
    start_resp = httpx.post(
        f"{api_url}/api/v1/optimize",
        json={
            "budget_limit": budget_limit,
            "dataset_reference": "default",
            "ga_parameters": {"population_size": 20, "generations": 5, "random_seed": 42},
        },
        timeout=10.0,
    )
    assert start_resp.status_code == 202
    task_id = start_resp.json()["task_id"]

    deadline = time.time() + 30.0
    completed_data = None
    while time.time() < deadline:
        status_resp = httpx.get(f"{api_url}/api/v1/status/{task_id}", timeout=10.0)
        assert status_resp.status_code == 200
        current_status = status_resp.json()
        if current_status["status"] == "COMPLETED":
            completed_data = current_status
            break
        if current_status["status"] == "FAILED":
            pytest.fail(f"Tarefa de otimizacao falhou: {current_status}")
        time.sleep(0.5)

    assert completed_data is not None, f"Otimizacao com budget {budget_limit} nao concluiu a tempo."
    summary = completed_data["result"]["best_scenario_summary"]
    assert summary["budget_limit"] == budget_limit
    assert summary["total_cost"] <= budget_limit
    assert summary["budget_usage_ratio"] <= 100.0
