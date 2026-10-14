from unittest.mock import patch
from fastapi.testclient import TestClient

from application.dto.optimization_outcome import OptimizationOutcome
from core.config import get_settings
from core.container import build_task_result_store
from domain.model.task_id import TaskId
from main import app

client = TestClient(app)


def test_trigger_optimization_returns_202_with_task_id() -> None:
    payload = {
        "budget_limit": 1000.00,
        "dataset_reference": "historico_mensal_v1",
        "cycle_weeks": 4,
        "ga_parameters": {
            "population_size": 60,
            "generations": 100,
            "mutation_rate": 0.20,
            "parents_size": 20,
            "elite_size": 2,
            "random_seed": 42,
        },
    }

    with patch("core.celery_app.celery_app.send_task") as mock_send_task:
        response = client.post("/api/v1/optimize", json=payload)

        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "PROCESSING"
        assert data["message"] == "Algoritmo genético iniciado em background."
        mock_send_task.assert_called_once()


def test_trigger_optimization_validation_rejects_invalid_inputs() -> None:
    # budget_limit <= 0
    resp_bad_budget = client.post("/api/v1/optimize", json={"budget_limit": 0.0})
    assert resp_bad_budget.status_code == 422

    # elite_size > parents_size
    resp_bad_ga = client.post(
        "/api/v1/optimize",
        json={
            "ga_parameters": {
                "population_size": 50,
                "parents_size": 10,
                "elite_size": 20,
            }
        },
    )
    assert resp_bad_ga.status_code == 422


def test_get_status_returns_404_for_unknown_task() -> None:
    response = client.get("/api/v1/status/non-existent-task-id-xyz")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TASK_NOT_FOUND"


def test_get_status_returns_completed_result() -> None:
    settings = get_settings()
    store = build_task_result_store(settings)
    task_id = "test-task-completed-777"

    outcome = OptimizationOutcome.completed(
        task_id=task_id,
        best_scenario_summary={
            "total_cost": 987.44,
            "budget_limit": 1000.00,
            "budget_usage_ratio": 98.7,
            "served_quantity": 120,
            "required_total": 146,
            "served_ratio": 82.2,
            "items_at_risk": 1,
            "fitness": 816.92,
        },
        items_to_buy=[
            {
                "sku": "LEITE-UHT-1L",
                "product": "Leite UHT 1L",
                "quantity": 98,
                "unit_cost": 5.86,
                "required_quantity": 98,
                "uncovered_quantity": 0,
                "line_cost": 574.28,
            }
        ],
        baseline_comparison={
            "baseline": {
                "total_cost": 314.32,
                "served_quantity": 36,
                "served_ratio": 24.7,
                "items_at_risk": 2,
                "fitness": 236.58,
            },
            "optimized": {
                "total_cost": 987.44,
                "served_quantity": 120,
                "served_ratio": 82.2,
                "items_at_risk": 1,
                "fitness": 816.92,
            },
        },
        convergence_curve=[{"generation": 0, "max_fitness": 777.67}],
        model_metrics={"mae": 4.76, "features": ["f1", "f2"]},
    )
    store.save(TaskId.of(task_id), outcome)

    response = client.get(f"/api/v1/status/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["status"] == "COMPLETED"
    assert "result" in data
    assert data["result"]["best_scenario_summary"]["total_cost"] == 987.44
    # Garantia de D-01: projected_profit nao existe no payload
    assert "projected_profit" not in data["result"]["best_scenario_summary"]
