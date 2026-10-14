---
id: 06-baseline-e-indicadores
dominio: dominio-e-negocio
palavras-chave: baseline, solucao ingenua, indicadores, KPI, valores ouro, golden values, fixture, comparacao, validacao
fonte-da-verdade: Projeto_Preditivo.ipynb (Entregavel 04, secoes 4, 6 e 7)
depende-de: [04-funcao-fitness, 05-algoritmo-genetico]
---

# Baseline, Indicadores e Valores-Ouro

Este documento é a **referência de verificação** do sistema: todos os números aqui foram produzidos pelo notebook e conferidos manualmente. Qualquer implementação que não os reproduza está errada.

---

## 1. Solução ingênua (baseline obrigatório)

Serve para provar que o AG agrega valor. **Não é opcional** — a comparação é parte do entregável.

**Regra:** divide o orçamento igualmente entre todos os produtos; em cada um, compra o máximo que cabe na sua parcela, sem passar da necessidade.

```
share_per_item = budget_limit / numero_de_itens
quantity(i)    = floor( share_per_item / unit_price(i) )
devolver repair(plano)          # mesmo operador de reparo do AG
```

* Em `Money` (centavos inteiros): `share_per_item = budget_limit_cents // numero_de_itens` e `quantity(i) = share_per_item // unit_price_cents(i)` — divisão inteira produz o mesmo resultado do `floor` em float.
* O reparo final é o que zera itens sem necessidade.
* Implementar como `NaiveReplenishmentPolicy`, atrás da mesma porta de "política de plano" do AG, para que o caso de uso de comparação não saiba qual é qual (LSP).

**Defeito que a baseline expõe (narrativa da apresentação):** ela reserva orçamento para Arroz, Feijão, Detergente e Refrigerante, que não precisavam de compra, e por isso gasta só R$ 314,32 dos R$ 1.000,00 — deixando o cliente sem leite e sem café.

## 2. Cenário de referência (fixture canônica)

Salvar **exatamente** este conteúdo em `backend/tests/fixtures/reference_scenario.json` e usá-lo em todos os testes de valor-ouro. A fixture é estática de propósito: ela não depende de reproduzir a sequência de números aleatórios do dataset sintético, o que tornaria os testes frágeis a mudanças de versão de NumPy.

```json
{
  "budget_limit": "1000.00",
  "cycle_weeks": 4,
  "items": [
    {"sku": "ARROZ-5KG",        "product": "Arroz 5kg",        "unit_price": "29.89", "stock_on_hand": 201, "forecast_weekly_demand": 42, "required_quantity": 0},
    {"sku": "CAFE-500G",        "product": "Café 500g",        "unit_price": "18.78", "stock_on_hand": 192, "forecast_weekly_demand": 60, "required_quantity": 48},
    {"sku": "DETERGENTE-500ML", "product": "Detergente 500ml", "unit_price": "3.07",  "stock_on_hand": 202, "forecast_weekly_demand": 39, "required_quantity": 0},
    {"sku": "FEIJAO-1KG",       "product": "Feijão 1kg",       "unit_price": "9.55",  "stock_on_hand": 270, "forecast_weekly_demand": 46, "required_quantity": 0},
    {"sku": "LEITE-UHT-1L",     "product": "Leite UHT 1L",     "unit_price": "5.86",  "stock_on_hand": 226, "forecast_weekly_demand": 81, "required_quantity": 98},
    {"sku": "REFRIGERANTE-2L",  "product": "Refrigerante 2L",  "unit_price": "10.76", "stock_on_hand": 263, "forecast_weekly_demand": 65, "required_quantity": 0}
  ]
}
```

Derivados do cenário:

| Grandeza | Valor |
|---|---|
| Itens no cenário | 6 |
| Itens com necessidade > 0 | 2 (Café, Leite) |
| Necessidade total | **146 unidades** |
| Custo para atender 100% | **R$ 1.475,72** (48 × 18,78 + 98 × 5,86) |
| Orçamento | **R$ 1.000,00** |
| Déficit orçamentário | **R$ 475,72** |

## 3. Valores-ouro (testes de regressão)

### 3.1 Baseline — plano `[0, 8, 0, 0, 28, 0]`

| Indicador | Valor exato | Como conferir |
|---|---|---|
| `total_cost` | **R$ 314,32** | 8 × 18,78 + 28 × 5,86 = 150,24 + 164,08 |
| `served_quantity` | **36** unidades | 8 + 28 |
| `served_ratio` | **24,6575…%** | 100 × 36 / 146 |
| `items_at_risk` | **2** | Café (8 < 48) e Leite (28 < 98) |
| `fitness` | **236,5753…** | 24,6575 × 10 − 2 × 5 |

Arredondado para exibição: custo R$ 314,32 · cobertura 24,7% · risco 2 · fitness 236,58.

### 3.2 Otimizado (AG, semente 42) — plano `[0, 22, 0, 0, 98, 0]`

| Indicador | Valor exato | Como conferir |
|---|---|---|
| `total_cost` | **R$ 987,44** | 22 × 18,78 + 98 × 5,86 = 413,16 + 574,28 |
| `served_quantity` | **120** unidades | 22 + 98 |
| `served_ratio` | **82,1917…%** | 100 × 120 / 146 |
| `items_at_risk` | **1** | só Café (22 < 48) |
| `fitness` | **816,9178…** | 82,1917 × 10 − 1 × 5 |
| `budget_usage_ratio` | **98,7%** | 987,44 / 1000 |
| `history[0]` | **777,67** | melhor da população inicial aleatória |
| `history[-1]` | **816,92** | melhor da última geração |

Detalhamento por item do plano ótimo:

| Produto | Necessidade | Comprado | Saldo de risco | Custo |
|---|---:|---:|---:|---:|
| Arroz 5kg | 0 | 0 | 0 | R$ 0,00 |
| Café 500g | 48 | 22 | 26 | R$ 413,16 |
| Detergente 500ml | 0 | 0 | 0 | R$ 0,00 |
| Feijão 1kg | 0 | 0 | 0 | R$ 0,00 |
| Leite UHT 1L | 98 | 98 | 0 | R$ 574,28 |
| Refrigerante 2L | 0 | 0 | 0 | R$ 0,00 |

### 3.3 Este plano é o ótimo global — e isso é testável

Prova (vale citar na defesa): como cada unidade comprada contribui igualmente para a cobertura, maximizar unidades dentro do orçamento é comprar **do mais barato ao mais caro** entre os itens com necessidade. Leite (R$ 5,86) primeiro: 98 unidades = R$ 574,28; restam R$ 425,72 → Café (R$ 18,78): `floor(425,72 / 18,78) = 22` unidades. Total **120 unidades**, custo R$ 987,44. Nenhuma realocação aumenta as unidades (trocar Leite por Café sempre reduz o total, pois Café é mais caro), e a penalidade de risco não muda — com esse orçamento é impossível zerar os dois itens.

**Consequência prática:** implemente um `GreedyCheapestFirstPolicy` em `tests/` (ou como política alternativa) e inclua um teste que afirme `fitness(AG) == fitness(guloso)` no cenário de referência. É a validação mais forte do motor evolutivo — e detecta regressão sutil em qualquer operador.

## 4. Tabela comparativa (saída obrigatória do sistema)

| Indicador | Baseline | AG | Leitura |
|---|---:|---:|---|
| Custo total | R$ 314,32 | **R$ 987,44** | 98,7% do orçamento aproveitado |
| Demanda atendida (un.) | 36 | **120** | +84 unidades |
| Demanda atendida (%) | 24,7% | **82,2%** | +57,5 pontos percentuais |
| Produtos em risco | 2 | **1** | risco reduzido à metade |
| Fitness | 236,58 | **816,92** | +245% de eficácia |

Essa comparação é produzida pelo caso de uso `CompareReplenishmentStrategies` e vai no payload de resposta (ver D-01 em `04-decisoes-e-roadmap/01-divergencias-e-decisoes.md`).

## 5. Tolerâncias numéricas em teste

| Grandeza | Comparação |
|---|---|
| `Money` / custos | **Igualdade exata em centavos** (`Money` é inteiro) |
| `served_ratio`, `fitness` | `pytest.approx(..., abs=1e-4)` |
| MAE do modelo de ML | `<= 6.0` (referência 4,76; margem para versão de biblioteca) |
| Quantidades | Igualdade exata de inteiros |
| Plano do AG com semente fixa | Igualdade exata da tupla de quantidades |

Nunca compare dinheiro com `==` em `float`. O notebook produziu `314.32000000000005` justamente por isso — motivo da decisão D-03 (dinheiro em centavos inteiros).

## 6. Indicadores de UI (KPI cards)

| Card | Campo de origem | Formato |
|---|---|---|
| Orçamento utilizado | `budget_usage_ratio` | `98,7%` + `R$ 987,44 de R$ 1.000,00` |
| Demanda atendida | `served_ratio` | `82,2%` + `120 de 146 un.` |
| Produtos em risco | `items_at_risk` | `1 de 6` |
| Fitness alcançado | `fitness` | `816,92` + delta vs. baseline |
| Erro médio do modelo | `model_mae` | `± 4,76 un./semana` |

Formatação monetária e percentual em **pt-BR** (`Intl.NumberFormat('pt-BR')`): vírgula decimal, ponto de milhar, prefixo `R$`.
