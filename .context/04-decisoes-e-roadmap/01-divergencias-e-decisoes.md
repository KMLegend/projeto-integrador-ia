---
id: 01-divergencias-e-decisoes
dominio: decisoes
palavras-chave: ADR, decisoes de arquitetura, divergencias, conflitos, lucro, profit, DEAP, pygad, dinheiro, float, centavos, versionamento
fonte-da-verdade: este documento (maior precedencia da base)
depende-de: []
---

# Divergências e Decisões (ADR)

**Este documento tem a maior precedência da base.** Ele registra os pontos em que o notebook, a arquitetura e o contrato de API discordam entre si, e a decisão que resolve cada caso. Quem implementar deve seguir a decisão, não a fonte original divergente.

Formato: `D-nn` · Contexto → Decisão → Consequência.

---

## D-01 — `projected_profit` no contrato de API × fitness não modela lucro

**Contexto.** `00-arquitetura-tecnica/contratos_de_api.md` especifica `best_scenario_summary` com `total_cost` e `projected_profit`. O notebook (Entregável 04) não tem lucro: o dataset não tem preço de venda nem margem, e a função fitness otimiza **cobertura da demanda** e **número de produtos em risco**.

**Decisão.**
1. `projected_profit` **não é emitido** pela API. Reportar lucro que o sistema não calcula seria inventar número — inaceitável numa entrega avaliada por banca.
2. `best_scenario_summary` é estendido com os indicadores que o sistema realmente produz: `budget_limit`, `budget_usage_ratio`, `served_quantity`, `required_total`, `served_ratio`, `items_at_risk`, `fitness`.
3. A palavra `profit`/`lucro` não aparece no código (ver `01-dominio-e-negocio/01-glossario-e-linguagem-ubiqua.md`, seção 4).
4. Se um dia o dataset ganhar preço de venda, entra uma `MarginAwareFitnessPolicy` (OCP) e **então** `projected_profit` passa a ser emitido.

**Consequência.** O frontend tipa `ScenarioSummary` sem `projected_profit`. O contrato original fica marcado como "exemplo ilustrativo" nesse campo.

## D-02 — DEAP/PyGAD × implementação própria do AG

**Contexto.** A visão geral da arquitetura lista "DEAP ou PyGAD" na stack. O notebook implementa o AG manualmente, com um operador de reparo customizado.

**Decisão.** **Implementação própria**, em `domain/evolution/`, sem biblioteca de AG.

Motivos: (a) fidelidade exata aos valores apresentados à banca, incluindo o reparo customizado; (b) o domínio precisa ficar livre de dependência externa para cumprir a regra de dependência e as exigências SOLID/Object Calisthenics; (c) o código do AG é a entrega acadêmica central de Computação Evolutiva — terceirizá-lo esvaziaria a avaliação.

**Consequência.** `deap`/`pygad` não entram no `requirements.txt`. Se forem desejados no futuro, entram como adaptador alternativo de uma porta `OptimizationEngine`, sem tocar no domínio.

## D-03 — Dinheiro em centavos inteiros, não `float`

**Contexto.** O notebook usa `float` e produziu `custo = 314.32000000000005`. Com `float`, a comparação `custo > ORCAMENTO` pode disparar remoção de unidade por erro de representação, mudando o plano recomendado.

**Decisão.** `Money` encapsula **inteiro em centavos**. Construção apenas por `Money.from_reais(str | Decimal)`. Proibido construir `Money` a partir de `float`. Na borda, Pydantic recebe número JSON e converte para `Decimal` antes de entrar no domínio.

**Consequência.** Comparações monetárias são exatas; testes comparam dinheiro por igualdade (sem tolerância). Verificado: os valores-ouro (R$ 314,32 / R$ 987,44 e os fitness 236,58 / 816,92) são **idênticos** em float e em centavos — a decisão não altera os números apresentados.

## D-04 — Estrutura de diretórios refinada (`ai_engine` dividido)

**Contexto.** `especifica_es_do_backend.md` sugere `/ai_engine/genetic_algorithm` e `/ai_engine/forecasting` no mesmo nível de `/api` e `/core`. Isso colocaria regra de negócio pura e código dependente de sklearn na mesma camada.

**Decisão.** Adotar a árvore de `03-implementacao/01-estrutura-de-diretorios.md`, com `domain/`, `application/`, `infrastructure/`, `api/`, `core/`. O `ai_engine` é dividido: conceitos e o motor evolutivo em `domain/evolution/` e `domain/forecasting/`; sklearn/joblib em `infrastructure/forecasting/`.

**Consequência.** A tabela de mapeamento da seção 2 de `01-estrutura-de-diretorios.md` é o rastro entre a sugestão original e a estrutura final. A sugestão original fica como referência histórica.

## D-05 — Extensões do payload de API são opcionais e retrocompatíveis

**Contexto.** O contrato de `POST /api/v1/optimize` define `budget_limit`, `dataset_reference` e `ga_parameters` com `population_size` e `generations`. O notebook também tem taxa de mutação, nº de pais, elitismo, semente e semanas do ciclo.

**Decisão.** Campos novos são **opcionais e com padrão** igual ao do notebook: `mutation_rate=0.20`, `parents_size=20`, `elite_size=2`, `random_seed=42`, `cycle_weeks=4`. Uma requisição no formato original do contrato continua válida e produz o comportamento do notebook.

**Consequência.** Nenhuma quebra de contrato. Mudança incompatível, se vier, exige `/api/v2`.

## D-06 — Caminho do WebSocket: `/ws/v1/progress/{task_id}`

**Contexto.** `especifica_es_do_backend.md` menciona `/ws/progress/{task_id}`; `contratos_de_api.md` especifica `WS /ws/v1/progress/{task_id}`.

**Decisão.** Vale o contrato: **`/ws/v1/progress/{task_id}`** (versionado, coerente com `/api/v1`).

**Consequência.** O frontend usa `VITE_WS_BASE_URL + /ws/v1/progress/{task_id}`; o Nginx faz proxy de `/ws/`.

## D-07 — Semântica de `dataset_reference`

**Contexto.** O contrato exige `dataset_reference` (ex.: `"historico_mensal_v1"`), mas não existe dado real — só o dataset simulado.

**Decisão.** `dataset_reference` é um **identificador lógico de fonte de histórico**, resolvido para uma implementação de `StockHistoryRepository`:

| Valor | Resolve para |
|---|---|
| `historico_mensal_v1` (e o padrão) | `SimulatedStockHistoryRepository` (120 registros, semente 42) |
| Qualquer outro valor | `422` com código `UNKNOWN_DATASET` |

**Consequência.** Plugar um ERP real no futuro é registrar uma nova referência no mapa do container — sem mudar contrato nem domínio.

## D-08 — Valores-ouro a partir de fixture estática, não de dataset regerado

**Contexto.** O cenário de referência (preços 29,89/18,78/… e necessidades 48 e 98) vem de 120 registros gerados por uma sequência específica de sorteios de NumPy. Testes que regeram esse dataset ficariam reféns da ordem exata dos sorteios e de versões de biblioteca.

**Decisão.** Os testes de valor-ouro usam a fixture estática `backend/tests/fixtures/reference_scenario.json` (conteúdo normativo em `01-dominio-e-negocio/06-baseline-e-indicadores.md`). O gerador sintético tem testes próprios, com tolerância (`MAE ≤ 6,0`), não de igualdade exata.

**Consequência.** Fitness, reparo e AG têm teste determinístico e estável; a camada de ML tem teste estatisticamente tolerante. Atualizar a fixture exige decisão explícita registrada aqui.

## D-09 — `max_fitness: 12500.00` no exemplo do contrato é ilustrativo

**Contexto.** O exemplo de mensagem WebSocket no contrato traz `max_fitness: 12500.00`. Com a função fitness definida (`served_ratio × 10 − items_at_risk × 5`), o teto é **1000**.

**Decisão.** O valor do exemplo é ilustrativo; a **escala real é 0 a 1000**. O campo permanece `max_fitness` (nome do contrato), tipo número decimal.

**Consequência.** O eixo Y do gráfico de convergência é dimensionado pelos dados recebidos, nunca por um máximo fixo de 12500 — senão a curva fica achatada e ilegível.

## D-10 — `unit_price` serve como preço de venda e custo de compra

**Contexto.** O dataset tem uma única coluna `preco`, usada como feature do modelo (preço de venda, que afeta a demanda) e como custo unitário de compra na otimização.

**Decisão.** Manter a simplificação do notebook, **documentando-a explicitamente** na UI e no relatório (RN-09).

**Consequência.** Dois campos separados (`sale_price` e `purchase_cost`) são evolução prevista; a separação não muda o AG, só o cálculo de custo — por isso está atrás de `UnitPrice`.

## D-11 — Previsão com regressão linear, não Prophet

**Contexto.** A stack menciona "Prophet/Scikit-Learn". O Entregável 03 usa `LinearRegression`.

**Decisão.** **`LinearRegression`** nesta implantação: é o modelo apresentado, interpretável e com MAE conhecido (4,76). Prophet exigiria série temporal por produto e muda a natureza do dataset.

**Consequência.** Prophet, se entrar, é outra implementação de `DemandForecaster` — zero mudança no domínio. `prophet` não entra no `requirements.txt` agora.

## D-12 — Object Calisthenics regra 8 (máx. 2 atributos) é cumprida por composição

**Contexto.** Limitar classes a 2 atributos de instância é a regra mais restritiva do conjunto, e modelos de domínio naturalmente acumulam campos.

**Decisão.** A regra vale integralmente em `domain/` e `application/`, cumprida por **composição** (`CatalogItem` + `ReplenishmentItem`; `EvolutionEngine` = `_settings` + `_operators`). Exceções: Value Objects de configuração (`EvolutionSettings`) e schemas Pydantic de borda, cada um com comentário `# OC-8: <justificativa>`. A lista fechada de exceções por camada está na seção 11 de `02-padroes-de-engenharia/02-object-calisthenics.md`.

**Consequência.** Exceção sem comentário justificando é recusada em revisão. Nenhuma exceção vale para `domain/`.

## D-13 — Portas do frontend: 5173 em dev, 3000 em produção

**Contexto.** `infraestrutura_docker.md` diz "porta 3000 ou 5173".

**Decisão.** **5173** em desenvolvimento (Vite dev server, via `docker-compose.override.yml`) e **3000** em produção (Nginx servindo `dist`). `CORS_ORIGINS` inclui as duas.

**Consequência.** Em produção, Nginx faz proxy de `/api/` e `/ws/`, então o frontend chama caminhos relativos e CORS deixa de ser necessário.

---

## Como registrar uma divergência nova

1. Acrescente uma entrada `D-nn` neste arquivo com Contexto → Decisão → Consequência.
2. Atualize o documento afetado para apontar para a decisão.
3. Se a decisão alterar número apresentado à banca (fitness, custo, MAE, cobertura), **pare e consulte o time** — esses valores estão nos slides e no notebook.
4. Nunca resolva divergência silenciosamente no código: sem registro, o próximo agente vai "consertar" de volta.
