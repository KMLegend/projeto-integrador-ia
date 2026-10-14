---
id: 01-solid
dominio: padroes-de-engenharia
palavras-chave: SOLID, SRP, OCP, LSP, ISP, DIP, injecao de dependencia, protocol, inversao de dependencia, clean architecture
fonte-da-verdade: exigencia explicita do projeto
depende-de: [02-object-calisthenics, 03-modularidade-e-fronteiras]
---

# SOLID aplicado a este projeto

Exigência **não-negociável** nº 1. Cada princípio abaixo vem com a aplicação concreta neste domínio, o anti-padrão a evitar e como verificar.

---

## S — Single Responsibility Principle

> Uma classe tem **um** motivo para mudar.

O `avaliar()` do notebook faz quatro coisas: repara o plano, calcula custo, calcula cobertura e pontua. No sistema isso se decompõe:

| Classe | Único motivo para mudar |
|---|---|
| `BudgetAwarePlanRepair` | Mudou a regra de viabilidade |
| `CoverageCalculator` | Mudou o cálculo dos indicadores |
| `WeightedFitnessPolicy` | Mudou a forma de pontuar |
| `FitnessWeights` | Mudaram os pesos |
| `EvolutionEngine` | Mudou o laço evolutivo |
| `OptimizeReplenishment` (caso de uso) | Mudou a orquestração |
| `RedisProgressPublisher` | Mudou o transporte de progresso |

**Anti-padrões proibidos:** `OptimizationService` que carrega dataset + treina modelo + roda AG + serializa JSON; qualquer classe terminada em `Manager`, `Helper`, `Util`, `Processor`.

**Teste objetivo:** se a descrição da classe precisa de "e", ela tem responsabilidade a mais.

## O — Open/Closed Principle

> Aberta para extensão, fechada para modificação.

Cada eixo de variação do negócio é uma porta com múltiplas implementações. **Adicionar comportamento = adicionar classe**, nunca um `if` novo:

| Eixo de variação | Porta | Implementações previstas |
|---|---|---|
| Como pontuar um plano | `FitnessPolicy` | `WeightedFitnessPolicy`, `CostTieBreakingFitnessPolicy`, `ServiceLevelFitnessPolicy` |
| Como viabilizar um plano | `PlanRepair` | `BudgetAwarePlanRepair`, `BatchedBudgetPlanRepair` |
| Como prever demanda | `DemandForecaster` | `LinearRegressionDemandForecaster`, `CachedDemandForecaster`, `FixedDemandForecaster` |
| Como selecionar pais | `SelectionStrategy` | `TruncationSelection`, `TournamentSelection`, `RouletteSelection` |
| Como cruzar | `CrossoverStrategy` | `UniformCrossover`, `SinglePointCrossover` |
| Como mutar | `MutationStrategy` | `LocalShiftMutation`, `NeedAwareMutation` |
| Onde guardar resultado | `TaskResultStore` | `RedisTaskResultStore`, `InMemoryTaskResultStore` |
| Para onde emitir progresso | `EvolutionObserver` | `RedisProgressPublisher`, `ThrottledEvolutionObserver`, `NullEvolutionObserver` |
| De onde vem o histórico | `StockHistoryRepository` | `SimulatedStockHistoryRepository`, `CsvStockHistoryRepository` |

**Sinal de violação:** `if strategy_name == "tournament"` dentro do `EvolutionEngine`. A escolha de implementação acontece **uma única vez**, na composição (`core/container.py`).

**Teste objetivo:** adicionar `TournamentSelection` não deve alterar uma única linha de `EvolutionEngine`, `FitnessPolicy` ou dos casos de uso — prove com um teste que injeta a nova estratégia.

## L — Liskov Substitution Principle

> Qualquer implementação de uma porta pode substituir outra sem quebrar quem a usa.

Regras concretas:

* Toda `FitnessPolicy` devolve `PlanAssessment` — nenhuma devolve `None` nem lança exceção para plano válido.
* Toda `SelectionStrategy` devolve **ao menos 2** progenitores (senão o crossover é impossível).
* Todo `PlanRepair` devolve plano que satisfaz as invariantes 2–4 de `01-dominio-e-negocio/02-regras-de-negocio.md`.
* Todo `DemandForecaster` devolve previsão inteira `≥ 1` para **todo** produto do histórico recebido.
* Nenhuma implementação **fortalece** pré-condição nem **enfraquece** pós-condição.

**Como garantir:** um módulo de **testes de contrato** parametrizado roda a mesma bateria contra todas as implementações de cada porta (`tests/contracts/test_fitness_policy_contract.py`, etc.). Implementação nova sem passar no contrato não entra.

## I — Interface Segregation Principle

> Ninguém depende de método que não usa.

Portas pequenas e focadas. **Proibido** uma `IOptimizationService` com `train`, `forecast`, `optimize`, `save`, `publish`.

| Porta | Métodos |
|---|---|
| `FitnessPolicy` | `evaluate` |
| `PlanRepair` | `repair` |
| `DemandForecaster` | `forecast` |
| `RandomSource` | `ratio`, `integer_below`, `integer_inclusive` |
| `EvolutionObserver` | `on_generation` |
| `TaskResultStore` | `save`, `find` |
| `StockHistoryRepository` | `load_history` |
| `Clock` | `now` |

O `EvolutionEngine` não recebe um `TaskResultStore` — ele não persiste nada. Persistência é do caso de uso.

## D — Dependency Inversion Principle

> Política de alto nível não depende de detalhe; os dois dependem de abstração.

**A abstração é declarada por quem a consome** (o domínio), não por quem a implementa:

```
domain/ports/demand_forecaster.py          <- a interface vive no DOMINIO
infrastructure/forecasting/linear_regression_forecaster.py  <- o detalhe implementa
```

Regras duras:

1. **Nenhum** arquivo em `domain/` ou `application/` importa `sklearn`, `pandas`, `numpy`, `redis`, `celery`, `fastapi`, `pydantic` ou `joblib`.
2. Toda dependência entra por **construtor**. Proibido instanciar colaborador dentro do método, proibido singleton global, proibido import dentro de função para "resolver" ciclo.
3. A composição acontece num único lugar: `core/container.py`. Só ele conhece classes concretas.
4. Celery e FastAPI são **adaptadores de entrada**: a task Celery resolve o caso de uso no container e o invoca; ela não contém regra de negócio.

```python
# application/use_cases/optimize_replenishment.py
@dataclass(frozen=True, slots=True)
class OptimizeReplenishment:
    _scenario_builder: ScenarioBuilder      # porta
    _optimization: OptimizationRunner       # porta

    def execute(self, request: OptimizationRequest) -> OptimizationOutcome:
        scenario = self._scenario_builder.build_for(request.cycle())
        return self._optimization.run(scenario, request.settings())
```

Esse caso de uso roda em teste unitário **sem** Redis, sem Celery, sem sklearn e sem rede.

**Teste objetivo (automatizado no CI):**

```bash
grep -rnE "import (numpy|pandas|sklearn|redis|celery|fastapi|pydantic|joblib)" backend/src/domain backend/src/application
```

Deve retornar vazio. O `import-linter` cobre o caso geral — ver `03-modularidade-e-fronteiras.md`.

---

## Como isso aparece na revisão de código

Um pull request é recusado se:

- [ ] Uma classe tem mais de um motivo para mudar (SRP).
- [ ] Um comportamento novo foi adicionado com `if`/`elif` sobre tipo ou nome de estratégia (OCP).
- [ ] Uma implementação de porta não passa nos testes de contrato da porta (LSP).
- [ ] Uma porta tem método que algum consumidor não usa (ISP).
- [ ] `domain/` ou `application/` importa biblioteca de infraestrutura (DIP).
- [ ] Um colaborador é instanciado fora do `container.py` (DIP).
