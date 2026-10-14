from dataclasses import dataclass

from domain.errors.domain_errors import InvalidParametersError


@dataclass(frozen=True, slots=True)
class EvolutionSettings:  # OC-8: Parameter Object imutavel para hiperparametros do AG
    """Parametros de configuracao do algoritmo genetico."""

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
        self._validate_structural()
        self._validate_stochastic()

    def _validate_structural(self) -> None:
        self._validate_population()
        self._validate_generations()
        self._validate_parents()
        self._validate_elite()

    def _validate_stochastic(self) -> None:
        self._validate_rate()
        self._validate_range()
        self._validate_seed()

    def _validate_population(self) -> None:
        if self.population_size < 2:
            raise InvalidParametersError(
                f"Tamanho da populacao deve ser >= 2: {self.population_size}"
            )

    def _validate_generations(self) -> None:
        if self.generations < 1:
            raise InvalidParametersError(f"Numero de geracoes deve ser >= 1: {self.generations}")

    def _validate_rate(self) -> None:
        if not (0.0 <= self.mutation_rate <= 1.0):
            raise InvalidParametersError(
                f"Taxa de mutacao deve estar em [0.0, 1.0]: {self.mutation_rate}"
            )

    def _validate_parents(self) -> None:
        if self.parents_size < 2 or self.parents_size > self.population_size:
            msg = f"Tamanho de pais ({self.parents_size}) fora de [2, {self.population_size}]"
            raise InvalidParametersError(msg)

    def _validate_elite(self) -> None:
        if self.elite_size < 0 or self.elite_size > self.parents_size:
            msg = f"Tamanho da elite ({self.elite_size}) fora de [0, {self.parents_size}]"
            raise InvalidParametersError(msg)

    def _validate_range(self) -> None:
        if self.mutation_range < 1:
            raise InvalidParametersError(
                f"Intervalo de mutacao deve ser >= 1: {self.mutation_range}"
            )

    def _validate_seed(self) -> None:
        if self.random_seed < 0:
            raise InvalidParametersError(f"Semente aleatoria deve ser >= 0: {self.random_seed}")
