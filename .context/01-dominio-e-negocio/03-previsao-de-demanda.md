---
id: 03-previsao-de-demanda
dominio: dominio-e-negocio
palavras-chave: machine learning, regressao linear, previsao de demanda, features, MAE, sklearn, dataset sintetico, forecasting
fonte-da-verdade: Projeto_Preditivo.ipynb (Entregaveis 02 e 03)
depende-de: [01-glossario-e-linguagem-ubiqua, 02-regras-de-negocio]
---

# Previsão de Demanda (Machine Learning Clássico)

Módulo que transforma histórico de estoque em **demanda semanal prevista por produto**. É a entrada do algoritmo genético.

---

## 1. Formulação do problema

* **Tipo:** regressão supervisionada (o alvo é quantidade contínua, não categoria).
* **Modelo:** `sklearn.linear_model.LinearRegression` (mínimos quadrados ordinários).
* **Alvo (`y`):** `future_demand` — unidades previstas para os próximos 7 dias.
* **Métrica:** MAE (`mean_absolute_error`), porque mantém a unidade física do negócio ("erra ~5 unidades").
* **Por que linear e não XGBoost/rede neural:** a entrega exige prova de conceito auditável e interpretável (coeficientes explicáveis à banca). Trocar o modelo depois **não deve exigir mudança em nenhuma outra camada** — é exatamente o que a porta `DemandForecaster` garante (OCP + DIP).

## 2. Features (fixas — 5, definidas no Entregável 02)

A ordem das colunas é **parte do contrato** do modelo serializado: alterá-la invalida um modelo já treinado.

| # | Feature (código) | Coluna no notebook | Tipo | Justificativa de negócio |
|---|---|---|---|---|
| 1 | `stock_on_hand` | `estoque_atual` | int ≥ 0 | Disponibilidade na data de referência |
| 2 | `weekly_outflow` | `saidas_7_dias` | int ≥ 0 | Ritmo imediato de consumo |
| 3 | `monthly_outflow` | `saidas_30_dias` | int ≥ 0 | Tendência mensal, mais estável |
| 4 | `unit_price` | `preco` | float > 0 | Elasticidade da demanda ao preço |
| 5 | `promotion_flag` | `promocao` | 0 ou 1 | Aceleração promocional das vendas |

`reference_date` e `product` são **identificadores**, não features.

> **Implementação obrigatória:** a lista ordenada vive em um único lugar (`FeatureSchema.ORDERED_NAMES`) e é reutilizada no treino, na inferência e na validação de entrada. Duplicar essa lista é bug esperando acontecer.

## 3. Pipeline de treinamento

```
dataset (120 registros) → split 80/20 (random_state=42) → fit(X_treino, y_treino)
                                                        → predict(X_teste) → MAE
```

* **Split:** `train_test_split(X, y, test_size=0.20, random_state=42)` → 96 treino / 24 teste.
* **Semente:** `42` em todo o pipeline, para a demonstração ser reproduzível ao vivo.
* **Resultado de referência do notebook:** **MAE = 4,76 unidades**.
* **Sem normalização/scaling:** regressão linear por mínimos quadrados não exige, e a ausência mantém os coeficientes interpretáveis na escala original.
* **Sem validação cruzada** nesta PoC (está no roadmap, fase 6).

## 4. Dataset sintético (gerador reproduzível)

Não há dado real de ERP. O gerador deve reproduzir a lógica do notebook **exatamente**, porque o MAE de referência depende dela.

**Catálogo base** (produto, saída semanal típica, preço normal):

| Produto | `baseline_weekly_outflow` | `baseline_price` |
|---|---|---|
| Café 500g | 68 | 18.90 |
| Arroz 5kg | 50 | 29.90 |
| Feijão 1kg | 48 | 9.49 |
| Leite UHT 1L | 100 | 5.79 |
| Detergente 500ml | 30 | 3.39 |
| Refrigerante 2L | 78 | 10.49 |

**Grade temporal:** 20 semanas a partir de `2026-02-18`, passo de 7 dias → 6 produtos × 20 semanas = **120 registros**.

**Fórmulas por registro** (semente global `np.random.seed(42)`, draws na ordem exata abaixo):

```
promotion_flag = 1 se random() < 0.20 senao 0
seasonality    = 1 + 0.08 × sin(2π × indice_da_semana / 10)
unit_price     = round(baseline_price × (0.90 se promocao senao 1) × normal(1, 0.01), 2)
weekly_outflow = max(1, round(baseline_weekly_outflow × seasonality × (1.15 se promocao senao 1) + normal(0, 4)))
monthly_outflow= max(weekly_outflow, round(weekly_outflow × 4 + normal(0, 10)))
stock_on_hand  = max(0, round(weekly_outflow × uniform(2, 6)))

future_demand  = max(1, round(
      0.55 × weekly_outflow
    + 0.35 × (monthly_outflow / 4)
    + 0.10 × baseline_weekly_outflow × promotion_flag
    + 0.15 × baseline_weekly_outflow × (baseline_price − unit_price) / baseline_price
    + normal(0, 5)
))
```

* A ordem dos sorteios aleatórios **não pode mudar** — alterá-la muda todo o dataset.
* O gerador é **infraestrutura**, não domínio: vive em `infrastructure/dataset/`.
* Ele implementa a mesma porta de leitura que um futuro `CsvStockHistoryRepository` ou conector de ERP — trocar simulado por real é trocar o adaptador registrado no container de injeção.

## 5. Da previsão ao cenário de otimização

Esta é a ponte Entregável 03 → Entregável 04. **O modelo não é retreinado** nesta etapa.

```
1. Pegar o último registro de cada produto (ordenado por reference_date)
2. forecast_weekly_demand = max(1, round(modelo.predict(features_do_ultimo_registro)))
3. cycle_demand      = forecast_weekly_demand × 4                     (RN-01)
4. required_quantity = max(0, cycle_demand − stock_on_hand)           (RN-03)
5. Ordenar os itens por nome de produto (ordem estável e determinística)
6. Montar ReplenishmentScenario com (sku, unit_price, required_quantity)
```

**Cenário de referência produzido pelo notebook** (usar como fixture de teste — ver `06-baseline-e-indicadores.md`):

| Produto | `stock_on_hand` | `unit_price` | `forecast_weekly_demand` | `cycle_demand` | `required_quantity` |
|---|---|---|---|---|---|
| Arroz 5kg | 201 | 29.89 | 42 | 168 | 0 |
| Café 500g | 192 | 18.78 | 60 | 240 | **48** |
| Detergente 500ml | 202 | 3.07 | 39 | 156 | 0 |
| Feijão 1kg | 270 | 9.55 | 46 | 184 | 0 |
| Leite UHT 1L | 226 | 5.86 | 81 | 324 | **98** |
| Refrigerante 2L | 263 | 10.76 | 65 | 260 | 0 |

Total necessário: **146 unidades**; custo para atender 100%: **R$ 1.475,72**; orçamento disponível: **R$ 1.000,00** → déficit de R$ 475,72. É esse déficit que justifica o AG.

## 6. Ciclo de vida do modelo treinado

Requisito de containerização: o worker **não pode retreinar o modelo em cada tarefa Celery**.

* Artefato: `joblib` salvo em `MODEL_STORE_PATH` (volume Docker compartilhado entre `api_backend` e `celery_worker`).
* Carregamento **lazy com cache em processo**: o primeiro uso no worker carrega do disco; se o arquivo não existir, treina, persiste e segue.
* Pré-aquecimento explícito: serviço one-shot `model_trainer` no Compose (profile `tools`) — ver `03-implementacao/04-docker-e-infraestrutura.md`.
* O artefato persistido guarda, junto do modelo: ordem das features, semente, MAE de treino e versão do schema. Um artefato com schema incompatível é descartado e retreinado, nunca usado às cegas.

## 7. Porta do domínio (contrato)

O domínio conhece **só isto** sobre previsão — nada de sklearn, pandas ou joblib:

```python
# domain/ports/demand_forecaster.py
from typing import Protocol
from domain.model.stock_snapshot import StockSnapshots
from domain.model.weekly_demand import WeeklyDemandForecasts

class DemandForecaster(Protocol):
    def forecast(self, snapshots: StockSnapshots) -> WeeklyDemandForecasts:
        """Devolve a demanda semanal prevista para cada produto do histórico."""
        ...
```

Implementações possíveis (todas em `infrastructure/forecasting/`), sem nenhuma mudança no domínio:

| Implementação | Uso |
|---|---|
| `LinearRegressionDemandForecaster` | Produção desta PoC |
| `CachedDemandForecaster` | Decorator: memoiza por `Sku` (padrão Decorator, OCP) |
| `FixedDemandForecaster` | Testes: devolve valores constantes, sem sklearn |

## 8. Critérios de aceite do módulo

1. `LinearRegressionDemandForecaster` treina com o dataset sintético e atinge **MAE ≤ 6,0** unidades (margem sobre o 4,76 de referência, tolerante a variação de versão de biblioteca).
2. Toda previsão devolvida é inteira e `≥ 1`.
3. O domínio não importa `sklearn`/`pandas`/`numpy` (verificado por `import-linter` no CI).
4. `FixedDemandForecaster` permite rodar **todos** os testes de domínio e de caso de uso sem sklearn instalado.
5. Duas execuções com a mesma semente produzem o mesmo dataset e o mesmo MAE.
6. A classificação de risco de RN-06 é aplicável a qualquer previsão (testada nos três níveis).
