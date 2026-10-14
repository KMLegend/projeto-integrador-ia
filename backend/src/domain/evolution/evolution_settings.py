from dataclasses import dataclass

from domain.errors.domain_errors import InvalidParametersError


# OC-8: Value Object de configuracao do algoritmo genetico (excecao autorizada em D-12)
@dataclass(frozen=True, slots=True)
class EvolutionSettings:
    population_size: int
    generations: int
    mutation_rate: float
    parents_size: int
    elite_size: int
    mutation_range: int
    random_seed: int

    @staticmethod
    def notebook_defaults() -> "EvolutionSettings":
        return EvolutionSettings(60, 100, 0.20, 20, 2, 10, 42)

    def __post_init__(self) -> None:
        self._validate_population_and_generations()
        self._validate_rates_and_counts()

    def _validate_population_and_generations(self) -> None:
        if self.population_size < 2:
            raise InvalidParametersError(
                f"Tamanho da populacao deve ser >= 2: {self.population_size}"
            )
        if self.generations < 1:
            raise InvalidParametersError(f"Numero de geracoes deve ser >= 1: {self.generations}")
        if not (0.0 <= self.mutation_rate <= 1.0):
            raise InvalidParametersError(
                f"Taxa de mutacao deve estar em [0.0, 1.0]: {self.mutation_rate}"
            )

    def _validate_rates_and_counts(self) -> None:
        if self.parents_size < 2 or self.parents_size > self.population_size:
            msg = f"Tamanho de pais ({self.parents_size}) fora de [2, {self.population_size}]"
            raise InvalidParametersError(msg)
        if self.elite_size < 0 or self.elite_size > self.parents_size:
            msg = f"Tamanho da elite ({self.elite_size}) fora de [0, {self.parents_size}]"
            raise InvalidParametersError(msg)
        if self.mutation_range < 1:
            raise InvalidParametersError(
                f"Intervalo de mutacao deve ser >= 1: {self.mutation_range}"
            )
        if self.random_seed < 0:
            raise InvalidParametersError(f"Semente aleatoria deve ser >= 0: {self.random_seed}")
