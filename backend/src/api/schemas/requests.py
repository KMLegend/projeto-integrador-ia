from pydantic import BaseModel, Field, model_validator


class GeneticAlgorithmParametersSchema(BaseModel):
    """Parametros do algoritmo genetico com validacoes rigorosas."""

    population_size: int = Field(default=60, ge=10, le=500)
    generations: int = Field(default=100, ge=1, le=1000)
    mutation_rate: float = Field(default=0.20, ge=0.0, le=1.0)
    parents_size: int = Field(default=20, ge=2)
    elite_size: int = Field(default=2, ge=1)
    mutation_range: int = Field(default=10, ge=1)
    random_seed: int = Field(default=42)

    @model_validator(mode="after")
    def validate_sizes(self) -> "GeneticAlgorithmParametersSchema":
        if not (self.elite_size <= self.parents_size <= self.population_size):
            raise ValueError("elite_size deve ser <= parents_size <= population_size")
        return self


class OptimizeRequestSchema(BaseModel):
    """Payload de entrada da rota POST /api/v1/optimize."""

    budget_limit: float = Field(default=1000.00, gt=0.0)
    dataset_reference: str = Field(default="historico_mensal_v1")
    cycle_weeks: int = Field(default=4, ge=1)
    ga_parameters: GeneticAlgorithmParametersSchema = Field(
        default_factory=GeneticAlgorithmParametersSchema
    )
