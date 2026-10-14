from pydantic import BaseModel


class OptimizeAcceptedResponse(BaseModel):
    """Resposta imediata da criacao da tarefa assincrona (HTTP 202)."""

    task_id: str
    status: str = "PROCESSING"
    message: str = "Algoritmo genético iniciado em background."


class ItemToBuySchema(BaseModel):
    """Linha do plano de compras para item com quantidade > 0."""

    sku: str
    product: str
    quantity: int
    unit_cost: float
    required_quantity: int
    uncovered_quantity: int
    line_cost: float


class BestScenarioSummarySchema(BaseModel):
    """Resumo estatistico do melhor cenario encontrado pelo AG (D-01: sem projected_profit)."""

    total_cost: float
    budget_limit: float
    budget_usage_ratio: float
    served_quantity: int
    required_total: int
    served_ratio: float
    items_at_risk: int
    fitness: float


class StrategySummarySchema(BaseModel):
    """Indicadores consolidados de uma estrategia."""

    total_cost: float
    served_quantity: int
    served_ratio: float
    items_at_risk: int
    fitness: float


class BaselineComparisonSchema(BaseModel):
    """Comparativo direto entre baseline e solucao otimizada."""

    baseline: StrategySummarySchema
    optimized: StrategySummarySchema


class ConvergencePointSchema(BaseModel):
    """Ponto individual da curva de convergencia."""

    generation: int
    max_fitness: float


class ModelMetricsSchema(BaseModel):
    """Metricas e explicabilidade do modelo preditivo."""

    mae: float
    features: list[str]


class OptimizationResultSchema(BaseModel):
    """Payload consolidado do resultado concluido da otimizacao."""

    best_scenario_summary: BestScenarioSummarySchema
    items_to_buy: list[ItemToBuySchema]
    baseline_comparison: BaselineComparisonSchema
    convergence_curve: list[ConvergencePointSchema]
    model_metrics: ModelMetricsSchema


class StatusResponseSchema(BaseModel):
    """Resposta da rota GET /api/v1/status/{task_id}."""

    task_id: str
    status: str
    result: OptimizationResultSchema | None = None
    error: dict[str, str] | None = None
