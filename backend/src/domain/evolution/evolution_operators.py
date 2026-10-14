from dataclasses import dataclass

from domain.evolution.generation_report import GenerationReport
from domain.evolution.local_shift_mutation import LocalShiftMutation
from domain.evolution.plan_factory import PlanFactory
from domain.evolution.population import Population
from domain.evolution.truncation_selection import TruncationSelection
from domain.evolution.uniform_crossover import UniformCrossover
from domain.model.plan_assessment import PlanAssessment
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.ports.fitness_policy import FitnessPolicy
from domain.ports.plan_repair import PlanRepair
from domain.ports.random_source import RandomSource


@dataclass(frozen=True, slots=True)
class EvaluationPipeline:
    """Sub-agrupamento de avaliacao e selecao para cumprir OC-8."""

    _policy: FitnessPolicy
    _selection: TruncationSelection

    def evaluate(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PlanAssessment:
        return self._policy.evaluate(plan, scenario)

    def select(self, population: Population, scenario: ReplenishmentScenario) -> Population:
        return self._selection.select(population, self._policy, scenario)

    def evaluate_generation(
        self,
        population: Population,
        scenario: ReplenishmentScenario,
        generation: int,
    ) -> GenerationReport:
        ranked = population.ranked_by(self._policy, scenario)
        best_assessment = self._policy.evaluate(ranked.plan_at(0), scenario)
        return GenerationReport(generation, best_assessment.fitness())


@dataclass(frozen=True, slots=True)
class GeneticPipeline:
    """Sub-agrupamento de recombinacao e mutacao para cumprir OC-8."""

    _crossover: UniformCrossover
    _mutation: LocalShiftMutation

    def recombine_and_mutate(
        self,
        parent_a: PurchasePlan,
        parent_b: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> PurchasePlan:
        child = self._crossover.combine(parent_a, parent_b, scenario)
        return self._mutation.mutate(child, scenario)

    def random_index_below(
        self,
        limit: int,
    ) -> int:
        return self._crossover.random_index_below(limit)


@dataclass(frozen=True, slots=True)
class VariationOperators:
    """Sub-agrupamento de criacao e reproducao para cumprir OC-8."""

    _factory: PlanFactory
    _genetic: GeneticPipeline

    def create_initial_population(
        self,
        size: int,
        scenario: ReplenishmentScenario,
    ) -> Population:
        plans = [self._factory.random_plan(scenario) for _ in range(size)]
        return Population.of_plans(plans)

    def breed_child(
        self,
        parent_a: PurchasePlan,
        parent_b: PurchasePlan,
        scenario: ReplenishmentScenario,
    ) -> PurchasePlan:
        return self._genetic.recombine_and_mutate(parent_a, parent_b, scenario)

    def random_index_below(
        self,
        limit: int,
    ) -> int:
        return self._genetic.random_index_below(limit)


@dataclass(frozen=True, slots=True)
class EvolutionOperators:
    """Agrupamento de operadores evolutivos cumprindo a Regra 8 (max 2 atributos)."""

    _evaluation: EvaluationPipeline
    _variation: VariationOperators

    @staticmethod
    def standard(
        random_source: RandomSource,
        repair: PlanRepair,
        policy: FitnessPolicy,
        parents_size: int = 20,
    ) -> "EvolutionOperators":
        evaluation = EvaluationPipeline(
            _policy=policy,
            _selection=TruncationSelection(_parents_size=parents_size),
        )
        genetic = GeneticPipeline(
            _crossover=UniformCrossover(random_source, repair),
            _mutation=LocalShiftMutation(random_source, repair),
        )
        variation = VariationOperators(
            _factory=PlanFactory(random_source, repair),
            _genetic=genetic,
        )
        return EvolutionOperators(evaluation, variation)

    def create_initial_population(
        self,
        size: int,
        scenario: ReplenishmentScenario,
    ) -> Population:
        return self._variation.create_initial_population(size, scenario)

    def evaluate_generation(
        self,
        population: Population,
        scenario: ReplenishmentScenario,
        generation: int,
    ) -> GenerationReport:
        return self._evaluation.evaluate_generation(population, scenario, generation)

    def select_parents(
        self,
        population: Population,
        scenario: ReplenishmentScenario,
    ) -> Population:
        return self._evaluation.select(population, scenario)

    def breed_next_generation(
        self,
        parents: Population,
        target_size: int,
        elite_size: int,
        scenario: ReplenishmentScenario,
    ) -> Population:
        new_plans = list(parents.top(elite_size).plans())
        num_parents = parents.size()
        while len(new_plans) < target_size:
            idx_a = self._variation.random_index_below(num_parents)
            idx_b = self._variation.random_index_below(num_parents)
            child = self._variation.breed_child(
                parents.plan_at(idx_a), parents.plan_at(idx_b), scenario
            )
            new_plans.append(child)
        return Population.of_plans(new_plans)

    def best_assessment(
        self,
        population: Population,
        scenario: ReplenishmentScenario,
    ) -> PlanAssessment:
        ranked = population.ranked_by(self._evaluation._policy, scenario)
        return self._evaluation.evaluate(ranked.plan_at(0), scenario)
