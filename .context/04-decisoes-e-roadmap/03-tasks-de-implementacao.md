---
id: 03-tasks-de-implementacao
dominio: decisoes
palavras-chave: tasks, tarefas, sequencia de implementacao, ordem de serviço, backlog executavel, task 1, task 2, prompt de agente, checklist
fonte-da-verdade: este documento (derivado de 02-roadmap-de-implantacao.md)
depende-de: [02-roadmap-de-implantacao, 01-divergencias-e-decisoes]
---

# TASKS de Implementação (sequência executável)

Cada TASK abaixo é uma **ordem de serviço autocontida**: um agente pega **uma** task, lê só os documentos listados em *Ler antes*, entrega os arquivos de *Entregar* e para. Não avance para a próxima task no mesmo trabalho.

* **Numeração:** `TASK n` ↔ `T-nn` de `02-roadmap-de-implantacao.md` (mesma ordem, mesmo escopo). Esse arquivo dá a visão de fases; este dá a ordem de execução.
* **Ordem:** sequencial por padrão. Tasks com *Depende de* satisfeito e marcadas `∥` podem rodar em paralelo por agentes diferentes.
* **Definition of Done:** além do *Aceite* de cada task, valem os 7 itens da seção final de `02-roadmap-de-implantacao.md`.
* **Regra de ouro:** se faltar um número, fórmula ou limiar, **pare e pergunte**. Não invente regra de negócio — ela está em `01-dominio-e-negocio/`.

---

## FASE 0 — Fundação

### TASK 1 — Árvore de diretórios do repositório
- **Depende de:** — · **Camada:** repositório
- **Ler antes:** `03-implementacao/01-estrutura-de-diretorios.md`
- **Fazer:** criar a árvore completa de `backend/src/` (domain, application, infrastructure, api, core) e `frontend/src/` (features, shared), com `__init__.py` vazios em cada pacote Python e `.gitkeep` nas pastas ainda sem arquivo.
- **Entregar:** a árvore exatamente como especificada, mais `backend/tests/` com `unit/`, `contracts/`, `properties/`, `integration/`, `e2e/`, `fixtures/`, `doubles/`.
- **Aceite:** `find backend/src -type d` reproduz a árvore do documento; nenhuma pasta extra; nenhuma das pastas proibidas (`utils/`, `helpers/`, `common/`, `services/`).
- **Não fazer:** nenhum código de lógica; nenhum arquivo dentro de `.context/`.

### TASK 2 — Toolchain e portões de qualidade `∥`
- **Depende de:** TASK 1 · **Camada:** repositório
- **Ler antes:** `02-padroes-de-engenharia/03-modularidade-e-fronteiras.md` (seção 2), `02-padroes-de-engenharia/04-estrategia-de-testes.md` (seção 6)
- **Fazer:** `backend/pyproject.toml` (config de `ruff` com `C901`, `PLR0912`, `PLR0913`; `mypy --strict`; `pytest` com `--cov`), `requirements.txt`, `requirements-dev.txt` e `.importlinter` com os 3 contratos (camadas, domínio puro, api não toca infra).
- **Entregar:** os 5 arquivos de configuração + script `backend/scripts/check_calisthenics.sh` com os greps da seção 10 de `02-object-calisthenics.md`.
- **Aceite:** `ruff check src`, `mypy --strict src`, `lint-imports` e `check_calisthenics.sh` executam e passam (ainda sem código de negócio).
- **Não fazer:** não inclua `deap`, `pygad` nem `prophet` (decisões D-02 e D-11).

### TASK 3 — Containerização completa `∥`
- **Depende de:** TASK 1 · **Camada:** infraestrutura
- **Ler antes:** `03-implementacao/04-docker-e-infraestrutura.md` (documento inteiro)
- **Fazer:** `backend/Dockerfile` (multi-stage base/development/runtime, usuário não-root, `PYTHONPATH=/app/src`), `frontend/Dockerfile` (development/build/runtime-nginx), `frontend/nginx.conf` (fallback SPA + proxy `/api/` e `/ws/` com headers de upgrade), `docker-compose.yml`, `docker-compose.override.yml`, `.env.example`, `Makefile`.
- **Entregar:** os 7 arquivos; os 4 serviços (`frontend`, `api_backend`, `celery_worker`, `redis_broker`) + `model_trainer` no profile `tools`; rede `ai_inventory_network`; volume `model_store`.
- **Aceite:** `docker compose build` conclui; `docker compose up -d redis_broker` fica *healthy*; `docker compose config` sem aviso.
- **Não fazer:** não suba a API ainda (ela não existe até a TASK 4).

### TASK 4 — `main.py` mínimo e `GET /health`
- **Depende de:** TASK 2, TASK 3 · **Camada:** api
- **Ler antes:** `03-implementacao/02-contratos-de-codigo-backend.md` (seção 8), `01-estrutura-de-diretorios.md`
- **Fazer:** `src/main.py` montando o FastAPI, `src/api/routes/health_routes.py`, `src/core/config.py` com `Settings` (pydantic-settings) cobrindo as 9 variáveis da tabela.
- **Entregar:** os 3 arquivos + teste `tests/integration/test_health.py`.
- **Aceite:** `docker compose up -d` deixa `api_backend` *healthy*; `curl localhost:8000/health` → `200`; nenhum `os.environ` fora de `config.py`.
- **Não fazer:** nenhuma rota de otimização; nenhum import de `infrastructure/`.

> **PORTÃO DA FASE 0:** Redis + API no ar, com healthcheck verde e portões de lint executáveis.

---

## FASE 1 — Domínio: Value Objects (zero dependência externa)

### TASK 5 — Value Objects base
- **Depende de:** TASK 2 · **Camada:** `domain/model/`
- **Ler antes:** `02-padroes-de-engenharia/02-object-calisthenics.md` (regras 3, 7, 8, 9), `03-implementacao/02-contratos-de-codigo-backend.md` (seção 1), decisão **D-03**
- **Fazer:** `money.py`, `quantity.py`, `unit_price.py`, `sku.py`, `percentage.py`, `fitness_score.py`, `position.py` (com `Position` e `MaybePosition`).
- **Entregar:** 7 módulos + testes unitários em `tests/unit/domain/model/`.
- **Aceite:** todos `@dataclass(frozen=True, slots=True)` com validação em `__post_init__`; **`Money` armazena centavos inteiros e só constrói de `str`/`Decimal`** (construir de `float` levanta erro); zero `@property`/`get_`/`set_`; `Money.from_reais("18.78").times(22)` == `Money.from_reais("413.16")`.
- **Não fazer:** nenhuma regra de fitness, reparo ou cenário.

### TASK 6 — Value Objects de política `∥`
- **Depende de:** TASK 5 · **Camada:** `domain/model/`
- **Ler antes:** `01-dominio-e-negocio/02-regras-de-negocio.md` (RN-01, RN-05, RN-06), `04-funcao-fitness.md` (seção 5)
- **Fazer:** `budget_constraint.py`, `replenishment_cycle.py`, `fitness_weights.py`, `stock_risk_level.py` (Enum `SHORTAGE`/`ADEQUATE`/`EXCESS`), `stock_risk_thresholds.py`, `domain/errors/domain_errors.py`.
- **Entregar:** 6 módulos + testes.
- **Aceite:** `FitnessWeights.default()` == `(coverage=10.0, risk_penalty=5.0)`; `cycle_weeks < 1` → `InvalidCycleError`; `budget_limit <= 0` → `InvalidBudgetError`; limiar `1.8` só existe dentro de `StockRiskThresholds`.
- **Não fazer:** não implemente o classificador de risco (TASK 11).

### TASK 7 — Entidades e coleções de primeira classe
- **Depende de:** TASK 5, TASK 6 · **Camada:** `domain/model/`
- **Ler antes:** `03-implementacao/02-contratos-de-codigo-backend.md` (seção 1), `02-object-calisthenics.md` (regras 4, 5, 8), `01-dominio-e-negocio/06-baseline-e-indicadores.md` (seção 2)
- **Fazer:** `catalog_item.py`, `replenishment_item.py`, `replenishment_scenario.py`, `purchase_plan.py`, `coverage_report.py`, `plan_assessment.py`. Criar também a fixture canônica `tests/fixtures/reference_scenario.json` (conteúdo normativo na seção 2 de `06-baseline-e-indicadores.md`) e o loader `tests/conftest.py` que a expõe como fixture `reference_scenario`.
- **Entregar:** 6 módulos + fixture JSON + `conftest.py` + testes.
- **Aceite:** `ReplenishmentItem` tem **2** atributos (`_catalog_item`, `_required_quantity`); nenhuma coleção expõe `tuple`/`list` crua; `PurchasePlan` é imutável (toda operação devolve nova instância); fixture carregada produz cenário com `required_total() == 146` e custo total de necessidade `R$ 1.475,72`.
- **Não fazer:** não calcule fitness nem cobertura aqui.

> **PORTÃO DA FASE 1:** testes de domínio verdes **sem numpy instalado**; `check_calisthenics.sh` sem violação.

---

## FASE 2 — Domínio: regras de decisão

### TASK 8 — `CoverageCalculator` (RN-07)
- **Depende de:** TASK 7 · **Camada:** `domain/policy/`
- **Ler antes:** `01-dominio-e-negocio/04-funcao-fitness.md` (seções 2 e casos de borda), `02-regras-de-negocio.md` (RN-07)
- **Fazer:** `coverage_calculator.py` produzindo `CoverageReport` (`served_ratio`, `items_at_risk`).
- **Entregar:** 1 módulo + testes dos **6 casos de borda** da tabela da seção 2 de `04-funcao-fitness.md`.
- **Aceite:** `required_total == 0` ⇒ `served_ratio = 100` e `items_at_risk = 0`; item com necessidade 0 nunca conta como em risco; cenário vazio não divide por zero; `0 ≤ served_ratio ≤ 100` sempre.
- **Não fazer:** não aplique pesos (é da TASK 10).

### TASK 9 — `BudgetAwarePlanRepair` (RN-04, RN-05)
- **Depende de:** TASK 7 · **Camada:** `domain/policy/`
- **Ler antes:** `01-dominio-e-negocio/04-funcao-fitness.md` (seção 3 — algoritmo normativo), `02-object-calisthenics.md` (regras 1 e 2)
- **Fazer:** `budget_aware_plan_repair.py` implementando a porta `PlanRepair`: CLAMP → remover unidade do item de **maior preço unitário** (empate: menor índice) até caber no orçamento.
- **Entregar:** porta `domain/ports/plan_repair.py` + implementação + testes.
- **Aceite:** idempotente (`repair(repair(p)) == repair(p)`); nunca devolve plano inviável; orçamento menor que a unidade mais barata ⇒ plano zero **sem laço infinito**; teste de propriedade com 1.000 planos aleatórios mantendo as invariantes 2–4 de `02-regras-de-negocio.md`; **zero `else`**; métodos ≤ 5 linhas.
- **Não fazer:** não otimize em lote agora (`BatchedBudgetPlanRepair` é extensão futura).

### TASK 10 — `WeightedFitnessPolicy` (função fitness)
- **Depende de:** TASK 8, TASK 9 · **Camada:** `domain/policy/`
- **Ler antes:** `01-dominio-e-negocio/04-funcao-fitness.md` (inteiro), `06-baseline-e-indicadores.md` (seção 3)
- **Fazer:** porta `domain/ports/fitness_policy.py` + `weighted_fitness_policy.py`: `fitness = served_ratio × 10 − items_at_risk × 5`.
- **Entregar:** porta + implementação + **testes de valor-ouro**.
- **Aceite:** no cenário de referência, plano `[0,8,0,0,28,0]` ⇒ fitness **236,5753** (`abs=1e-4`) e custo **R$ 314,32** exato; plano `[0,22,0,0,98,0]` ⇒ fitness **816,9178** e custo **R$ 987,44**; cenário sem necessidade ⇒ **1000**; plano vazio com 2 itens em necessidade ⇒ **−10**; função pura (1.000 chamadas, mesmo resultado); pesos 10/5 não aparecem hardcoded fora de `FitnessWeights.default()`.
- **Não fazer:** não implemente políticas alternativas de fitness (seção 6 de `04-funcao-fitness.md` é extensão futura).

### TASK 11 — `StockRiskClassifier` (RN-06) `∥`
- **Depende de:** TASK 6 · **Camada:** `domain/policy/`
- **Ler antes:** `01-dominio-e-negocio/02-regras-de-negocio.md` (RN-06), `02-object-calisthenics.md` (regra 2 — exemplo canônico)
- **Fazer:** `stock_risk_classifier.py` + `stock_risk_rules.py` (`ShortageRule`, `ExcessRule`) com lista ordenada de regras e `next(..., ADEQUATE)`.
- **Entregar:** 2 módulos + testes dos três níveis, incluindo as fronteiras exatas (`stock == forecast` ⇒ `ADEQUATE`; `stock == 1.8 × forecast` ⇒ `ADEQUATE`).
- **Aceite:** precedência falta → excesso → adequado preservada; **zero `else`**; adicionar um 4º nível de risco não exige alterar o classificador.
- **Não fazer:** não leia histórico nem chame previsão (é da TASK 23).

### TASK 12 — `NaiveReplenishmentPolicy` (baseline)
- **Depende de:** TASK 9 · **Camada:** `domain/policy/`
- **Ler antes:** `01-dominio-e-negocio/06-baseline-e-indicadores.md` (seções 1 e 3.1)
- **Fazer:** `naive_replenishment_policy.py`: `share = budget_cents // n_itens`, `quantity(i) = share // unit_price_cents(i)`, depois `repair`.
- **Entregar:** 1 módulo + teste de valor-ouro.
- **Aceite:** no cenário de referência produz **exatamente** `[0, 8, 0, 0, 28, 0]`, custo **R$ 314,32**, 36 unidades, 2 itens em risco, fitness **236,58**.
- **Não fazer:** não use `float` na divisão (decisão D-03).

> **PORTÃO DA FASE 2:** a regra de negócio está provada por teste **sem AG, sem ML e sem Docker**.

---

## FASE 3 — Domínio: motor evolutivo

### TASK 13 — `RandomSource` determinístico
- **Depende de:** TASK 2 · **Camada:** `domain/ports/` + `infrastructure/randomness/` + `tests/doubles/`
- **Ler antes:** `01-dominio-e-negocio/05-algoritmo-genetico.md` (seção 8), `02-regras-de-negocio.md` (RN-08)
- **Fazer:** porta `random_source.py` (`ratio`, `integer_below`, `integer_inclusive`), `seeded_random_source.py` (sobre `random.Random`, stdlib) e `scripted_random_source.py` (dublê que devolve sequência pré-definida).
- **Entregar:** 3 módulos + testes.
- **Aceite:** mesma semente ⇒ mesma sequência em 10 execuções; `ScriptedRandomSource` esgotado levanta erro explícito; `grep -rn "import random\|np.random" src/domain src/application` só encontra a porta.
- **Não fazer:** não use `numpy.random` (o AG não precisa de numpy).

### TASK 14 — Operadores genéticos
- **Depende de:** TASK 9, TASK 13 · **Camada:** `domain/evolution/`
- **Ler antes:** `01-dominio-e-negocio/05-algoritmo-genetico.md` (seção 4 — algoritmos normativos)
- **Fazer:** portas `selection_strategy.py`, `crossover_strategy.py`, `mutation_strategy.py` + `plan_factory.py`, `truncation_selection.py`, `uniform_crossover.py`, `local_shift_mutation.py`.
- **Entregar:** 3 portas + 4 implementações + testes exatos com `ScriptedRandomSource`.
- **Aceite:** `PlanFactory` sorteia em `[0, required]` e repara; crossover é **uniforme por gene** com corte em `0.5`; mutação é **por indivíduo** (`ratio() < 0.20`), sorteia 1 posição e aplica variação em `[-10, +10]` com piso 0; **todos** os operadores reparam a saída; nenhum teste depende de tolerância estatística.
- **Não fazer:** **não** "corrija" a mutação para sortear só posições com necessidade > 0 — a ineficiência é fiel ao notebook e documentada; `NeedAwareMutation` é opt-in futuro.

### TASK 15 — Agregados do ciclo evolutivo `∥`
- **Depende de:** TASK 7 · **Camada:** `domain/evolution/`
- **Ler antes:** `01-dominio-e-negocio/05-algoritmo-genetico.md` (seções 3 e 7), `03-implementacao/02-contratos-de-codigo-backend.md` (seção 3)
- **Fazer:** `population.py`, `generation_report.py`, `generation_history.py`, `evolution_result.py`, `evolution_settings.py`.
- **Entregar:** 5 módulos + testes.
- **Aceite:** `EvolutionSettings.notebook_defaults()` == `(60, 100, 0.20, 20, 2, 10, 42)`; valida `elite_size ≤ parents_size ≤ population_size` e `population_size ≥ 2` → `InvalidParametersError`; `EvolutionSettings` carrega o comentário `# OC-8: <justificativa>`; `Population` é coleção de primeira classe.
- **Não fazer:** não implemente o laço (TASK 16).

### TASK 16 — `EvolutionEngine` (laço evolutivo)
- **Depende de:** TASK 10, TASK 14, TASK 15 · **Camada:** `domain/evolution/`
- **Ler antes:** `01-dominio-e-negocio/05-algoritmo-genetico.md` (seção 5 — ordem normativa), `06-baseline-e-indicadores.md` (seções 3.2 e 3.3)
- **Fazer:** `evolution_engine.py`, `evolution_operators.py`, `null_evolution_observer.py` + porta `evolution_observer.py`.
- **Entregar:** 4 módulos + testes de valor-ouro e de invariante.
- **Aceite:** com semente 42 no cenário de referência, devolve plano **`[0, 22, 0, 0, 98, 0]`** com fitness **816,9178** e custo **R$ 987,44**; `history` tem `generations` elementos e é **não-decrescente** (testar com 1.000 gerações); `history[0]` é o melhor da população inicial; o resultado **empata com o guloso do-mais-barato-ao-mais-caro** (ótimo global — implementar `GreedyCheapestFirstPolicy` em `tests/`); todo plano de toda geração é viável (verificado por observer); caso degenerado `population_size=2, generations=1, elite_size=2` roda; cenário sem necessidade ⇒ plano zero, fitness 1000, sem laço infinito.
- **Não fazer:** nenhum import de Redis/Celery; o engine não persiste nada.

### TASK 17 — Testes de contrato das portas de domínio
- **Depende de:** TASK 16 · **Camada:** `tests/contracts/`
- **Ler antes:** `02-padroes-de-engenharia/04-estrategia-de-testes.md` (seção 3), `01-solid.md` (seção LSP)
- **Fazer:** bateria parametrizada por porta: `FitnessPolicy`, `PlanRepair`, `SelectionStrategy`, `CrossoverStrategy`, `MutationStrategy`, `RandomSource`.
- **Entregar:** 6 arquivos de contrato + `pytest --cov=domain` ≥ **95%**.
- **Aceite:** cada bateria roda contra **todas** as implementações existentes da porta; `SelectionStrategy` sempre devolve ≥ 2 progenitores; `PlanRepair` sempre devolve plano viável; trocar qualquer estratégia por um dublê **não** exige alterar `EvolutionEngine` (teste explícito de OCP/DIP).
- **Não fazer:** não teste infraestrutura aqui.

> **PORTÃO DA FASE 3:** o AG reproduz o notebook de forma determinística, sem Redis, Celery ou sklearn. Cobertura de `domain/` ≥ 95%.

---

## FASE 4 — Previsão de demanda e casos de uso

### TASK 18 — Conceitos de previsão no domínio
- **Depende de:** TASK 5 · **Camada:** `domain/forecasting/` + `domain/ports/`
- **Ler antes:** `01-dominio-e-negocio/03-previsao-de-demanda.md` (seções 2 e 7), `01-glossario-e-linguagem-ubiqua.md` (seção 3)
- **Fazer:** `stock_snapshot.py`, `stock_snapshots.py`, `weekly_demand_forecast.py`, `weekly_demand_forecasts.py`, `feature_schema.py` + porta `demand_forecaster.py`.
- **Entregar:** 6 módulos + testes.
- **Aceite:** `FeatureSchema.ORDERED_NAMES` define as 5 features em **um único lugar**, na ordem `stock_on_hand, weekly_outflow, monthly_outflow, unit_price, promotion_flag`; `WeeklyDemandForecast` garante inteiro `≥ 1` (RN-02); `StockSnapshots.latest_per_product()` é determinístico; nenhum import de pandas/sklearn.
- **Não fazer:** nenhuma chamada a sklearn.

### TASK 19 — Gerador do dataset sintético `∥`
- **Depende de:** TASK 18 · **Camada:** `infrastructure/dataset/`
- **Ler antes:** `01-dominio-e-negocio/03-previsao-de-demanda.md` (seção 4 — fórmulas e ordem dos sorteios)
- **Fazer:** `product_catalog.py` (os 6 produtos com saída típica e preço base), `synthetic_dataset_generator.py`, `simulated_stock_history_repository.py` + porta `stock_history_repository.py`.
- **Entregar:** 3 módulos + 1 porta + testes.
- **Aceite:** 120 registros (6 produtos × 20 semanas de 7 dias a partir de `2026-02-18`); **ordem dos sorteios exatamente** como no documento; reprodutível com semente 42; devolve `StockSnapshots` (não DataFrame) na fronteira do adaptador.
- **Não fazer:** não altere as fórmulas para "melhorar" o dataset — isso muda o MAE de referência.

### TASK 20 — Forecaster com regressão linear e persistência do modelo
- **Depende de:** TASK 18, TASK 19 · **Camada:** `infrastructure/forecasting/`
- **Ler antes:** `01-dominio-e-negocio/03-previsao-de-demanda.md` (seções 3, 6, 7), decisão **D-11**
- **Fazer:** `linear_regression_demand_forecaster.py`, `model_store.py` (joblib: salvar/carregar com features + semente + MAE + versão de schema, e CLI `--train`), `cached_demand_forecaster.py` (Decorator).
- **Entregar:** 3 módulos + testes de integração em `tests/integration/forecasting/`.
- **Aceite:** split 80/20 com `random_state=42` (96/24); **MAE ≤ 6,0**; previsões inteiras `≥ 1`; carregamento lazy com cache em processo; artefato com schema incompatível é descartado e retreinado, nunca usado; `python -m infrastructure.forecasting.model_store --train` gera o artefato em `MODEL_STORE_PATH`.
- **Não fazer:** não use Prophet nem ensembles (D-11); não normalize as features.

### TASK 21 — Dublê `FixedDemandForecaster` `∥`
- **Depende de:** TASK 18 · **Camada:** `tests/doubles/`
- **Ler antes:** `02-padroes-de-engenharia/04-estrategia-de-testes.md` (seções 1 e 5)
- **Fazer:** `fixed_demand_forecaster.py` devolvendo previsões constantes configuráveis, mais `recording_evolution_observer.py` e `in_memory_task_result_store.py`.
- **Entregar:** 3 dublês + testes que provam que atendem às portas.
- **Aceite:** com os dublês, **todos** os testes de domínio e de caso de uso rodam sem sklearn, pandas, numpy ou Redis instalados.
- **Não fazer:** dublê não entra em `src/`.

### TASK 22 — `BuildReplenishmentScenario` (RN-01 a RN-03)
- **Depende de:** TASK 7, TASK 18, TASK 21 · **Camada:** `application/use_cases/`
- **Ler antes:** `01-dominio-e-negocio/02-regras-de-negocio.md` (RN-01..RN-03), `03-previsao-de-demanda.md` (seção 5)
- **Fazer:** `build_replenishment_scenario.py`: último registro por produto → previsão → `cycle_demand = previsão × 4` → `required = max(0, cycle_demand − estoque)` → ordenar por nome de produto → `ReplenishmentScenario`.
- **Entregar:** 1 caso de uso + testes com `FixedDemandForecaster`.
- **Aceite:** com as previsões do cenário de referência (42, 60, 39, 46, 81, 65), reproduz necessidades **0, 48, 0, 0, 98, 0** e `required_total == 146`; ordem dos itens estável (alfabética por produto); roda sem sklearn.
- **Não fazer:** não retreine o modelo aqui (D-11 / seção 5 de `03-previsao-de-demanda.md`).

### TASK 23 — Casos de uso de otimização, comparação e risco
- **Depende de:** TASK 12, TASK 16, TASK 22 · **Camada:** `application/`
- **Ler antes:** `03-implementacao/02-contratos-de-codigo-backend.md` (seção 4), `06-baseline-e-indicadores.md` (seção 4)
- **Fazer:** `optimize_replenishment.py`, `compare_replenishment_strategies.py`, `classify_stock_risk.py`, `read_optimization_status.py` + DTOs `optimization_request.py` e `optimization_outcome.py`.
- **Entregar:** 4 casos de uso + 2 DTOs + testes.
- **Aceite:** fluxo completo histórico → previsão → cenário → plano ótimo → comparativo roda **em teste unitário sem infraestrutura**; comparativo reproduz a tabela da seção 4 de `06-baseline-e-indicadores.md` (236,58 vs 816,92); nenhum import de Celery/Redis/FastAPI/sklearn em `application/`.
- **Não fazer:** não persista nem publique progresso aqui (portas injetadas, implementadas na fase 5).

> **PORTÃO DA FASE 4:** pipeline ponta a ponta em teste unitário, sem nenhuma infraestrutura.

---

## FASE 5 — Infraestrutura, API e tempo real

### TASK 24 — `Settings` e container de injeção
- **Depende de:** TASK 23 · **Camada:** `core/`
- **Ler antes:** `02-padroes-de-engenharia/01-solid.md` (seção DIP), `03-modularidade-e-fronteiras.md` (seção 4), `02-contratos-de-codigo-backend.md` (seção 8), decisão **D-07**
- **Fazer:** completar `core/config.py` e criar `core/container.py` com as funções de composição (`build_optimization_use_case`, etc.), incluindo o mapa de `dataset_reference` → repositório.
- **Entregar:** 2 módulos + testes de composição.
- **Aceite:** `container.py` é o **único** arquivo que instancia classes concretas; `dataset_reference` desconhecido → erro mapeado para `422 UNKNOWN_DATASET`; nenhum service locator; `Settings` instanciado uma vez e injetado.
- **Não fazer:** não leia `os.environ` fora de `config.py`.

### TASK 25 — Adaptadores Redis e progresso
- **Depende de:** TASK 16, TASK 24 · **Camada:** `infrastructure/messaging/`, `persistence/`, `application/decorators/`
- **Ler antes:** `01-dominio-e-negocio/05-algoritmo-genetico.md` (seção 6), `03-implementacao/02-contratos-de-codigo-backend.md` (seção 5.3)
- **Fazer:** `redis_task_result_store.py` + porta `task_result_store.py`, `redis_progress_publisher.py`, `redis_progress_subscriber.py`, `throttled_evolution_observer.py`, `infrastructure/time/system_clock.py` + porta `clock.py`.
- **Entregar:** 5 módulos + 2 portas + testes de integração com Redis real.
- **Aceite:** publica em `progress:{task_id}`; `ThrottledEvolutionObserver` repassa 1 em cada 10 gerações **sempre incluindo a primeira e a última**; **falha de publicação não derruba a otimização** (loga e segue — teste com Redis indisponível).
- **Não fazer:** não coloque regra de negócio nos adaptadores.

### TASK 26 — Celery e task de otimização
- **Depende de:** TASK 23, TASK 24, TASK 25 · **Camada:** `core/` + `infrastructure/tasks/`
- **Ler antes:** `03-implementacao/02-contratos-de-codigo-backend.md` (seção 6), `04-docker-e-infraestrutura.md` (seção 1)
- **Fazer:** `core/celery_app.py` e `infrastructure/tasks/optimization_task.py`.
- **Entregar:** 2 módulos + teste de integração com worker real.
- **Aceite:** fila `optimization_queue`; `task_id` do Celery **é** o da API; `task_time_limit=300` / `soft=270`; exceção de domínio ⇒ resultado `FAILED` com código mapeado e **sem retry**; a task só traduz, delega e devolve (zero regra).
- **Não fazer:** não chame o `EvolutionEngine` direto — vá pelo caso de uso.

### TASK 27 — Rotas REST e schemas
- **Depende de:** TASK 24, TASK 26 · **Camada:** `api/`
- **Ler antes:** `03-implementacao/02-contratos-de-codigo-backend.md` (seções 5.1, 5.2), decisões **D-01**, **D-05**
- **Fazer:** `api/schemas/requests.py`, `responses.py`, `api/routes/optimization_routes.py`, `status_routes.py`, `api/mappers/scenario_mapper.py`, `outcome_mapper.py`.
- **Entregar:** 6 módulos + testes de API.
- **Aceite:** `POST /api/v1/optimize` → **202** com `task_id`; campos opcionais com os padrões do notebook (`mutation_rate=0.20`, `parents_size=20`, `elite_size=2`, `random_seed=42`, `cycle_weeks=4`); validações fora de faixa → **422**; `GET /api/v1/status/{task_id}` devolve o payload **exatamente** como na seção 5.2; **`projected_profit` NÃO é emitido** (D-01); `items_to_buy` só com `quantity > 0`, ordenado por `line_cost` desc; `api/` não importa `infrastructure/` direto.
- **Não fazer:** não invente campos fora do contrato sem registrar `D-nn`.

### TASK 28 — WebSocket de progresso
- **Depende de:** TASK 25, TASK 27 · **Camada:** `api/websockets/`
- **Ler antes:** `03-implementacao/02-contratos-de-codigo-backend.md` (seção 5.3), decisões **D-06**, **D-09**
- **Fazer:** `progress_socket.py` em **`/ws/v1/progress/{task_id}`** (D-06), assinando o canal Redis e repassando ao cliente.
- **Entregar:** 1 módulo + teste de integração.
- **Aceite:** emite `{generation, max_fitness, status}`; `status` vai de `evolving` para `completed`/`failed`; encerra após o estado final; `task_id` inexistente fecha com **4404**; desconexão do cliente não derruba o worker.
- **Não fazer:** não use o caminho `/ws/progress/...` sem versão.

### TASK 29 — Tratamento de erros HTTP `∥`
- **Depende de:** TASK 27 · **Camada:** `api/errors/`
- **Ler antes:** `03-implementacao/02-contratos-de-codigo-backend.md` (seção 7)
- **Fazer:** `exception_handlers.py` mapeando as 6 exceções de domínio da tabela.
- **Entregar:** 1 módulo + teste por código de erro.
- **Aceite:** formato `{"error": {"code": "...", "message": "..."}}`; mensagens em **português**; **nenhum stack trace** na resposta; os 6 mapeamentos cobertos.
- **Não fazer:** não devolva `500` genérico para erro de validação.

### TASK 30 — Integração e ponta a ponta no Compose
- **Depende de:** TASK 20, TASK 28, TASK 29 · **Camada:** `tests/integration/`, `tests/e2e/`
- **Ler antes:** `02-padroes-de-engenharia/04-estrategia-de-testes.md` (seções 1 e 8), `03-implementacao/04-docker-e-infraestrutura.md` (seção 10)
- **Fazer:** testes e2e cobrindo os 10 critérios de containerização.
- **Entregar:** suíte e2e + alvo `make e2e`.
- **Aceite:** os **10 critérios** da seção 10 de `04-docker-e-infraestrutura.md` passam, incluindo: `COMPLETED` em até 60 s; ≥ 2 mensagens de progresso com `generation` crescente; `down -v && up` funcionando do zero; nada exigindo Python/Node no host.
- **Não fazer:** não "pule" o teste do WebSocket por ser chato de automatizar — é o requisito de tempo real.

> **PORTÃO DA FASE 5:** `docker compose up` + `POST /optimize` devolve o plano de referência, com progresso chegando por WebSocket.

---

## FASE 6 — Frontend

### TASK 31 — Scaffold e contratos TypeScript
- **Depende de:** TASK 27 · **Camada:** `frontend/`
- **Ler antes:** `03-implementacao/03-contratos-de-codigo-frontend.md` (seções 1 e 10), decisão **D-01**
- **Fazer:** Vite + React + TS + Tailwind + TanStack Query; `src/shared/api/contracts.ts` com **todos** os tipos da seção 1.
- **Entregar:** scaffold + `contracts.ts` + `tailwind.config.js` + regra ESLint `import/no-restricted-paths` entre features.
- **Aceite:** `tsc --noEmit` limpo; **zero `any`**; tipos da API existem em **um só** arquivo; `ScenarioSummary` **sem** `projected_profit`.
- **Não fazer:** não duplique tipo de API em componente.

### TASK 32 — Clientes HTTP e WebSocket `∥`
- **Depende de:** TASK 31 · **Camada:** `frontend/src/shared/api/`
- **Ler antes:** `03-implementacao/03-contratos-de-codigo-frontend.md` (seção 2)
- **Fazer:** `httpClient.ts` (`OptimizationApi` + factory) e `websocketClient.ts` (`ProgressChannel` + factory), lendo `VITE_API_BASE_URL` / `VITE_WS_BASE_URL`.
- **Entregar:** 2 módulos + dublês de teste + testes.
- **Aceite:** componentes dependem da **interface**, não de `fetch`; testes injetam implementação falsa **sem mock de `fetch`**; reconexão de socket tratada.
- **Não fazer:** nenhum `fetch`/`axios` fora desta pasta.

### TASK 33 — Formulário de otimização
- **Depende de:** TASK 32 · **Camada:** `features/optimization/`
- **Ler antes:** `03-implementacao/03-contratos-de-codigo-frontend.md` (seções 3, 4, 6)
- **Fazer:** `OptimizationForm.tsx`, `useStartOptimization.ts`, `optimizationFormSchema.ts` e `shared/formatting/` (`currency.ts`, `percentage.ts`, `units.ts`).
- **Entregar:** 3 arquivos da feature + 3 de formatação + testes.
- **Aceite:** padrões R$ 1.000,00 / 60 / 100 / 0,20; validação com mensagens em português; formatação via `Intl.NumberFormat('pt-BR')` (**nenhum `toFixed` espalhado**); botão desabilitado + spinner enquanto envia.
- **Não fazer:** não calcule nada de negócio no componente.

### TASK 34 — Acompanhamento: polling e WebSocket
- **Depende de:** TASK 32, TASK 33 · **Camada:** `features/optimization/`, `features/convergence/`
- **Ler antes:** `03-implementacao/03-contratos-de-codigo-frontend.md` (seções 3 e 7)
- **Fazer:** `useOptimizationStatus.ts` e `useProgressSocket.ts`.
- **Entregar:** 2 hooks + testes.
- **Aceite:** `refetchInterval` 2 s enquanto `PROCESSING` e **`false`** após `COMPLETED`/`FAILED`; `staleTime: Infinity` depois de concluir; socket indisponível **não** bloqueia a tela (cai para polling com aviso discreto).
- **Não fazer:** não deixe polling rodando para sempre.

### TASK 35 — Resultados: KPIs, plano e comparativo
- **Depende de:** TASK 34 · **Camada:** `features/results/`
- **Ler antes:** `03-implementacao/03-contratos-de-codigo-frontend.md` (seções 4 e 6), `01-dominio-e-negocio/06-baseline-e-indicadores.md` (seções 4 e 6)
- **Fazer:** `KpiCards.tsx`, `PurchasePlanTable.tsx`, `StrategyComparisonTable.tsx`.
- **Entregar:** 3 componentes + testes com o payload de referência.
- **Aceite:** exibe **R$ 987,44 · 98,7% · 82,2% · 1 produto em risco · fitness 816,92 · ± 4,76 un./semana**, tudo em pt-BR; comparativo mostra baseline × otimizado; tabelas com `<caption>` e `<th scope>`.
- **Não fazer:** não recalcule indicadores no frontend — eles vêm da API.

### TASK 36 — Gráficos Plotly
- **Depende de:** TASK 34, TASK 35 · **Camada:** `features/convergence/`, `features/results/`
- **Ler antes:** `03-implementacao/03-contratos-de-codigo-frontend.md` (seção 5), decisão **D-09**
- **Fazer:** `ConvergenceChart.tsx`, `BudgetDistributionChart.tsx` e o comparativo necessidade × comprado.
- **Entregar:** 3 gráficos + testes de renderização.
- **Aceite:** curva avança ao vivo durante a execução; **eixo Y escalado pelos dados** (nunca 0–12500 — D-09); distribuição ordenada por custo desc, só itens comprados; `locale: 'pt-BR'`, `responsive: true`; estado vazio explícito ("Aguardando primeira geração…"); cada gráfico acompanhado de tabela equivalente.
- **Não fazer:** não deixe gráfico em branco como estado de carregamento.

### TASK 37 — Estados de UI e acessibilidade
- **Depende de:** TASK 35, TASK 36 · **Camada:** `frontend/src/`
- **Ler antes:** `03-implementacao/03-contratos-de-codigo-frontend.md` (seções 7, 8, 9)
- **Fazer:** os **7 estados** da tabela (inicial, enviando, processando, socket indisponível, concluído, falha, resultado vazio) + passagem de acessibilidade.
- **Entregar:** componentes de estado + testes por estado.
- **Aceite:** os 7 estados renderizam; "Estoque suficiente para o ciclo — nenhuma compra necessária" quando não há necessidade; labels associados e `aria-describedby` em erro; layout funcional a partir de **360 px**; contraste AA.
- **Não fazer:** não mostre erro bloqueante quando só o WebSocket falhou.

> **PORTÃO DA FASE 6:** demonstração ponta a ponta no navegador com os números do notebook na tela.

---

## FASE 7 — Fechamento

### TASK 38 — `README.md` do repositório `∥`
- **Depende de:** TASK 30 · **Camada:** repositório
- **Ler antes:** `INDEX.md`, `03-implementacao/04-docker-e-infraestrutura.md`
- **Fazer:** README com propósito, diagrama do fluxo, como subir (`make up`), como testar, como pré-treinar o modelo, e o aviso de dados simulados (RN-09).
- **Entregar:** `README.md`.
- **Aceite:** alguém sem contexto sobe o sistema seguindo **só** o README; aponta para `.context/INDEX.md` para detalhes.
- **Não fazer:** não duplique a base de contexto no README.

### TASK 39 — Pipeline de CI
- **Depende de:** TASK 30, TASK 37 · **Camada:** repositório
- **Ler antes:** `02-padroes-de-engenharia/04-estrategia-de-testes.md` (seção 6)
- **Fazer:** workflow com **todos** os portões: `ruff format --check`, `ruff check`, `mypy --strict`, `lint-imports`, `check_calisthenics.sh`, `pytest --cov=domain --cov-fail-under=95`, `--cov-fail-under=80` global, `tsc --noEmit`, `eslint`, `vitest run`.
- **Entregar:** arquivo de workflow + alvos no `Makefile`.
- **Aceite:** build **vermelho** se qualquer portão falhar (provado quebrando um de propósito e revertendo).
- **Não fazer:** não marque portão como `continue-on-error`.

### TASK 40 — Fixar versões `∥`
- **Depende de:** TASK 39 · **Camada:** repositório
- **Ler antes:** `03-implementacao/04-docker-e-infraestrutura.md` (seção 6)
- **Fazer:** fixar com `==` em `requirements.txt` / `requirements-dev.txt` e versões exatas em `package.json`; commitar `package-lock.json`.
- **Entregar:** arquivos de dependência fixados.
- **Aceite:** `docker compose build --no-cache` em máquina limpa produz o mesmo ambiente; MAE e fitness seguem reproduzindo os valores-ouro.
- **Não fazer:** não fixe antes do CI estar verde (TASK 39).

### TASK 41 — Revisão final contra as 4 exigências
- **Depende de:** todas · **Camada:** repositório
- **Ler antes:** `INDEX.md` (seção 3) + os 4 documentos de `02-padroes-de-engenharia/`
- **Fazer:** percorrer os checklists de revisão de `01-solid.md` (6 itens), `02-object-calisthenics.md` (seções 10 e 11), `03-modularidade-e-fronteiras.md` (seção 7, 8 sinais de erosão) e `04-estrategia-de-testes.md` (seção 6).
- **Entregar:** relatório de conformidade apontando arquivo/linha de cada exceção `# OC-8` e cada decisão `D-nn` aplicada.
- **Aceite:** **SOLID** — toda dependência externa atrás de porta, nada concreto fora do container; **Object Calisthenics** — greps sem violação e exceções todas justificadas; **Docker** — os 10 critérios verdes; **Modularidade** — `lint-imports` verde com os 3 contratos.
- **Não fazer:** não "resolva" violação apagando o teste ou afrouxando o portão — registre `D-nn` ou corrija o código.

---

## Quadro de acompanhamento

| Fase | Tasks | Portão de saída |
|---|---|---|
| 0 — Fundação | 1 · 2 · 3 · 4 | Redis + API *healthy*, lint executável |
| 1 — Value Objects | 5 · 6 · 7 | Domínio testado sem numpy |
| 2 — Regras de decisão | 8 · 9 · 10 · 11 · 12 | Fitness e baseline nos valores-ouro |
| 3 — Motor evolutivo | 13 · 14 · 15 · 16 · 17 | AG em 816,92 determinístico, `domain/` ≥ 95% |
| 4 — Previsão e casos de uso | 18 · 19 · 20 · 21 · 22 · 23 | Pipeline completo sem infraestrutura |
| 5 — Infra, API, tempo real | 24 · 25 · 26 · 27 · 28 · 29 · 30 | Compose ponta a ponta com WebSocket |
| 6 — Frontend | 31 · 32 · 33 · 34 · 35 · 36 · 37 | Demonstração no navegador |
| 7 — Fechamento | 38 · 39 · 40 · 41 | As 4 exigências verificadas |

**Caminho mínimo se o prazo apertar:** TASK 1 → 23 entregam o valor acadêmico central (regra de negócio, fitness e AG reproduzindo o notebook, com SOLID/Object Calisthenics/modularidade provados por teste). TASK 24 → 30 entregam a containerização exigida. Reduza o escopo dos gráficos (TASK 36) **antes** de reduzir testes de domínio.
