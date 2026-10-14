---
id: 04-funcao-fitness
dominio: dominio-e-negocio
palavras-chave: fitness, funcao de aptidao, avaliar, reparo, ajustar ao orcamento, penalidade, pesos, cobertura, viabilidade
fonte-da-verdade: Projeto_Preditivo.ipynb (Entregavel 04, celulas `ajustar_ao_orcamento` e `avaliar`)
depende-de: [02-regras-de-negocio, 05-algoritmo-genetico, 06-baseline-e-indicadores]
---

# Função de Fitness e Operador de Reparo

Este é o **coração da regra de negócio** da otimização. A fórmula abaixo é normativa: a implementação precisa reproduzir os valores-ouro de `06-baseline-e-indicadores.md` exatamente.

---

## 1. O que o fitness mede

> Dado um orçamento limitado, **qual plano de compra cobre a maior parte da necessidade de reposição deixando o menor número de produtos desabastecidos?**

Duas forças, em ordem de importância:

1. **Cobertura (recompensa principal):** percentual da necessidade total atendido em unidades.
2. **Dispersão do risco (penalidade secundária):** cada produto que segue com necessidade não coberta tira pontos.

A penalidade existe para desempatar: entre dois planos que cobrem as mesmas unidades totais, o sistema prefere o que **concentra** a cobertura e deixa menos produtos na prateleira vazia. Em varejo, um produto zerado custa cliente perdido, independentemente de quantas unidades faltaram.

## 2. Fórmula normativa

```
fitness = served_ratio × coverage_weight − items_at_risk × risk_penalty_weight

coverage_weight    = 10   (padrão)
risk_penalty_weight = 5   (padrão)
```

Com:

```
served_quantity = Σ min(quantity(i), required_quantity(i))
required_total  = Σ required_quantity(i)
served_ratio    = 100 × served_quantity / required_total        se required_total > 0
                = 100                                           se required_total == 0
items_at_risk   = count( quantity(i) < required_quantity(i) )
```

**Pré-condição absoluta:** o fitness só é calculado sobre um plano **já reparado** (seção 3). Pontuar plano inviável é bug de severidade alta — um plano que estoura o orçamento pode "ganhar" a evolução e produzir recomendação impossível de executar.

### Propriedades (úteis em teste e na defesa oral)

| Propriedade | Valor |
|---|---|
| Fitness máximo teórico | `1000` (cobertura 100%, zero produtos em risco) |
| Fitness mínimo | `0 − 5 × n_itens_com_necessidade` (plano vazio) |
| Monotonicidade | Comprar uma unidade a mais de um item com necessidade **nunca** reduz o fitness |
| Pureza | Função pura de `(plano, cenário, pesos)`; sem I/O, sem aleatoriedade, sem relógio |
| Escala | `served_ratio` em pontos percentuais (0–100), **não** em fração (0–1) |

### Casos de borda (todos precisam de teste)

| Situação | Comportamento exigido |
|---|---|
| `required_total == 0` (nada a comprar) | `served_ratio = 100`, `items_at_risk = 0`, `fitness = 1000` |
| Item com `required_quantity == 0` | Nunca conta como em risco (`0 < 0` é falso) |
| Plano todo zero com necessidade existente | `served_ratio = 0`, `fitness = −5 × n_itens_com_necessidade` |
| Orçamento menor que o item mais barato | Plano viável é o plano zero; não lançar exceção |
| Cenário vazio (nenhum item) | `fitness = 1000`; não dividir por zero |
| Empate de fitness | Resolvido pela política de ordenação do AG (ver `05-algoritmo-genetico.md`), **não** pelo fitness |

## 3. Operador de reparo (`PlanRepair`) — torna o plano viável

Equivalente ao `ajustar_ao_orcamento` do notebook. É o que mantém a população sempre dentro das restrições RN-04 e RN-05, em vez de penalizar inviabilidade no fitness.

**Algoritmo (normativo, nesta ordem):**

```
1. CLAMP:  quantity(i) ← min( max(quantity(i), 0), required_quantity(i) )   para todo i
2. ENQUANTO total_cost(plano) > budget_limit:
     2.1. candidatos ← { i : quantity(i) > 0 }
     2.2. se candidatos vazio: interromper   (orçamento menor que qualquer unidade)
     2.3. i* ← candidato de MAIOR unit_price (empate: menor índice)
     2.4. quantity(i*) ← quantity(i*) − 1
3. devolver plano
```

**Por que remover a unidade mais cara:** cada unidade removida custa exatamente 1 unidade de cobertura, independentemente do preço. Remover a mais cara libera o máximo de orçamento pelo mínimo de cobertura perdida — o reparo é, portanto, *coverage-efficient*, e não um ajuste arbitrário. Vale dizer isso à banca.

**Consequências de projeto:**

* Depois do reparo, `quantity(i) ≤ required_quantity(i)` sempre vale, então `min(...)` no `served_quantity` é defensivo (mantenha-o: protege contra chamada indevida de fitness sem reparo).
* O reparo é aplicado em **quatro** pontos: criação do indivíduo, crossover, mutação e qualquer plano vindo de fora (ex.: baseline). Centralize numa única implementação.
* O laço de remoção é `O(unidades removidas × n_itens)`. Para 6 itens é irrelevante. Com centenas de SKUs, substituir por remoção em lote (calcular quantas unidades do item mais caro cabem de uma vez) — **mesmo resultado**, outra complexidade; é uma troca legítima de `PlanRepair` sob OCP, e precisa de teste de equivalência com a versão ingênua.

## 4. Separação de responsabilidades (SRP)

Quatro responsabilidades distintas, quatro objetos. Não as funda num `avaliar()` monolítico como no notebook:

| Responsabilidade | Objeto | Camada |
|---|---|---|
| Tornar o plano viável | `BudgetAwarePlanRepair` (implementa `PlanRepair`) | `domain/policy/` |
| Calcular indicadores de cobertura | `CoverageCalculator` → `CoverageReport` | `domain/model/` |
| Converter indicadores em pontuação | `WeightedFitnessPolicy` (implementa `FitnessPolicy`) | `domain/policy/` |
| Guardar os pesos | `FitnessWeights` (Value Object) | `domain/model/` |

O AG depende **apenas** da `Protocol` `FitnessPolicy` — nunca da implementação concreta (DIP).

## 5. Contratos de código

```python
# domain/ports/fitness_policy.py
from typing import Protocol
from domain.model.purchase_plan import PurchasePlan
from domain.model.replenishment_scenario import ReplenishmentScenario
from domain.model.plan_assessment import PlanAssessment

class FitnessPolicy(Protocol):
    def evaluate(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PlanAssessment:
        """Pontua um plano JA REPARADO. Funcao pura."""
        ...


# domain/ports/plan_repair.py
class PlanRepair(Protocol):
    def repair(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        """Devolve um plano viavel: respeita a necessidade de cada item e o orcamento."""
        ...
```

```python
# domain/model/fitness_weights.py
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class FitnessWeights:
    coverage: float
    risk_penalty: float

    @staticmethod
    def default() -> "FitnessWeights":
        return FitnessWeights(coverage=10.0, risk_penalty=5.0)

    def score(self, coverage_report: "CoverageReport") -> "FitnessScore":
        return FitnessScore(
            coverage_report.served_ratio_points() * self.coverage
            - coverage_report.items_at_risk_count() * self.risk_penalty
        )
```

```python
# domain/policy/weighted_fitness_policy.py
@dataclass(frozen=True, slots=True)
class WeightedFitnessPolicy:
    _coverage_calculator: CoverageCalculator
    _weights: FitnessWeights

    def evaluate(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PlanAssessment:
        coverage_report = self._coverage_calculator.report_for(plan, scenario)
        return PlanAssessment(plan, self._weights.score(coverage_report))
```

Note: 2 atributos de instância por classe, métodos de 1–2 linhas, nenhum `else`, nenhum primitivo cru cruzando fronteira — conforme `02-padroes-de-engenharia/02-object-calisthenics.md`.

```python
# domain/policy/budget_aware_plan_repair.py
@dataclass(frozen=True, slots=True)
class BudgetAwarePlanRepair:
    _budget: BudgetConstraint

    def repair(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        return self._fit_to_budget(plan.clamped_to(scenario.required_quantities()), scenario)

    def _fit_to_budget(self, plan: PurchasePlan, scenario: ReplenishmentScenario) -> PurchasePlan:
        while self._budget.is_exceeded_by(scenario.total_cost_of(plan)):
            most_expensive = scenario.most_expensive_position_among(plan.non_empty_positions())
            if most_expensive.is_absent():
                return plan
            plan = plan.decremented_at(most_expensive.value())
        return plan
```

> O `if` com `return` antecipado é permitido (guard clause); o proibido é `else`. `most_expensive` devolve um `Optional`-like explícito (`Maybe`/`Position`) para não vazar `None` cru.

## 6. Extensões previstas (OCP — adicione classe, não `if`)

Implementações alternativas de `FitnessPolicy`, todas plugáveis sem tocar no AG. **A política padrão continua sendo `WeightedFitnessPolicy` com pesos 10/5** — qualquer outra é opt-in via configuração, porque mudar o padrão invalida os números apresentados à banca.

| Política | Comportamento | Quando |
|---|---|---|
| `CostTieBreakingFitnessPolicy` | Desempata planos de cobertura igual preferindo o mais barato (subtrai ε × custo) | Se o gestor quiser economizar sobras de orçamento |
| `ServiceLevelFitnessPolicy` | Penaliza por unidade descoberta, não por produto | Se faltar 1 unidade for muito diferente de faltar 90 |
| `MarginAwareFitnessPolicy` | Introduz margem/lucro no objetivo | Só quando houver preço de venda no dataset (ver D-01) |
| `ShelfLifeAwareFitnessPolicy` | Penaliza compra acima do giro para itens perecíveis | Fase 6 do roadmap |

## 7. Checklist de aceite do fitness

1. Reproduz **236,58** para o plano baseline `[0, 8, 0, 0, 28, 0]` no cenário de referência.
2. Reproduz **816,92** para o plano ótimo `[0, 22, 0, 0, 98, 0]`.
3. Devolve **1000** para cenário sem necessidade alguma.
4. É função pura: 1.000 chamadas com a mesma entrada devolvem o mesmo `FitnessScore`.
5. Nunca pontua plano inviável — teste que injeta plano acima do orçamento diretamente no fitness e verifica que o caso de uso repara antes.
6. Os pesos 10/5 **não** aparecem hardcoded fora de `FitnessWeights.default()`.
7. Após `repair`, as invariantes 2, 3 e 4 de `02-regras-de-negocio.md` valem para qualquer plano aleatório (teste de propriedade com 1.000 planos sorteados).
