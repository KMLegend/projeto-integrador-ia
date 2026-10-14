from dataclasses import dataclass
from typing import Any

from domain.evolution.evolution_settings import EvolutionSettings
from domain.model.budget_constraint import BudgetConstraint
from domain.model.replenishment_cycle import ReplenishmentCycle


@dataclass(frozen=True, slots=True)
class OptimizationRequest:  # OC-8: DTO de entrada para caso de uso de otimizacao
    """Parametros da requisicao de otimizacao assincrona ou sincrona."""

    task_id: str = "default-task"
    budget_limit: float = 1000.00
    dataset_reference: str = "historico_mensal_v1"
    cycle_weeks: int = 4
    population_size: int = 60
    generations: int = 100
    mutation_rate: float = 0.20
    parents_size: int = 20
    elite_size: int = 2
    mutation_range: int = 10
    random_seed: int = 42

    def to_budget_constraint(self) -> BudgetConstraint:
        return BudgetConstraint.from_reais(f"{self.budget_limit:.2f}")

    def to_replenishment_cycle(self) -> ReplenishmentCycle:
        return ReplenishmentCycle.of_weeks(self.cycle_weeks)

    def to_evolution_settings(self) -> EvolutionSettings:
        return EvolutionSettings(
            population_size=self.population_size,
            generations=self.generations,
            mutation_rate=self.mutation_rate,
            parents_size=self.parents_size,
            elite_size=self.elite_size,
            mutation_range=self.mutation_range,
            random_seed=self.random_seed,
        )

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "OptimizationRequest":
        ga_params = payload.get("ga_parameters") or {}
        return OptimizationRequest(
            task_id=str(payload.get("task_id", "default-task")),
            budget_limit=float(payload.get("budget_limit", 1000.00)),
            dataset_reference=str(payload.get("dataset_reference", "historico_mensal_v1")),
            cycle_weeks=int(payload.get("cycle_weeks", 4)),
            population_size=int(ga_params.get("population_size", 60)),
            generations=int(ga_params.get("generations", 100)),
            mutation_rate=float(ga_params.get("mutation_rate", 0.20)),
            parents_size=int(ga_params.get("parents_size", 20)),
            elite_size=int(ga_params.get("elite_size", 2)),
            mutation_range=int(ga_params.get("mutation_range", 10)),
            random_seed=int(ga_params.get("random_seed", 42)),
        )
