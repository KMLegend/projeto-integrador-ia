---
id: 04-estrategia-de-testes
dominio: padroes-de-engenharia
palavras-chave: testes, pytest, piramide de testes, determinismo, valores ouro, testes de contrato, cobertura, CI, qualidade
fonte-da-verdade: derivado das exigencias do projeto
depende-de: [01-solid, 03-modularidade-e-fronteiras, 01-dominio-e-negocio/06-baseline-e-indicadores]
---

# Estratégia de Testes e Qualidade

O desenho SOLID só se sustenta se os testes o exercitarem. Esta estratégia é o que prova que as quatro exigências do projeto foram cumpridas.

---

## 1. Pirâmide

| Nível | O que cobre | Dependências externas | Tempo-alvo |
|---|---|---|---|
| **Domínio** (maioria) | Value Objects, fitness, reparo, operadores do AG, classificação de risco | Nenhuma — nem numpy | < 2 s total |
| **Contrato de porta** | Toda implementação de cada `Protocol` | Dublês | < 2 s |
| **Caso de uso** | Orquestração com portas falsas | Nenhuma | < 3 s |
| **Integração** | sklearn real, Redis real, Celery real | Containers | < 60 s |
| **Ponta a ponta** | `POST /optimize` → worker → `GET /status` + WebSocket | Compose completo | < 3 min |

Regra: um teste que precisa de Redis **não** é teste de domínio. Se um teste de domínio precisar de mock de rede, o desenho está errado.

## 2. Testes de valor-ouro (regressão de negócio)

Os números de `01-dominio-e-negocio/06-baseline-e-indicadores.md` viram testes. São eles que impedem alguém de "melhorar" o fitness e invalidar o que foi apresentado à banca:

```python
def test_baseline_reproduces_notebook_fitness(reference_scenario, fitness_policy):
    plan = PurchasePlan.of_units((0, 8, 0, 0, 28, 0))
    assessment = fitness_policy.evaluate(plan, reference_scenario)
    assert assessment.fitness_value() == pytest.approx(236.5753, abs=1e-4)
    assert reference_scenario.total_cost_of(plan) == Money.from_reais("314.32")

def test_genetic_algorithm_reaches_known_optimum(reference_scenario, engine_with_seed_42):
    result = engine_with_seed_42.evolve(reference_scenario)
    assert result.best_plan() == PurchasePlan.of_units((0, 22, 0, 0, 98, 0))
    assert result.best_fitness() == pytest.approx(816.9178, abs=1e-4)

def test_genetic_algorithm_matches_greedy_optimum(reference_scenario, engine_with_seed_42):
    greedy = GreedyCheapestFirstPolicy().build_plan(reference_scenario)
    assert engine_with_seed_42.evolve(reference_scenario).best_fitness() >= fitness_of(greedy)
```

## 3. Testes de contrato (LSP)

Uma bateria parametrizada por porta, aplicada a **todas** as implementações:

```python
@pytest.mark.parametrize("repair", [
    BudgetAwarePlanRepair(BudgetConstraint(Money.from_reais("1000.00"))),
    BatchedBudgetPlanRepair(BudgetConstraint(Money.from_reais("1000.00"))),
])
def test_repair_always_produces_feasible_plan(repair, reference_scenario, random_plans):
    for plan in random_plans:
        repaired = repair.repair(plan, reference_scenario)
        assert_within_required_quantities(repaired, reference_scenario)
        assert reference_scenario.total_cost_of(repaired) <= Money.from_reais("1000.00")
```

Implementação nova de porta **sem** entrar nessa lista é recusada em revisão.

## 4. Testes de propriedade (invariantes)

Com `hypothesis`, sobre as invariantes de `01-dominio-e-negocio/02-regras-de-negocio.md`:

| Propriedade | Afirmação |
|---|---|
| Viabilidade | Para qualquer plano aleatório, `repair` devolve plano dentro do orçamento e da necessidade |
| Idempotência | `repair(repair(p)) == repair(p)` |
| Faixa | `0 ≤ served_ratio ≤ 100` para qualquer plano reparado |
| Monotonicidade | Elitismo → `history` nunca decresce |
| Determinismo | Mesma semente ⇒ mesmo resultado (10 execuções) |
| Pureza | `evaluate` chamado 100× devolve o mesmo valor |

## 5. Determinismo (regra dura)

* Nenhum teste usa `random`, `numpy.random` ou `datetime.now()` diretamente — sempre `ScriptedRandomSource` e `FixedClock`.
* `ScriptedRandomSource` recebe a sequência exata de sorteios, permitindo testar crossover e mutação de forma exata, sem tolerância estatística.
* Teste intermitente (*flaky*) é tratado como falha de produto, não de teste: ou tem aleatoriedade não injetada, ou depende de ordem de execução.

## 6. Portões de qualidade no CI

| Portão | Comando | Critério |
|---|---|---|
| Formatação | `ruff format --check` | Sem diferença |
| Lint | `ruff check` | Zero erro (regras `C901`, `PLR0912`, `PLR0913` ativas) |
| Tipos | `mypy --strict backend/src` | Zero erro |
| Fronteiras | `lint-imports` | Todos os contratos cumpridos |
| Object Calisthenics | script de greps da seção 10 de `02-object-calisthenics.md` | Zero violação |
| Testes | `pytest` | Tudo verde |
| Cobertura de domínio | `pytest --cov=domain --cov-fail-under=95` | **≥ 95%** em `domain/` |
| Cobertura global | `--cov-fail-under=80` | ≥ 80% |
| Frontend | `tsc --noEmit`, `eslint`, `vitest run` | Zero erro |

Cobertura alta é exigida **só no domínio** — é onde está a regra de negócio e onde testar é barato. Exigir 95% de adaptador de Redis gera teste de mock sem valor.

## 7. Organização dos testes

```
backend/tests/
  unit/
    domain/          espelha a estrutura de domain/
    application/
  contracts/         uma bateria por porta
  properties/        testes com hypothesis
  integration/
    forecasting/     sklearn real
    messaging/       Redis real (testcontainers ou servico do compose)
  e2e/               API + worker via compose
  fixtures/
    reference_scenario.json    <- fixture canonica dos valores-ouro
  doubles/
    fixed_demand_forecaster.py
    scripted_random_source.py
    recording_evolution_observer.py
    in_memory_task_result_store.py
```

Nomenclatura: `test_<unidade>_<comportamento_esperado>`. Em português no docstring, em inglês no nome da função.

## 8. Testes de containerização

A exigência de Docker precisa de verificação executável:

1. `docker compose build` conclui sem erro.
2. `docker compose up -d` deixa os 4 serviços *healthy*.
3. `POST /api/v1/optimize` responde `202` com `task_id`.
4. Em até 60 s, `GET /api/v1/status/{task_id}` responde `COMPLETED` com plano viável.
5. O WebSocket recebe **ao menos 2** mensagens de progresso com `generation` crescente.
6. `docker compose down -v && docker compose up` funciona do zero (sem estado residual).
7. Nenhum passo acima exige Python ou Node instalados no host.
