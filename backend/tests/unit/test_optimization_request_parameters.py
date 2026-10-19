import pytest

from application.dto.optimization_request import OptimizationRequest
from core.config import get_settings
from core.container import build_optimization_use_case
from domain.errors.domain_errors import InvalidBudgetError


def test_optimization_request_to_budget_constraint() -> None:
    req_default = OptimizationRequest(budget_limit=1000.0)
    budget = req_default.to_budget_constraint()
    assert budget.limit_money().cents_for_computation() == 100000
    assert budget.value_for_serialization() == 1000.00

    req_100 = OptimizationRequest(budget_limit=100.0)
    assert req_100.to_budget_constraint().value_for_serialization() == 100.00

    req_1 = OptimizationRequest(budget_limit=1.0)
    assert req_1.to_budget_constraint().value_for_serialization() == 1.00

    req_zero = OptimizationRequest(budget_limit=0.0)
    with pytest.raises(InvalidBudgetError):
        req_zero.to_budget_constraint()


def test_optimization_request_to_evolution_settings() -> None:
    req = OptimizationRequest(
        population_size=80,
        generations=50,
        mutation_rate=0.35,
        parents_size=25,
        elite_size=4,
        mutation_range=15,
        random_seed=123,
    )
    settings = req.to_evolution_settings()
    assert settings.population_size == 80
    assert settings.generations == 50
    assert settings.mutation_rate == 0.35
    assert settings.parents_size == 25
    assert settings.elite_size == 4
    assert settings.mutation_range == 15
    assert settings.random_seed == 123


def test_optimization_request_from_payload_with_custom_and_default_values() -> None:
    payload = {
        "budget_limit": 500.0,
        "dataset_reference": "historico_mensal_v1",
        "cycle_weeks": 8,
        "ga_parameters": {
            "population_size": 40,
            "generations": 20,
            "mutation_rate": 0.15,
            "parents_size": 10,
            "elite_size": 2,
            "mutation_range": 5,
            "random_seed": 777,
        },
    }
    req = OptimizationRequest.from_payload(payload)
    assert req.budget_limit == 500.0
    assert req.dataset_reference == "historico_mensal_v1"
    assert req.cycle_weeks == 8
    assert req.population_size == 40
    assert req.generations == 20
    assert req.mutation_rate == 0.15
    assert req.parents_size == 10
    assert req.elite_size == 2
    assert req.mutation_range == 5
    assert req.random_seed == 777

    # Payload vazio deve usar defaults configurados
    req_default = OptimizationRequest.from_payload(
        {},
        default_budget=1000.0,
        default_cycle=4,
        default_seed=42,
    )
    assert req_default.budget_limit == 1000.0
    assert req_default.cycle_weeks == 4
    assert req_default.population_size == 60
    assert req_default.generations == 100
    assert req_default.random_seed == 42


def test_optimization_honors_budget_limit_100() -> None:
    settings = get_settings()
    request = OptimizationRequest(task_id="test-budget-100", budget_limit=100.0, generations=10)
    use_case = build_optimization_use_case(settings, request=request)
    outcome = use_case.execute(request)

    summary = outcome.best_scenario_summary
    assert summary is not None
    assert summary["budget_limit"] == 100.0
    assert summary["total_cost"] <= 100.0
    assert summary["budget_usage_ratio"] <= 100.0

    comparison = outcome.baseline_comparison
    assert comparison is not None
    assert comparison["baseline"]["total_cost"] <= 100.0


def test_optimization_honors_budget_limit_1_producing_zero_cost_without_error() -> None:
    settings = get_settings()
    request = OptimizationRequest(task_id="test-budget-1", budget_limit=1.0, generations=5)
    use_case = build_optimization_use_case(settings, request=request)
    outcome = use_case.execute(request)

    summary = outcome.best_scenario_summary
    assert summary is not None
    assert summary["budget_limit"] == 1.0
    assert summary["total_cost"] == 0.00
    assert summary["budget_usage_ratio"] == 0.0
    assert outcome.items_to_buy is not None
    assert len(outcome.items_to_buy) == 0


def test_optimization_honors_generations_parameter() -> None:
    settings = get_settings()
    request = OptimizationRequest(task_id="test-gen-5", generations=5)
    use_case = build_optimization_use_case(settings, request=request)
    outcome = use_case.execute(request)

    assert len(outcome.convergence_curve) == 5
    assert [p["generation"] for p in outcome.convergence_curve] == [0, 1, 2, 3, 4]


def test_optimization_honors_random_seed_parameter() -> None:
    settings = get_settings()
    req_seed1 = OptimizationRequest(task_id="test-seed-1", random_seed=1, generations=5)
    req_seed999 = OptimizationRequest(task_id="test-seed-999", random_seed=999, generations=5)

    use_case_1 = build_optimization_use_case(settings, request=req_seed1)
    use_case_999 = build_optimization_use_case(settings, request=req_seed999)

    out_1 = use_case_1.execute(req_seed1)
    out_999 = use_case_999.execute(req_seed999)

    fit_1 = out_1.convergence_curve[0]["max_fitness"]
    fit_999 = out_999.convergence_curve[0]["max_fitness"]
    assert fit_1 != fit_999


def test_optimization_with_default_request_preserves_golden_values() -> None:
    settings = get_settings()
    request = OptimizationRequest(
        task_id="test-golden",
        budget_limit=1000.00,
        population_size=60,
        generations=100,
        random_seed=42,
    )
    use_case = build_optimization_use_case(settings, request=request)
    outcome = use_case.execute(request)

    summary = outcome.best_scenario_summary
    assert summary is not None
    assert summary["total_cost"] == 987.44
    assert summary["budget_limit"] == 1000.00
    assert summary["budget_usage_ratio"] == 98.7
    assert summary["served_quantity"] == 120
    assert summary["required_total"] == 146
    assert summary["served_ratio"] == 82.2
    assert summary["items_at_risk"] == 1
    assert summary["fitness"] == 816.92
