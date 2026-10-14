---
id: 01-glossario-e-linguagem-ubiqua
dominio: dominio-e-negocio
palavras-chave: glossario, linguagem ubiqua, nomenclatura, traducao, ddd, naming
fonte-da-verdade: Projeto_Preditivo.ipynb (Entregaveis 02/03/04) + .context/00-arquitetura-tecnica/contratos_de_api.md
depende-de: []
---

# Glossário e Linguagem Ubíqua

## 1. Regra de idioma (obrigatória)

| Camada | Idioma | Motivo |
|---|---|---|
| **Identificadores de código** (classes, métodos, variáveis, arquivos, pastas) | **Inglês** | O contrato de API já publicado usa inglês (`budget_limit`, `items_to_buy`, `sku`, `quantity`); misturar idiomas no código gera `necessidade_reposicao` conversando com `items_to_buy` |
| **Campos de API (JSON) e tipos TypeScript** | **Inglês** | Contrato já fechado em `00-arquitetura-tecnica/contratos_de_api.md` |
| **Documentação, docstrings, comentários, mensagens de commit, textos de UI** | **Português** | Entrega acadêmica e banca avaliadora são em português |

**Proibido:** nomes híbridos (`calcular_fitness`, `PurchasePlanRepositorio`, `qtd_necessaria`). **Proibido:** abreviar (regra 6 de Object Calisthenics) — use `quantity`, nunca `qty`; `population`, nunca `pop`.

## 2. Dicionário PT-BR → código

| Termo de negócio (PT-BR) | Identificador no código | Tipo | Definição curta |
|---|---|---|---|
| Produto / SKU | `Sku` | Value Object | Identificador único do item de catálogo |
| Preço unitário de compra | `UnitPrice` | Value Object | Custo de uma unidade; nesta PoC usa-se o `preco` do dataset |
| Dinheiro / orçamento em reais | `Money` | Value Object | Valor monetário armazenado em **centavos inteiros** |
| Quantidade (unidades) | `Quantity` | Value Object | Inteiro não-negativo de unidades |
| Estoque atual | `StockOnHand` | Value Object | Unidades disponíveis na data de referência |
| Saídas em 7 dias | `weekly_outflow` | feature | Consumo da última semana |
| Saídas em 30 dias | `monthly_outflow` | feature | Consumo dos últimos 30 dias |
| Promoção (0/1) | `promotion_flag` | feature | Indicador binário de promoção ativa |
| Demanda futura (alvo do modelo) | `future_demand` | alvo de ML | Unidades previstas para os próximos 7 dias |
| Demanda semanal prevista | `WeeklyDemandForecast` | Value Object | Saída do modelo, por produto, arredondada e ≥ 1 |
| Ciclo de reposição (4 semanas) | `ReplenishmentCycle` | Value Object | Horizonte de cobertura desejado |
| Demanda do ciclo | `cycle_demand` | cálculo | `demanda semanal prevista × semanas do ciclo` |
| Necessidade de reposição (líquida) | `RequiredQuantity` | Value Object | `max(0, demanda do ciclo − estoque atual)` |
| Cenário de reposição | `ReplenishmentScenario` | First-class collection | Conjunto de itens com preço e necessidade |
| Item do cenário | `ReplenishmentItem` | Entity | Um produto do cenário (catálogo + necessidade) |
| Plano de compra / indivíduo / cromossomo | `PurchasePlan` | First-class collection | Vetor de quantidades a comprar, uma por item |
| Gene | posição em `PurchasePlan` | — | Quantidade de um produto específico |
| População | `Population` | First-class collection | Conjunto de `PurchasePlan` de uma geração |
| Geração | `GenerationNumber` | Value Object | Índice da iteração evolutiva |
| Função de aptidão / fitness | `FitnessPolicy` (porta) / `FitnessScore` (VO) | Protocol + VO | Pontuação de um plano de compra |
| Pesos do fitness | `FitnessWeights` | Value Object | Os multiplicadores (10 e 5) configuráveis |
| Operador de reparo / ajuste ao orçamento | `PlanRepair` (porta) | Protocol | Torna um plano viável (necessidade + orçamento) |
| Orçamento máximo | `BudgetConstraint` | Value Object | Teto de gasto do plano |
| Demanda atendida (%) | `served_ratio` | indicador | `100 × unidades compradas ÷ unidades necessárias` |
| Produtos em risco | `items_at_risk` | indicador | Itens que seguem com necessidade não coberta |
| Saldo de risco | `uncovered_quantity` | indicador | Unidades que faltaram por item |
| Relatório de cobertura | `CoverageReport` | Value Object | Agrupa `served_ratio` + `items_at_risk` |
| Solução ingênua / baseline | `NaiveReplenishmentPolicy` | Strategy | Divide o orçamento igualmente entre produtos |
| Elitismo | `EliteSize` | Value Object | Quantos melhores sobrevivem intactos |
| Classificação de risco de estoque | `StockRiskLevel` | Enum | `SHORTAGE` / `ADEQUATE` / `EXCESS` |
| Possível falta | `StockRiskLevel.SHORTAGE` | Enum member | Estoque abaixo da demanda prevista |
| Possível excesso | `StockRiskLevel.EXCESS` | Enum member | Estoque acima de 1,8 × demanda prevista |
| Adequado | `StockRiskLevel.ADEQUATE` | Enum member | Demais casos |
| Tarefa de otimização | `OptimizationTask` | Entity | Execução assíncrona identificada por `task_id` |

## 3. Nomes do notebook → nomes do código

Mapa direto para quem estiver portando as células do notebook (coluna da esquerda = nome original em `Projeto_Preditivo.ipynb`).

| Notebook | Código |
|---|---|
| `estoque_atual` | `stock_on_hand` |
| `saidas_7_dias` | `weekly_outflow` |
| `saidas_30_dias` | `monthly_outflow` |
| `preco` | `unit_price` |
| `promocao` | `promotion_flag` |
| `demanda_futura` | `future_demand` |
| `demanda_prevista_semanal` | `forecast_weekly_demand` |
| `demanda_do_ciclo` | `cycle_demand` |
| `necessidade_reposicao` | `required_quantity` |
| `ORCAMENTO` | `budget_limit` |
| `SEMANAS_DO_CICLO` | `cycle_weeks` |
| `TAMANHO_POPULACAO` | `population_size` |
| `GERACOES` | `generations` |
| `TAXA_MUTACAO` | `mutation_rate` |
| `ajustar_ao_orcamento()` | `PlanRepair.repair()` |
| `avaliar()` | `FitnessPolicy.evaluate()` |
| `criar_individuo()` | `PlanFactory.random_plan()` |
| `cruzar()` | `CrossoverStrategy.combine()` |
| `mutar()` | `MutationStrategy.mutate()` |
| `solucao_ingenua()` | `NaiveReplenishmentPolicy.build_plan()` |
| `melhor_por_geracao` | `EvolutionResult.history` |
| `percentual_atendido` | `served_ratio` |
| `produtos_em_risco` | `items_at_risk` |
| `saldo_de_risco` | `uncovered_quantity` |

## 4. Termos que **não** devem aparecer no código

| Termo | Por quê | Use em vez disso |
|---|---|---|
| `lucro` / `profit` | O fitness desta PoC **não** otimiza lucro — não existe margem nem preço de venda no dataset. Ver `04-decisoes-e-roadmap/01-divergencias-e-decisoes.md` (D-01) | `served_ratio`, `coverage` |
| `solucao` | Ambíguo (solução de quê?) | `PurchasePlan` |
| `individuo` / `cromossomo` no domínio | Vocabulário do algoritmo, não do negócio; fica restrito ao módulo do AG | `PurchasePlan` |
| `data`, `info`, `manager`, `helper`, `util` | Nomes vazios; violam a regra 6 de Object Calisthenics | Nome do conceito real |
