import os
import time
import httpx
import pytest

def get_base_urls() -> tuple[str, str]:
    api_url = os.getenv("API_BASE_URL")
    if not api_url:
        for candidate in ["http://localhost:8000", "http://api_backend:8000"]:
            try:
                res = httpx.get(f"{candidate}/health", timeout=2.0)
                if res.status_code == 200:
                    api_url = candidate
                    break
            except Exception:
                continue
    if not api_url:
        api_url = "http://localhost:8000"

    ws_url = os.getenv("WS_BASE_URL")
    if not ws_url:
        ws_url = api_url.replace("http://", "ws://").replace("https://", "wss://")

    return api_url.rstrip("/"), ws_url.rstrip("/")


def test_api_health_check_responds_healthy() -> None:
    """Criterio 3: curl localhost:8000/health -> 200 e status healthy."""
    api_url, _ = get_base_urls()
    response = httpx.get(f"{api_url}/health", timeout=10.0)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


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
        elif current_status["status"] == "FAILED":
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
    assert len(items) == 2  # Leite (98) e Feijao (22)
    assert all(item["quantity"] > 0 for item in items)
    # Ordenado por line_cost decrescente
    assert items[0]["line_cost"] >= items[1]["line_cost"]
    assert items[0]["sku"] == "LEITE-UHT-1L"
    assert items[1]["sku"] == "CAFE-500G"


def test_websocket_receives_progress_messages_with_increasing_generations() -> None:
    """Criterio 6: WebSocket recebe >= 2 mensagens de progresso com generation crescente."""
    import json
    import websockets.sync.client

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

    assert len(received_messages) >= 2, f"Esperado >= 2 mensagens de progresso, recebido: {received_messages}"
    generations = [m["generation"] for m in received_messages]
    assert generations == sorted(generations)
    assert received_messages[-1]["status"] == "completed"

