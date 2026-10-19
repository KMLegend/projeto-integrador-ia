---
id: 02-roadmap-de-implantacao
dominio: decisoes
palavras-chave: roadmap, fases, tarefas, backlog, ordem de implementacao, criterios de aceite, definition of done, planejamento
fonte-da-verdade: derivado de toda a base de contexto
depende-de: [todos]
---

# Roadmap de Implantação

Sequência de execução para agentes. Cada tarefa é **atômica**, tem critério de aceite objetivo e lista os documentos a ler antes de começar. Fases são sequenciais; tarefas dentro de uma fase podem ser paralelizadas quando não houver dependência declarada.

Legenda de dependência: `T-xx` = tarefa anterior necessária.

> **Para executar, use `03-tasks-de-implementacao.md`.** Este documento dá a visão de fases e portões; lá cada `T-nn` virou uma `TASK n` autocontida (o que fazer, o que ler, o que entregar, o que **não** fazer). Mesma numeração, mesmo escopo — mantenha os dois em sincronia ao alterar escopo de tarefa.

---

## Fase 0 — Fundação (sem regra de negócio)

| # | Tarefa | Ler antes | Aceite |
|---|---|---|---|
| T-01 | Criar a árvore de diretórios de `backend/` e `frontend/` (com `__init__.py` vazios) | `03-implementacao/01-estrutura-de-diretorios.md` | Árvore idêntica à especificada; nada fora dela |
| T-02 | `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `.importlinter`, config do `ruff`/`mypy` | `02-padroes-de-engenharia/03-modularidade-e-fronteiras.md`, `04-estrategia-de-testes.md` | `ruff check`, `mypy --strict` e `lint-imports` rodam (ainda sem código) |
| T-03 | `backend/Dockerfile`, `frontend/Dockerfile`, `nginx.conf`, `docker-compose.yml`, `override`, `.env.example`, `Makefile` | `03-implementacao/04-docker-e-infraestrutura.md` | `docker compose build` conclui; `redis_broker` fica *healthy* |
| T-04 | `GET /health` + `main.py` mínimo do FastAPI | `03-implementacao/02-contratos-de-codigo-backend.md` | `curl localhost:8000/health` → `200`; `api_backend` *healthy* |

**Portão da fase 0:** `docker compose up` sobe Redis + API com healthcheck verde.

## Fase 1 — Domínio: Value Objects

| # | Tarefa | Ler antes | Aceite |
|---|---|---|---|
| T-05 | `Money`, `Quantity`, `UnitPrice`, `Sku`, `Percentage`, `FitnessScore`, `Position`/`MaybePosition` | `02-object-calisthenics.md`, `03-implementacao/02-contratos-de-codigo-backend.md` | Imutáveis, validados no `__post_init__`, sem `@property`/getter; `Money` só constrói de `str`/`Decimal` |
| T-06 | `BudgetConstraint`, `ReplenishmentCycle`, `FitnessWeights`, `StockRiskLevel`, `StockRiskThresholds` | `01-dominio-e-negocio/02-regras-de-negocio.md` | `FitnessWeights.default()` = (10, 5); invariantes de RN-01/RN-05 testadas |
| T-07 | `CatalogItem`, `ReplenishmentItem`, `ReplenishmentScenario`, `PurchasePlan`, `CoverageReport`, `PlanAssessment` | `02-contratos-de-codigo-backend.md` seção 1 | Coleções de primeira classe; ≤ 2 atributos por classe; nenhuma expõe `tuple` crua |

**Portão da fase 1:** testes de domínio passam sem numpy instalado; greps de Object Calisthenics sem violação.

## Fase 2 — Domínio: regras de decisão

| # | Tarefa | Ler antes | Aceite |
|---|---|---|---|
| T-08 | `CoverageCalculator` (RN-07) | `01-dominio-e-negocio/04-funcao-fitness.md` | `served_ratio` = 100 quando `required_total` = 0; os 6 casos de borda cobertos |
| T-09 | `BudgetAwarePlanRepair` (dep. T-07) | `04-funcao-fitness.md` seção 3 | Idempotente; nunca devolve plano inviável; para sem laço infinito quando nada é comprável |
| T-10 | `WeightedFitnessPolicy` (dep. T-08) | `04-funcao-fitness.md` | **Reproduz 236,5753 e 816,9178** no cenário de referência; função pura |
| T-11 | `StockRiskClassifier` + regras (RN-06) | `02-regras-de-negocio.md`, `02-object-calisthenics.md` | Três níveis testados; **zero `else`**; limiar 1,8 injetado |
| T-12 | `NaiveReplenishmentPolicy` (baseline) | `01-dominio-e-negocio/06-baseline-e-indicadores.md` | Produz `[0, 8, 0, 0, 28, 0]`, custo R$ 314,32, fitness 236,58 |

**Portão da fase 2:** os valores-ouro de baseline e fitness passam. A regra de negócio está pronta e provada **sem** AG, sem ML, sem Docker.

## Fase 3 — Domínio: motor evolutivo

| # | Tarefa | Ler antes | Aceite |
|---|---|---|---|
| T-13 | Porta `RandomSource` + `SeededRandomSource` + `ScriptedRandomSource` (teste) | `01-dominio-e-negocio/05-algoritmo-genetico.md` seção 8 | Mesma semente ⇒ mesma sequência; nenhum uso de `random` global acima de `infrastructure` |
| T-14 | `PlanFactory`, `TruncationSelection`, `UniformCrossover`, `LocalShiftMutation` (dep. T-09, T-13) | `05-algoritmo-genetico.md` seção 4 | Cada operador testado com `ScriptedRandomSource` de forma exata; todos reparam a saída |
| T-15 | `Population`, `GenerationReport`, `GenerationHistory`, `EvolutionResult`, `EvolutionSettings` | `05-algoritmo-genetico.md` seções 3 e 7 | `EvolutionSettings` valida `elite_size ≤ parents_size ≤ population_size` |
| T-16 | `EvolutionEngine` + `NullEvolutionObserver` (dep. T-14, T-15) | `05-algoritmo-genetico.md` seção 5 | **Fitness 816,92 e plano `[0,22,0,0,98,0]` com semente 42**; `history` não-decrescente; igual ao guloso ótimo |
| T-17 | Testes de contrato das portas de domínio | `02-padroes-de-engenharia/04-estrategia-de-testes.md` | Bateria parametrizada cobrindo todas as implementações de `FitnessPolicy`, `PlanRepair` e os 3 operadores |

**Portão da fase 3:** o AG reproduz o resultado do notebook, de forma determinística, sem Redis/Celery/sklearn. Cobertura de `domain/` ≥ 95%.

## Fase 4 — Previsão de demanda e casos de uso

| # | Tarefa | Ler antes | Aceite |
|---|---|---|---|
| T-18 | `StockSnapshot(s)`, `WeeklyDemandForecast(s)`, `FeatureSchema`, porta `DemandForecaster` | `01-dominio-e-negocio/03-previsao-de-demanda.md` | Ordem das 5 features definida em **um** lugar |
| T-19 | `SyntheticDatasetGenerator` + `SimulatedStockHistoryRepository` | `03-previsao-de-demanda.md` seção 4 | 120 registros; ordem dos sorteios conforme especificado; reprodutível com semente 42 |
| T-20 | `LinearRegressionDemandForecaster` + `ModelStore` (joblib) + `CachedDemandForecaster` (dep. T-18) | `03-previsao-de-demanda.md` seções 3, 6, 7 | **MAE ≤ 6,0**; previsões inteiras ≥ 1; artefato guarda features/semente/MAE/schema |
| T-21 | `FixedDemandForecaster` (dublê) | `04-estrategia-de-testes.md` | Todos os testes de caso de uso rodam sem sklearn |
| T-22 | `BuildReplenishmentScenario` (RN-01..RN-03) (dep. T-18, T-21) | `02-regras-de-negocio.md`, `03-previsao-de-demanda.md` seção 5 | Com previsões fixas, reproduz as necessidades 48 (Café) e 98 (Leite); itens ordenados por produto |
| T-23 | `OptimizeReplenishment`, `CompareReplenishmentStrategies`, `ClassifyStockRisk` (dep. T-16, T-22) | `03-implementacao/02-contratos-de-codigo-backend.md` seção 4 | Roda sem Redis/Celery/rede; devolve comparativo baseline × AG |

**Portão da fase 4:** fluxo completo histórico → previsão → cenário → plano ótimo + comparativo, em teste unitário, sem infraestrutura.

## Fase 5 — Infraestrutura, API e tempo real

| # | Tarefa | Ler antes | Aceite |
|---|---|---|---|
| T-24 | `core/config.py` (Settings) e `core/container.py` (composição) | `02-padroes-de-engenharia/01-solid.md`, `03-modularidade-e-fronteiras.md` | Único lugar que instancia classes concretas; nenhum `os.environ` espalhado |
| T-25 | `RedisTaskResultStore`, `RedisProgressPublisher`, `RedisProgressSubscriber`, `ThrottledEvolutionObserver` | `05-algoritmo-genetico.md` seção 6 | Falha de publicação não derruba a otimização; emite a 1ª e a última geração |
| T-26 | `core/celery_app.py` + `optimization_task.py` (dep. T-23, T-24) | `02-contratos-de-codigo-backend.md` seção 6 | Fila `optimization_queue`; `task_id` do Celery = da API; zero regra na task |
| T-27 | Schemas Pydantic + `POST /api/v1/optimize` + `GET /api/v1/status/{task_id}` + mappers | `02-contratos-de-codigo-backend.md` seção 5 | `202` com `task_id`; validações → `422`; payload exatamente como especificado |
| T-28 | `WS /ws/v1/progress/{task_id}` (dep. T-25) | `02-contratos-de-codigo-backend.md` seção 5.3, decisão D-06 | Mensagens `{generation, max_fitness, status}`; fecha após `completed`; `4404` se tarefa não existe |
| T-29 | Handlers de exceção de domínio → HTTP | `02-contratos-de-codigo-backend.md` seção 7 | Tabela de códigos implementada; sem stack trace na resposta |
| T-30 | Testes de integração (sklearn real, Redis real) e e2e via compose | `04-estrategia-de-testes.md` seções 1 e 8 | Os 10 critérios de containerização passam |

**Portão da fase 5:** `docker compose up` + `POST /optimize` → `COMPLETED` com o plano de referência, e progresso chegando por WebSocket.

## Fase 6 — Frontend

| # | Tarefa | Ler antes | Aceite |
|---|---|---|---|
| T-31 | Scaffold Vite + TS + Tailwind + TanStack Query; `contracts.ts` | `03-implementacao/03-contratos-de-codigo-frontend.md` | `tsc --noEmit` limpo; tipos da API em um só arquivo |
| T-32 | `httpClient` e `websocketClient` atrás de interface | idem seção 2 | Nenhum componente importa `fetch` direto |
| T-33 | `OptimizationForm` + `useStartOptimization` | idem seções 3 e 4 | Padrões R$ 1.000 / 60 / 100 / 0,20; validação com mensagens em português |
| T-34 | `useOptimizationStatus` (polling) + `useProgressSocket` | idem seção 3 | Polling para quando conclui; socket indisponível não bloqueia a tela |
| T-35 | `KpiCards`, `PurchasePlanTable`, `StrategyComparisonTable` | idem seções 4 e 6 | Exibe R$ 987,44 · 98,7% · 82,2% · 1 em risco · 816,92, formatado em pt-BR |
| T-36 | `ConvergenceChart` e `BudgetDistributionChart` (Plotly) | idem seção 5 | Curva avança ao vivo; eixo Y escalado pelos dados (não 0–12500, ver D-09) |
| T-37 | Estados de UI (7 estados) e acessibilidade | idem seções 8 e 9 | Todos os estados renderizam; labels, `caption`/`scope`, layout ≥ 360 px |

**Portão da fase 6:** demonstração ponta a ponta no navegador, com os números do notebook na tela.

## Fase 7 — Fechamento

| # | Tarefa | Ler antes | Aceite |
|---|---|---|---|
| T-38 | `README.md` do repositório (como subir, como testar, arquitetura em 1 diagrama) | `INDEX.md` | Alguém sem contexto sobe o sistema seguindo só o README |
| T-39 | CI com todos os portões de `04-estrategia-de-testes.md` seção 6 | idem | Build vermelho se qualquer portão falhar |
| T-40 | Fixar versões (`==`) em `requirements.txt` e `package.json` | `04-docker-e-infraestrutura.md` seção 6 | Build reprodutível na máquina da apresentação |
| T-41 | Revisão final contra as 4 exigências (SOLID, Object Calisthenics, Docker, Modularidade) | `INDEX.md` seção 3 | Checklist de cada documento de padrões percorrido e assinado |

---

## Definition of Done (vale para toda tarefa)

Uma tarefa só está concluída quando:

1. O código cumpre SOLID e Object Calisthenics, com exceções justificadas e comentadas.
2. Tem teste automatizado no nível correto da pirâmide.
3. `ruff check`, `mypy --strict` e `lint-imports` passam.
4. Nenhum número de negócio novo foi inventado — todos vêm de `01-dominio-e-negocio/`.
5. Se tocou em valor-ouro, o teste de regressão correspondente continua verde.
6. Se encontrou divergência, registrou `D-nn` em `01-divergencias-e-decisoes.md`.
7. Roda dentro do container, não só na máquina de quem escreveu.

## Caminho mínimo para demonstração

Se o prazo apertar, a ordem de corte é: **Fases 0→4** entregam o valor acadêmico central (regra de negócio, fitness e AG reproduzindo o notebook, com SOLID/Object Calisthenics/modularidade provados por teste). Fase 5 entrega a containerização exigida. Fase 6 é a camada de demonstração visual — reduza o escopo dos gráficos antes de reduzir testes de domínio.

## Evoluções fora do escopo atual

Registradas aqui para não vazarem para a implementação: preço de venda separado do custo de compra (D-10), fitness com margem (D-01), lead time de fornecedor, validade/shelf-life, desconto por volume, restrição de espaço de armazenagem, Prophet ou modelos de ensemble (D-11), validação cruzada, autenticação e multiusuário. *(Ingestão de datasets pelo usuário saiu desta lista — implementada, ver D-18.)*
