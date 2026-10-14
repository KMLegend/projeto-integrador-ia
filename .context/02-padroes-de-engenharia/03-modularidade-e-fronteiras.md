---
id: 03-modularidade-e-fronteiras
dominio: padroes-de-engenharia
palavras-chave: modularidade, camadas, clean architecture, regra de dependencia, import-linter, fronteiras, acoplamento, container, injecao
fonte-da-verdade: exigencia explicita do projeto + .context/00-arquitetura-tecnica/especifica_es_do_backend.md
depende-de: [01-solid, 02-object-calisthenics]
---

# Modularidade e Fronteiras entre Módulos

Exigência **não-negociável** nº 4. Modularidade aqui não é "muitas pastas": é **direção de dependência controlada e verificada por ferramenta**.

---

## 1. As quatro camadas

```
┌─────────────────────────────────────────────────────────────┐
│ api/            Adaptadores de ENTRADA (FastAPI, WebSocket) │
│ infrastructure/ Adaptadores de SAIDA (sklearn, Redis, CSV)  │
├─────────────────────────────────────────────────────────────┤
│ application/    Casos de uso (orquestracao, sem regra)      │
├─────────────────────────────────────────────────────────────┤
│ domain/         Regra de negocio + PORTAS (Protocols)       │
└─────────────────────────────────────────────────────────────┘
          dependencias apontam SEMPRE para baixo
```

| Camada | Contém | Pode importar | Nunca importa |
|---|---|---|---|
| `domain/` | Value Objects, entidades, políticas, portas (`Protocol`), exceções de domínio | Apenas stdlib (`dataclasses`, `typing`, `enum`, `decimal`, `abc`) | Qualquer outra camada; qualquer biblioteca de terceiros |
| `application/` | Casos de uso, DTOs internos, decorators de porta | `domain/` + stdlib | `api/`, `infrastructure/`, bibliotecas de terceiros |
| `infrastructure/` | sklearn, numpy/pandas, Redis, joblib, gerador de dataset, Celery | `domain/`, `application/`, terceiros | `api/` |
| `api/` | Routers, schemas Pydantic, mappers, endpoint WebSocket | `domain/`, `application/`, `core/` | `infrastructure/` **diretamente** (só via container) |
| `core/` | Configuração, container de injeção, app Celery | Todas | — |

**A regra em uma frase:** o domínio não sabe que existem FastAPI, Celery, Redis, sklearn ou React. Ele poderia ser executado por um script de linha de comando sem alterar uma linha.

## 2. Verificação automática (obrigatória no CI)

`backend/.importlinter`:

```ini
[importlinter]
root_packages = domain, application, infrastructure, api, core

[importlinter:contract:camadas]
name = Regra de dependencia das camadas
type = layers
layers =
    api
    infrastructure
    application
    domain

[importlinter:contract:dominio-puro]
name = Dominio nao depende de bibliotecas externas
type = forbidden
source_modules = domain, application
forbidden_modules =
    numpy
    pandas
    sklearn
    joblib
    redis
    celery
    fastapi
    pydantic
    starlette

[importlinter:contract:api-nao-toca-infra]
name = API acessa infraestrutura somente pelo container
type = forbidden
source_modules = api
forbidden_modules = infrastructure
ignore_imports =
    core.container -> infrastructure.*
```

```bash
lint-imports --config backend/.importlinter
```

Falha de contrato **quebra o build**. Esse é o critério objetivo da exigência de modularidade.

## 3. Módulos funcionais (dentro das camadas)

Além das camadas horizontais, o domínio é dividido por **assunto**:

```
domain/
  model/        Value Objects e entidades compartilhados
  policy/       Regras de decisao (fitness, reparo, risco, baseline)
  evolution/    Motor evolutivo e seus operadores
  forecasting/  Conceitos de previsao (sem implementacao de ML)
  ports/        Protocols consumidos pelo dominio
  errors/       Excecoes de dominio
```

Regras entre módulos funcionais:

* `evolution/` depende de `model/` e `ports/`; **não** depende de `policy/` (recebe `FitnessPolicy` por injeção).
* `forecasting/` **não** depende de `evolution/`. A ponte entre previsão e otimização é um caso de uso em `application/`.
* `policy/` depende de `model/`. Não depende de `evolution/`.
* Dependência circular entre módulos funcionais é **erro de build**, nunca "resolvida" com import dentro de função.

## 4. Composição num único ponto

`core/container.py` é o **único** arquivo que conhece classes concretas e faz `new`:

```python
# core/container.py (esboco)
def build_optimization_use_case(settings: Settings) -> OptimizeReplenishment:
    random_source = SeededRandomSource(settings.random_seed)
    repair = BudgetAwarePlanRepair(BudgetConstraint(settings.budget_limit))
    fitness = WeightedFitnessPolicy(CoverageCalculator(), FitnessWeights.default())
    engine = EvolutionEngine(
        settings.evolution_settings(),
        EvolutionOperators.standard(random_source, repair, fitness),
    )
    return OptimizeReplenishment(
        ScenarioBuilder(forecaster_for(settings), settings.cycle()),
        OptimizationRunner(engine, fitness, NaiveReplenishmentPolicy(repair)),
    )
```

* Troca de implementação = mudança **só** aqui.
* Proibido *service locator* (objeto global consultado de dentro das classes) — isso reintroduz acoplamento escondido.
* A task Celery chama `build_optimization_use_case(...)` e nada mais; não contém regra.

## 5. Fronteira backend ↔ frontend

| Aspecto | Regra |
|---|---|
| Fonte da verdade | `00-arquitetura-tecnica/contratos_de_api.md` |
| Direção | O frontend se adapta ao contrato; o contrato não muda para conveniência de componente |
| Tipos | `frontend/src/shared/api/contracts.ts` espelha o contrato e é o **único** lugar com esses tipos |
| Tradução | Nenhum componente React lê JSON cru da API: mappers convertem para os tipos de domínio do frontend |
| Versionamento | Prefixo `/api/v1`; mudança incompatível vira `/api/v2` |

## 6. Modularidade no frontend

```
frontend/src/
  features/
    optimization/     Formulario, disparo da tarefa, acompanhamento
    results/          KPIs, tabela do plano, comparativo
    convergence/      Grafico de convergencia (WebSocket)
  shared/
    api/              Cliente HTTP, cliente WebSocket, contratos
    ui/               Componentes burros reutilizaveis
    formatting/       Formatacao pt-BR de moeda, percentual, numero
```

* Uma feature **não** importa de outra feature. Compartilhamento acontece via `shared/`.
* Componente não chama `fetch` direto: usa hook da própria feature, que usa o cliente de `shared/api/` (DIP no frontend).
* `shared/ui/` não conhece domínio de estoque (sem `ProductCard` com regra dentro).

## 7. Sinais de erosão da modularidade (recusar em revisão)

- [ ] `from infrastructure...` dentro de `domain/` ou `application/`.
- [ ] `import pandas` em `application/`.
- [ ] Import dentro de função para quebrar ciclo.
- [ ] Classe concreta instanciada fora do `container.py`.
- [ ] `__init__.py` reexportando símbolo de outra camada ("atalho" que fura a fronteira).
- [ ] Modelo Pydantic usado como objeto de domínio.
- [ ] Componente React importando de outra feature.
- [ ] Tipo de API duplicado em dois arquivos do frontend.
