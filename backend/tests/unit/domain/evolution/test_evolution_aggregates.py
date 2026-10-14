import pytest

from domain.errors.domain_errors import InvalidParametersError
from domain.evolution.evolution_result import EvolutionResult
from domain.evolution.evolution_settings import EvolutionSettings
from domain.evolution.generation_history import GenerationHistory
from domain.evolution.generation_report import GenerationReport
from domain.evolution.population import Population
from domain.model.fitness_score import FitnessScore
from domain.model.plan_assessment import PlanAssessment
from domain.model.purchase_plan import PurchasePlan


def test_evolution_settings_notebook_defaults() -> None:
    settings = EvolutionSettings.notebook_defaults()
    assert settings.population_size == 60
    assert settings.generations == 100
    assert settings.mutation_rate == 0.20
    assert settings.parents_size == 20
    assert settings.elite_size == 2
    assert settings.mutation_range == 10
    assert settings.random_seed == 42


def test_evolution_settings_validations() -> None:
    with pytest.raises(InvalidParametersError):
        EvolutionSettings(1, 100, 0.20, 20, 2, 10, 42)  # population_size < 2

    with pytest.raises(InvalidParametersError):
        EvolutionSettings(60, 0, 0.20, 20, 2, 10, 42)  # generations < 1

    with pytest.raises(InvalidParametersError):
        EvolutionSettings(60, 100, 1.5, 20, 2, 10, 42)  # mutation_rate > 1.0

    with pytest.raises(InvalidParametersError):
        EvolutionSettings(60, 100, 0.20, 70, 2, 10, 42)  # parents_size > population_size

    with pytest.raises(InvalidParametersError):
        EvolutionSettings(60, 100, 0.20, 20, 25, 10, 42)  # elite_size > parents_size


def test_population_first_class_collection() -> None:
    p1 = PurchasePlan.of_units((0, 10))
    p2 = PurchasePlan.of_units((0, 20))
    pop = Population.of_plans([p1, p2])

    assert pop.size() == 2
    assert pop.plan_at(0) == p1
    assert pop.plan_at(1) == p2
    assert len(pop.plans()) == 2

    p3 = PurchasePlan.of_units((0, 30))
    extended = pop.extended_with(Population.of_plans([p3]))
    assert extended.size() == 3


def test_generation_history_and_result() -> None:
    rep0 = GenerationReport(0, FitnessScore(777.67))
    rep1 = GenerationReport(1, FitnessScore(816.92))

    history = GenerationHistory.empty().appended_with(rep0).appended_with(rep1)
    assert history.size() == 2
    assert history.at(0) == rep0
    assert history.best_fitness() == FitnessScore(816.92)

    plan = PurchasePlan.of_units((0, 22, 0, 0, 98, 0))
    assessment = PlanAssessment(plan, FitnessScore(816.92))
    result = EvolutionResult(assessment, history)

    assert result.best_plan() == plan
    assert result.best_fitness() == FitnessScore(816.92)
    assert len(result.convergence_curve()) == 2
