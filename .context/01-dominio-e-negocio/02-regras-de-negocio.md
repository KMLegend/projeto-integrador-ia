---
id: 02-regras-de-negocio
dominio: dominio-e-negocio
palavras-chave: regras de negocio, ciclo de reposicao, necessidade liquida, risco de estoque, invariantes, dominio
fonte-da-verdade: Projeto_Preditivo.ipynb (Entregavel 03 secao 4; Entregavel 04 secoes 2 e 3)
depende-de: [01-glossario-e-linguagem-ubiqua, 03-previsao-de-demanda]
---

# Regras de Negócio

Todas as regras abaixo são **determinísticas** e devem viver na camada `domain`, sem nenhum import de framework, numpy, pandas, sklearn, Redis ou Pydantic.

---

## RN-01 — Ciclo de reposição

O gestor compra para cobrir **4 semanas** de consumo.

```
cycle_demand(produto) = forecast_weekly_demand(produto) × cycle_weeks
cycle_weeks = 4   (padrão; configurável por requisição)
```

* `cycle_weeks` é parâmetro de configuração, **não** constante mágica — deve ser um Value Object `ReplenishmentCycle` recebido por injeção.
* Invariante: `cycle_weeks ≥ 1`. Valor fora disso → `InvalidCycleError`.

## RN-02 — Demanda semanal prevista

A previsão vem do modelo de ML já treinado (ver `03-previsao-de-demanda.md`) e passa por duas normalizações **nesta ordem**:

```
forecast_weekly_demand = max(1, round(predicao_do_modelo))
```

* `round` é o arredondamento half-to-even do Python/NumPy (o notebook usa `np.round`).
* O piso de 1 unidade existe porque demanda prevista zero ou negativa não tem significado operacional.
* Invariante: `forecast_weekly_demand ≥ 1`.

## RN-03 — Necessidade líquida de reposição

```
required_quantity(produto) = max(0, cycle_demand(produto) − stock_on_hand(produto))
```

* Produto com estoque suficiente para o ciclo tem necessidade **0** e nunca entra no plano de compra.
* Invariante: `required_quantity ≥ 0`, sempre inteiro.
* Consequência de projeto: itens com necessidade 0 permanecem no cenário (para aparecerem no relatório com quantidade 0), mas são irrelevantes para o fitness.

## RN-04 — Teto de compra por produto

Nunca se compra mais do que a necessidade líquida:

```
0 ≤ purchase_quantity(produto) ≤ required_quantity(produto)
```

* Justificativa de negócio: comprar acima da necessidade do ciclo cria excesso de estoque — exatamente o custo que o sistema existe para evitar.
* Essa invariante é garantida pelo operador de reparo (`PlanRepair`), detalhado em `04-funcao-fitness.md`.

## RN-05 — Restrição orçamentária

```
total_cost(plano) = Σ (purchase_quantity(i) × unit_price(i)) ≤ budget_limit
```

* `budget_limit` vem da requisição do usuário (`budget_limit` no payload do `POST /api/v1/optimize`).
* Invariante: `budget_limit > 0`.
* **Nenhum plano inviável pode ser pontuado.** O reparo roda antes de qualquer avaliação de fitness.
* Aritmética monetária é feita em **centavos inteiros** (`Money`), nunca em `float`. Ver decisão D-03 em `04-decisoes-e-roadmap/01-divergencias-e-decisoes.md`.

## RN-06 — Classificação de risco de estoque (Entregável 03)

Regra de leitura rápida para o gestor, independente do AG:

| Condição | `StockRiskLevel` | Rótulo na UI |
|---|---|---|
| `stock_on_hand < forecast_weekly_demand` | `SHORTAGE` | Possível falta |
| `stock_on_hand > forecast_weekly_demand × 1.8` | `EXCESS` | Possível excesso |
| demais casos | `ADEQUATE` | Adequado |

* O limiar `1.8` é um **parâmetro de política**, não constante no meio do código: `StockRiskThresholds(excess_multiplier=1.8)`.
* A ordem de avaliação importa: testa-se `SHORTAGE` primeiro, depois `EXCESS`, e o padrão é `ADEQUATE` (mesma semântica do `np.select` do notebook).
* Implementar **sem `else`** (regra 2 de Object Calisthenics): lista ordenada de regras + `next(...)` com padrão, ou dispatch por predicado. Exemplo canônico em `02-padroes-de-engenharia/02-object-calisthenics.md`.

## RN-07 — Indicadores de um plano de compra

Calculados sempre sobre um plano **já reparado**:

| Indicador | Fórmula | Observação |
|---|---|---|
| `total_cost` | `Σ quantity(i) × unit_price(i)` | em `Money` |
| `served_quantity` | `Σ min(quantity(i), required_quantity(i))` | após o reparo, `min` é defensivo: `quantity ≤ required` já vale por RN-04 |
| `required_total` | `Σ required_quantity(i)` | denominador da cobertura |
| `served_ratio` | `100 × served_quantity ÷ required_total` | **se `required_total == 0`, vale `100`** |
| `items_at_risk` | `count(quantity(i) < required_quantity(i))` | itens com necessidade 0 nunca contam |
| `uncovered_quantity(i)` | `required_quantity(i) − quantity(i)` | por item, para o relatório |
| `budget_usage_ratio` | `100 × total_cost ÷ budget_limit` | só para exibição |

## RN-08 — Determinismo e reprodutibilidade

* Toda execução do AG recebe uma **semente** (`random_seed`, padrão `42`) e deve produzir exatamente o mesmo resultado para a mesma entrada.
* Nenhuma chamada direta a `random` ou `numpy.random` fora do adaptador `RandomSource` (porta declarada no domínio). Isso é o que permite testar o AG.
* `datetime.now()` também não é chamado no domínio: injetar um `Clock`.

## RN-09 — Escopo honesto desta PoC

Registrar nos relatórios e na UI, porque a banca vai perguntar:

* Dataset é **simulado** (120 registros, semente 42); não há dado real de ERP.
* `unit_price` é usado tanto como preço de venda (feature do modelo) quanto como custo unitário de compra (otimização) — simplificação acadêmica explícita do notebook.
* O fitness **não** modela lucro, margem, lead time, validade (shelf-life), descontos por volume ou espaço de armazenagem. Esses são os ganchos de evolução futura (ver `04-decisoes-e-roadmap/02-roadmap-de-implantacao.md`, fase 6).

---

## Invariantes agregadas (checklist de revisão)

Uma implementação correta satisfaz **todas** estas afirmações, verificáveis por teste:

1. `cycle_weeks ≥ 1` e `budget_limit > 0` são validados na borda (Pydantic) **e** no domínio (Value Object).
2. Nenhum `purchase_quantity` é negativo.
3. Nenhum `purchase_quantity` excede o `required_quantity` do seu item.
4. `total_cost ≤ budget_limit` para todo plano avaliado, criado, cruzado ou mutado.
5. `0 ≤ served_ratio ≤ 100`.
6. `0 ≤ items_at_risk ≤ número de itens com necessidade > 0`.
7. Duas execuções com a mesma entrada e mesma semente retornam planos idênticos.
8. Nenhum módulo em `domain/` importa `numpy`, `pandas`, `sklearn`, `celery`, `redis`, `fastapi` ou `pydantic`.
