---
id: 01-estrutura-de-diretorios
dominio: implementacao
palavras-chave: estrutura de pastas, arvore de diretorios, layout, organizacao, scaffold, monorepo
fonte-da-verdade: derivado de .context/00-arquitetura-tecnica/especifica_es_do_backend.md + 02-padroes-de-engenharia/03-modularidade-e-fronteiras.md
depende-de: [02-padroes-de-engenharia/03-modularidade-e-fronteiras]
---

# Estrutura de Diretórios (obrigatória)

Esta árvore é **normativa**. Não crie pastas fora dela sem registrar a decisão em `04-decisoes-e-roadmap/01-divergencias-e-decisoes.md`.

---

## 1. Raiz do repositório

```
projeto-integrador/
├── .context/                  # Esta base de conhecimento (RAG). NAO e codigo.
├── doc-projeto/               # Entregaveis academicos (notebooks, slides, roteiro)
├── Projeto_Preditivo.ipynb    # Fonte da verdade do negocio (nao editar na implantacao)
├── backend/
├── frontend/
├── docker-compose.yml
├── docker-compose.override.yml   # Desenvolvimento (hot reload)
├── .env.example
├── Makefile                   # Atalhos: up, down, test, lint, train
└── README.md
```

## 2. Backend

```
backend/
├── Dockerfile
├── pyproject.toml
├── requirements.txt           # Runtime compartilhado API + worker
├── requirements-dev.txt       # pytest, mypy, ruff, hypothesis, import-linter
├── .importlinter
└── src/
    ├── domain/                       # ZERO dependencia externa
    │   ├── model/
    │   │   ├── money.py                      # Money (centavos inteiros)
    │   │   ├── quantity.py                   # Quantity
    │   │   ├── unit_price.py                 # UnitPrice
    │   │   ├── sku.py                        # Sku
    │   │   ├── percentage.py                 # Percentage
    │   │   ├── fitness_score.py              # FitnessScore
    │   │   ├── fitness_weights.py            # FitnessWeights
    │   │   ├── budget_constraint.py           # BudgetConstraint
    │   │   ├── replenishment_cycle.py         # ReplenishmentCycle
    │   │   ├── catalog_item.py                # CatalogItem
    │   │   ├── replenishment_item.py          # ReplenishmentItem
    │   │   ├── replenishment_scenario.py      # ReplenishmentScenario (colecao)
    │   │   ├── purchase_plan.py               # PurchasePlan (cromossomo, colecao)
    │   │   ├── coverage_report.py             # CoverageReport
    │   │   ├── plan_assessment.py             # PlanAssessment
    │   │   ├── position.py                    # Position / MaybePosition
    │   │   └── stock_risk_level.py            # StockRiskLevel (Enum)
    │   ├── policy/
    │   │   ├── coverage_calculator.py
    │   │   ├── weighted_fitness_policy.py
    │   │   ├── budget_aware_plan_repair.py
    │   │   ├── naive_replenishment_policy.py
    │   │   ├── stock_risk_classifier.py
    │   │   └── stock_risk_rules.py
    │   ├── evolution/
    │   │   ├── evolution_engine.py
    │   │   ├── evolution_settings.py
    │   │   ├── evolution_operators.py
    │   │   ├── population.py
    │   │   ├── plan_factory.py
    │   │   ├── truncation_selection.py
    │   │   ├── uniform_crossover.py
    │   │   ├── local_shift_mutation.py
    │   │   ├── generation_report.py
    │   │   ├── generation_history.py
    │   │   ├── evolution_result.py
    │   │   └── null_evolution_observer.py
    │   ├── forecasting/
    │   │   ├── stock_snapshot.py
    │   │   ├── stock_snapshots.py
    │   │   ├── weekly_demand_forecast.py
    │   │   ├── weekly_demand_forecasts.py
    │   │   └── feature_schema.py
    │   ├── ports/
    │   │   ├── fitness_policy.py
    │   │   ├── plan_repair.py
    │   │   ├── demand_forecaster.py
    │   │   ├── random_source.py
    │   │   ├── evolution_observer.py
    │   │   ├── selection_strategy.py
    │   │   ├── crossover_strategy.py
    │   │   ├── mutation_strategy.py
    │   │   ├── stock_history_repository.py
    │   │   ├── task_result_store.py
    │   │   └── clock.py
    │   └── errors/
    │       └── domain_errors.py
    │
    ├── application/                  # Casos de uso; so importa domain
    │   ├── use_cases/
    │   │   ├── optimize_replenishment.py
    │   │   ├── build_replenishment_scenario.py
    │   │   ├── compare_replenishment_strategies.py
    │   │   ├── classify_stock_risk.py
    │   │   └── read_optimization_status.py
    │   ├── dto/
    │   │   ├── optimization_request.py
    │   │   └── optimization_outcome.py
    │   └── decorators/
    │       └── throttled_evolution_observer.py
    │
    ├── infrastructure/               # Adaptadores de saida
    │   ├── forecasting/
    │   │   ├── linear_regression_demand_forecaster.py
    │   │   ├── cached_demand_forecaster.py
    │   │   └── model_store.py                 # joblib: save/load + schema
    │   ├── dataset/
    │   │   ├── simulated_stock_history_repository.py
    │   │   ├── synthetic_dataset_generator.py
    │   │   └── product_catalog.py             # catalogo base (6 produtos)
    │   ├── randomness/
    │   │   └── seeded_random_source.py
    │   ├── messaging/
    │   │   ├── redis_progress_publisher.py
    │   │   └── redis_progress_subscriber.py
    │   ├── persistence/
    │   │   └── redis_task_result_store.py
    │   ├── time/
    │   │   └── system_clock.py
    │   └── tasks/
    │       └── optimization_task.py           # task Celery (adaptador, sem regra)
    │
    ├── api/                          # Adaptadores de entrada
    │   ├── routes/
    │   │   ├── optimization_routes.py         # POST /api/v1/optimize
    │   │   ├── status_routes.py               # GET  /api/v1/status/{task_id}
    │   │   └── health_routes.py               # GET  /health
    │   ├── websockets/
    │   │   └── progress_socket.py             # WS /ws/v1/progress/{task_id}
    │   ├── schemas/
    │   │   ├── requests.py
    │   │   └── responses.py
    │   ├── mappers/
    │   │   ├── scenario_mapper.py
    │   │   └── outcome_mapper.py
    │   └── errors/
    │       └── exception_handlers.py          # erro de dominio -> HTTP
    │
    ├── core/
    │   ├── config.py                          # Settings (pydantic-settings)
    │   ├── container.py                       # UNICO ponto de composicao
    │   └── celery_app.py
    │
    └── main.py                                # Monta o FastAPI
```

### Mapeamento para a estrutura sugerida na arquitetura

`00-arquitetura-tecnica/especifica_es_do_backend.md` sugeriu uma árvore mais simples. Esta é um refinamento compatível — ver decisão D-04. Correspondência:

| Sugestão original | Nesta estrutura |
|---|---|
| `/api/routes`, `/api/websockets` | `src/api/routes/`, `src/api/websockets/` |
| `/core/config.py`, `/core/celery_app.py` | `src/core/config.py`, `src/core/celery_app.py` (+ `container.py`) |
| `/schemas/requests.py`, `/schemas/responses.py` | `src/api/schemas/requests.py`, `responses.py` |
| `/ai_engine/genetic_algorithm` | `src/domain/evolution/` + `src/domain/policy/` |
| `/ai_engine/forecasting` | `src/domain/forecasting/` (conceitos) + `src/infrastructure/forecasting/` (sklearn) |
| `main.py` | `src/main.py` |

O `ai_engine` foi **dividido** porque regra de negócio pura e dependência de sklearn não podem morar na mesma camada sem violar a regra de dependência.

## 3. Frontend

```
frontend/
├── Dockerfile
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── features/
    │   ├── optimization/
    │   │   ├── components/OptimizationForm.tsx
    │   │   ├── hooks/useStartOptimization.ts
    │   │   ├── hooks/useOptimizationStatus.ts
    │   │   └── validation/optimizationFormSchema.ts
    │   ├── results/
    │   │   ├── components/KpiCards.tsx
    │   │   ├── components/PurchasePlanTable.tsx
    │   │   ├── components/StrategyComparisonTable.tsx
    │   │   └── components/BudgetDistributionChart.tsx
    │   └── convergence/
    │       ├── components/ConvergenceChart.tsx
    │       └── hooks/useProgressSocket.ts
    ├── shared/
    │   ├── api/
    │   │   ├── contracts.ts          # UNICO lugar com os tipos da API
    │   │   ├── httpClient.ts
    │   │   └── websocketClient.ts
    │   ├── ui/                       # Button, Card, Table, Spinner (burros)
    │   └── formatting/
    │       ├── currency.ts           # pt-BR, R$
    │       ├── percentage.ts
    │       └── units.ts
    └── test/
        └── setup.ts
```

## 4. Convenções de arquivo

| Item | Convenção |
|---|---|
| Módulo Python | `snake_case.py`, **uma classe pública por arquivo**, nome do arquivo = nome da classe |
| Componente React | `PascalCase.tsx`, um componente por arquivo |
| Hook React | `useAlgumaCoisa.ts` |
| Teste Python | `test_<modulo>.py`, espelhando a árvore de `src/` |
| Teste frontend | `<Componente>.test.tsx` ao lado do componente |
| Arquivo acima de 200 linhas | Violação da regra 7 de Object Calisthenics — divida |

## 5. O que **não** criar

* `utils/`, `helpers/`, `common/`, `misc/`, `shared/` no backend — nomes vazios que acumulam lixo (regra 6). Todo código pertence a um conceito nomeável.
* `models.py` gigante com tudo dentro.
* `services/` como camada genérica — use `application/use_cases/`.
* Pasta de código na raiz do repositório fora de `backend/` e `frontend/`.
* Qualquer arquivo de código dentro de `.context/` — ela é só documentação.
