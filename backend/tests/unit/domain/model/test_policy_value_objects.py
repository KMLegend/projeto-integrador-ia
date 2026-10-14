import pytest

from domain.errors.domain_errors import InvalidBudgetError, InvalidCycleError
from domain.model.budget_constraint import BudgetConstraint
from domain.model.fitness_weights import FitnessWeights
from domain.model.money import Money
from domain.model.replenishment_cycle import ReplenishmentCycle
from domain.model.stock_risk_level import StockRiskLevel
from domain.model.stock_risk_thresholds import StockRiskThresholds


def test_fitness_weights_defaults() -> None:
    weights = FitnessWeights.default()
    assert weights.coverage == 10.0
    assert weights.risk_penalty == 5.0
    assert weights.coverage_weight() == 10.0
    assert weights.risk_penalty_weight() == 5.0


def test_replenishment_cycle_invariants() -> None:
    cycle = ReplenishmentCycle.default()
    assert cycle.weeks_count() == 4
    assert cycle.value_for_serialization() == 4

    with pytest.raises(InvalidCycleError):
        ReplenishmentCycle.of_weeks(0)
    with pytest.raises(InvalidCycleError):
        ReplenishmentCycle.of_weeks(-2)


def test_budget_constraint_invariants_and_methods() -> None:
    budget = BudgetConstraint.from_reais("1000.00")
    assert budget.value_for_serialization() == 1000.00
    assert not budget.is_exceeded_by(Money.from_reais("987.44"))
    assert budget.is_exceeded_by(Money.from_reais("1000.01"))

    # Divisao do orcamento entre 6 itens: 100000 // 6 = 16666 centavos (R$ 166,66)
    share = budget.share_among(6)
    assert share == Money.from_reais("166.66")

    with pytest.raises(InvalidBudgetError):
        BudgetConstraint.from_reais("0.00")
    with pytest.raises(InvalidBudgetError):
        BudgetConstraint.from_money(Money.zero())


def test_stock_risk_thresholds_and_level() -> None:
    thresholds = StockRiskThresholds.default()
    assert thresholds.multiplier_value() == 1.8

    assert StockRiskLevel.SHORTAGE.value == "SHORTAGE"
    assert StockRiskLevel.ADEQUATE.value == "ADEQUATE"
    assert StockRiskLevel.EXCESS.value == "EXCESS"
    assert StockRiskLevel.SHORTAGE.label_pt_br() == "Possível falta"
