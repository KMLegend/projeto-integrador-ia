---
id: 02-contratos-de-codigo-backend
dominio: implementacao
palavras-chave: contratos de codigo, assinaturas, classes, protocols, casos de uso, celery, fastapi, pydantic, backend, API
fonte-da-verdade: .context/00-arquitetura-tecnica/contratos_de_api.md + 01-dominio-e-negocio/*
depende-de: [01-estrutura-de-diretorios, 01-dominio-e-negocio/04-funcao-fitness, 01-dominio-e-negocio/05-algoritmo-genetico]
---

# Contratos de Código — Backend

Assinaturas normativas. Implemente **exatamente** estes nomes e tipos; o corpo é por conta de quem implementa, respeitando `02-padroes-de-engenharia/`.

---

## 1. Value Objects essenciais

```python
# domain/model/money.py
@dataclass(frozen=True, slots=True)
class Money:
    _cents: int

    @staticmethod
    def from_reais(amount: str | Decimal) -> "Money": ...   # "18.78" -> 1878 centavos
    @staticmethod
    def zero() -> "Money": ...
    def plus(self, other: "Money") -> "Money": ...
    def minus(self, other: "Money") -> "Money": ...
    def times(self, factor: int) -> "Money": ...
    def is_greater_than(self, other: "Money") -> bool: ...
    def ratio_to(self, total: "Money") -> "Percentage": ...
    def units_affordable_at(self, price: "UnitPrice") -> "Quantity": ...   # divisao inteira
    def value_for_serialization(self) -> str: ...                          # "987.44"
```

> `from_reais` aceita `str`/`Decimal`, **nunca `float`** — `float` reintroduz o erro de arredondamento. Entrada JSON numérica é convertida para `Decimal` na borda Pydantic.

```python
# domain/model/purchase_plan.py — first-class collection (cromossomo)
@dataclass(frozen=True, slots=True)
class PurchasePlan:
    _quantities: tuple[Quantity, ...]

    @staticmethod
    def of_units(units: Sequence[int]) -> "PurchasePlan": ...
    @staticmethod
    def empty_like(scenario: "ReplenishmentScenario") -> "PurchasePlan": ...
    def size(self) -> int: ...
    def quantity_at(self, position: Position) -> Quantity: ...
    def with_quantity_at(self, position: Position, quantity: Quantity) -> "PurchasePlan": ...
    def decremented_at(self, position: Position) -> "PurchasePlan": ...
    def clamped_to(self, ceilings: tuple[Quantity, ...]) -> "PurchasePlan": ...
    def non_empty_positions(self) -> tuple[Position, ...]: ...
    def total_units(self) -> Quantity: ...
    def units_for_serialization(self) -> tuple[int, ...]: ...
```

```python
# domain/model/replenishment_scenario.py — first-class collection
@dataclass(frozen=True, slots=True)
class ReplenishmentScenario:
    _items: tuple[ReplenishmentItem, ...]

    def size(self) -> int: ...
    def item_at(self, position: Position) -> ReplenishmentItem: ...
    def required_quantities(self) -> tuple[Quantity, ...]: ...
    def required_total(self) -> Quantity: ...
    def total_cost_of(self, plan: PurchasePlan) -> Money: ...
    def cost_at(self, position: Position, quantity: Quantity) -> Money: ...
    def most_expensive_position_among(self, positions: tuple[Position, ...]) -> MaybePosition: ...
    def positions_with_demand(self) -> tuple[Position, ...]: ...
```

```python
# domain/model/coverage_report.py
@dataclass(frozen=True, slots=True)
class CoverageReport:
    _served_ratio: Percentage
    _items_at_risk: int

    def served_ratio_points(self) -> float: ...
    def items_at_risk_count(self) -> int: ...
```

## 2. Portas (todas em `domain/ports/`)

| Porta | Assinatura |
|---|---|
| `FitnessPolicy` | `evaluate(plan: PurchasePlan, scenario: ReplenishmentScenario) -> PlanAssessment` |
| `PlanRepair` | `repair(plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan` |
| `SelectionStrategy` | `select(population: Population, policy: FitnessPolicy, scenario: ReplenishmentScenario) -> Population` |
| `CrossoverStrategy` | `combine(first: PurchasePlan, second: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan` |
| `MutationStrategy` | `mutate(plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan` |
| `DemandForecaster` | `forecast(snapshots: StockSnapshots) -> WeeklyDemandForecasts` |
| `RandomSource` | `ratio() -> float` · `integer_below(exclusive_limit: int) -> int` · `integer_inclusive(minimum: int, maximum: int) -> int` |
| `EvolutionObserver` | `on_generation(report: GenerationReport) -> None` |
| `StockHistoryRepository` | `load_history() -> StockSnapshots` |
| `TaskResultStore` | `save(task_id: TaskId, outcome: OptimizationOutcome) -> None` · `find(task_id: TaskId) -> MaybeOutcome` |
| `Clock` | `now() -> datetime` |

## 3. Motor evolutivo

```python
# domain/evolution/evolution_engine.py
@dataclass(frozen=True, slots=True)
class EvolutionEngine:
    _settings: EvolutionSettings
    _operators: EvolutionOperators

    def evolve(self, scenario: ReplenishmentScenario,
               observer: EvolutionObserver) -> EvolutionResult: ...
```

```python
# domain/evolution/evolution_settings.py
@dataclass(frozen=True, slots=True)
class EvolutionSettings:   # OC-8: Value Object de configuracao (excecao autorizada)
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
        """Valida elite_size <= parents_size <= population_size e population_size >= 2."""
```

```python
# domain/evolution/evolution_result.py
@dataclass(frozen=True, slots=True)
class EvolutionResult:
    _best_assessment: PlanAssessment
    _history: GenerationHistory

    def best_plan(self) -> PurchasePlan: ...
    def best_fitness(self) -> FitnessScore: ...
    def convergence_curve(self) -> tuple[GenerationReport, ...]: ...
```

## 4. Casos de uso (`application/use_cases/`)

```python
class BuildReplenishmentScenario:
    """Historico -> previsao -> necessidade liquida -> cenario. (RN-01..RN-03)"""
    def execute(self, cycle: ReplenishmentCycle) -> ReplenishmentScenario: ...

class OptimizeReplenishment:
    """Orquestra: monta cenario, roda AG, roda baseline, persiste resultado."""
    def execute(self, request: OptimizationRequest) -> OptimizationOutcome: ...

class CompareReplenishmentStrategies:
    """Avalia baseline e plano otimizado sobre o mesmo cenario."""
    def execute(self, scenario: ReplenishmentScenario,
                optimized: PurchasePlan) -> StrategyComparison: ...

class ClassifyStockRisk:
    """Aplica RN-06 a cada produto do historico."""
    def execute(self, snapshots: StockSnapshots) -> tuple[StockRiskAssessment, ...]: ...

class ReadOptimizationStatus:
    """Le o estado/resultado de uma tarefa pelo task_id."""
    def execute(self, task_id: TaskId) -> OptimizationStatusView: ...
```

Nenhum desses importa Celery, Redis, FastAPI ou sklearn.

## 5. Contrato HTTP

### 5.1 `POST /api/v1/optimize` → `202 Accepted`

Entrada (campos obrigatórios conforme contrato já publicado; opcionais são extensão retrocompatível — D-05):

```json
{
  "budget_limit": 1000.00,
  "dataset_reference": "historico_mensal_v1",
  "ga_parameters": {
    "population_size": 60,
    "generations": 100,
    "mutation_rate": 0.20,
    "parents_size": 20,
    "elite_size": 2,
    "random_seed": 42
  },
  "cycle_weeks": 4
}
```

Validação Pydantic: `budget_limit > 0`; `population_size` 10–500; `generations` 1–1000; `mutation_rate` 0.0–1.0; `cycle_weeks ≥ 1`; `elite_size ≤ parents_size ≤ population_size`. Violação → `422`.

Resposta:

```json
{ "task_id": "abc123xyz-890", "status": "PROCESSING",
  "message": "Algoritmo genético iniciado em background." }
```

### 5.2 `GET /api/v1/status/{task_id}`

```json
{ "task_id": "abc123xyz-890", "status": "PROCESSING", "result": null }
```

Concluído (campos de `best_scenario_summary` estendidos conforme D-01 — `projected_profit` **não** é emitido, pois o fitness não modela lucro):

```json
{
  "task_id": "abc123xyz-890",
  "status": "COMPLETED",
  "result": {
    "best_scenario_summary": {
      "total_cost": 987.44,
      "budget_limit": 1000.00,
      "budget_usage_ratio": 98.7,
      "served_quantity": 120,
      "required_total": 146,
      "served_ratio": 82.2,
      "items_at_risk": 1,
      "fitness": 816.92
    },
    "items_to_buy": [
      {"sku": "LEITE-UHT-1L", "product": "Leite UHT 1L", "quantity": 98,
       "unit_cost": 5.86, "required_quantity": 98, "uncovered_quantity": 0, "line_cost": 574.28},
      {"sku": "CAFE-500G", "product": "Café 500g", "quantity": 22,
       "unit_cost": 18.78, "required_quantity": 48, "uncovered_quantity": 26, "line_cost": 413.16}
    ],
    "baseline_comparison": {
      "baseline": {"total_cost": 314.32, "served_quantity": 36, "served_ratio": 24.7,
                   "items_at_risk": 2, "fitness": 236.58},
      "optimized": {"total_cost": 987.44, "served_quantity": 120, "served_ratio": 82.2,
                    "items_at_risk": 1, "fitness": 816.92}
    },
    "convergence_curve": [
      {"generation": 0, "max_fitness": 777.67},
      {"generation": 10, "max_fitness": 816.92}
    ],
    "model_metrics": {"mae": 4.76, "features": ["stock_on_hand", "weekly_outflow",
                      "monthly_outflow", "unit_price", "promotion_flag"]}
  }
}
```

Estados possíveis de `status`: `PROCESSING` · `COMPLETED` · `FAILED`. Em `FAILED`, incluir `"error": {"code": ..., "message": ...}` e **nunca** vazar stack trace.

`items_to_buy` contém **apenas** itens com `quantity > 0`, ordenados por `line_cost` decrescente. O plano completo (incluindo zeros) vai em `convergence`/relatório detalhado quando necessário.

### 5.3 `WS /ws/v1/progress/{task_id}`

Mensagem emitida pelo servidor, exatamente conforme o contrato:

```json
{ "generation": 15, "max_fitness": 12500.00, "status": "evolving" }
```

* `status`: `evolving` → `completed` (ou `failed`).
* Emitida a cada `progress_every` (10) gerações, **sempre** incluindo a primeira e a última.
* O servidor assina o canal Redis `progress:{task_id}` e repassa. Encerra a conexão após `completed`/`failed`.
* `task_id` inexistente → fecha com código `4404`.

## 6. Celery

```python
# infrastructure/tasks/optimization_task.py
@celery_app.task(name="optimization.run", queue="optimization_queue", bind=True)
def run_optimization(self, payload: dict) -> dict:
    """Adaptador: traduz payload, resolve o caso de uso no container e invoca."""
    request = OptimizationRequest.from_payload(payload)
    use_case = build_optimization_use_case(get_settings(), task_id=self.request.id)
    return OutcomeMapper().to_payload(use_case.execute(request))
```

Regras:

* Fila: `optimization_queue` (conforme a arquitetura).
* `task_id` do Celery **é** o `task_id` da API.
* A task não contém regra de negócio: traduz, delega, devolve.
* Exceção de domínio → resultado `FAILED` com código de erro mapeado; sem retry automático (resultado é determinístico, retry não ajuda).
* Timeout: `task_time_limit=300`, `task_soft_time_limit=270`.

## 7. Tratamento de erros

| Exceção de domínio | HTTP | Código |
|---|---|---|
| `InvalidBudgetError` | 422 | `INVALID_BUDGET` |
| `InvalidCycleError` | 422 | `INVALID_CYCLE` |
| `InvalidParametersError` | 422 | `INVALID_GA_PARAMETERS` |
| `NegativeQuantityError` | 500 | `INTERNAL_INVARIANT_VIOLATION` |
| `TaskNotFoundError` | 404 | `TASK_NOT_FOUND` |
| `ModelNotAvailableError` | 503 | `MODEL_UNAVAILABLE` |

Handlers centralizados em `api/errors/exception_handlers.py`. Formato: `{"error": {"code": "...", "message": "..."}}`, mensagem em português, sem stack trace.

## 8. Configuração (`core/config.py`)

| Variável | Padrão | Uso |
|---|---|---|
| `REDIS_URL` | `redis://redis_broker:6379/0` | Broker Celery |
| `REDIS_RESULT_URL` | `redis://redis_broker:6379/1` | Backend de resultados |
| `MODEL_STORE_PATH` | `/app/models/demand_forecaster.joblib` | Artefato do modelo |
| `DEFAULT_BUDGET_LIMIT` | `1000.00` | Padrão da PoC |
| `DEFAULT_CYCLE_WEEKS` | `4` | RN-01 |
| `DEFAULT_RANDOM_SEED` | `42` | Reprodutibilidade |
| `PROGRESS_EVERY_GENERATIONS` | `10` | Throttle de progresso |
| `CORS_ORIGINS` | `http://localhost:5173` | Frontend em dev |
| `LOG_LEVEL` | `INFO` | Logs |

Carregado com `pydantic-settings`; `Settings` é instanciado **uma vez** e injetado. Proibido `os.environ` espalhado pelo código.
