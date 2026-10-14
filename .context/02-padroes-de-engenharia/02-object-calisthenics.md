---
id: 02-object-calisthenics
dominio: padroes-de-engenharia
palavras-chave: object calisthenics, 9 regras, value object, sem else, wrap primitives, first class collections, lei de demeter, getters, classes pequenas
fonte-da-verdade: exigencia explicita do projeto (Jeff Bay, "Object Calisthenics")
depende-de: [01-solid, 03-modularidade-e-fronteiras]
---

# Object Calisthenics adaptado a Python

Exigência **não-negociável** nº 2. As 9 regras valem integralmente em `domain/` e `application/`. Em `infrastructure/` e `api/` valem as exceções **explicitamente listadas** na seção 11 — e só essas.

---

## Regra 1 — Um nível de indentação por método

Um método tem no máximo **um** nível além da assinatura. Mais que isso: extraia método com nome que explique o trecho.

```python
# RUIM — tres niveis
def repair(self, plan, scenario):
    for position in plan.positions():
        if plan.quantity_at(position) > scenario.required_at(position):
            while self._over_budget(plan):
                plan = plan.decremented_at(position)
    return plan

# BOM
def repair(self, plan, scenario):
    return self._fit_to_budget(plan.clamped_to(scenario.required_quantities()), scenario)

def _fit_to_budget(self, plan, scenario):
    while self._budget.is_exceeded_by(scenario.total_cost_of(plan)):
        plan = self._remove_most_expensive_unit(plan, scenario)
    return plan
```

Consequência prática: **métodos de 1 a 5 linhas**.

## Regra 2 — Não use `else`

Proibido: `else`, `elif`, operador ternário usado para desviar fluxo, `match` como substituto disfarçado de cadeia de `if`.

Permitido e preferido:

| Técnica | Quando |
|---|---|
| **Guard clause** (`if ...: return`) | Pré-condição e caso degenerado |
| **Polimorfismo** | A decisão é sobre tipo/estratégia |
| **Null Object** (`NullEvolutionObserver`) | Evitar `if observer is None` |
| **Dict dispatch** | Mapeamento valor → comportamento |
| **Lista ordenada de regras + `next(...)`** | Cadeia de classificação |

Exemplo canônico — classificação de risco (RN-06) sem nenhum `else`:

```python
# domain/policy/stock_risk_classifier.py
@dataclass(frozen=True, slots=True)
class StockRiskClassifier:
    _rules: tuple["StockRiskRule", ...]

    @staticmethod
    def with_thresholds(thresholds: StockRiskThresholds) -> "StockRiskClassifier":
        return StockRiskClassifier((
            ShortageRule(),
            ExcessRule(thresholds),
        ))

    def classify(self, stock: StockOnHand, forecast: WeeklyDemandForecast) -> StockRiskLevel:
        matched = (rule.level() for rule in self._rules if rule.matches(stock, forecast))
        return next(matched, StockRiskLevel.ADEQUATE)
```

A ordem da tupla preserva a precedência do `np.select` do notebook (falta antes de excesso), e adicionar um nível novo de risco é adicionar uma `StockRiskRule` — OCP de graça.

## Regra 3 — Envolva todos os primitivos e strings

Nenhum `int`, `float`, `str` ou `bool` cru atravessa fronteira de domínio. Com `float` isso não é preciosismo: `budget > custo` em float é a origem do `314.32000000000005` do notebook.

| Conceito | Value Object | Encapsula | Comportamento (não getters) |
|---|---|---|---|
| Dinheiro | `Money` | `int` (centavos) | `plus`, `minus`, `times`, `is_greater_than`, `zero` |
| Preço unitário | `UnitPrice` | `Money` | `total_for(Quantity)`, `is_more_expensive_than` |
| Quantidade | `Quantity` | `int ≥ 0` | `plus`, `decremented`, `limited_to`, `is_zero` |
| Identificador | `Sku` | `str` | `value_for_serialization`, `__eq__` |
| Percentual | `Percentage` | `float` | `of(part, whole)`, `points`, `times_weight` |
| Pontuação | `FitnessScore` | `float` | `is_better_than`, `value_for_serialization` |
| Orçamento | `BudgetConstraint` | `Money` | `is_exceeded_by`, `share_among(int)` |
| Ciclo | `ReplenishmentCycle` | `int` semanas | `demand_for(WeeklyDemandForecast)` |
| Geração | `GenerationNumber` | `int` | `next`, `is_multiple_of` |

Todo Value Object: `@dataclass(frozen=True, slots=True)`, **validação no `__post_init__`** (lança exceção de domínio própria), e sem setter.

```python
@dataclass(frozen=True, slots=True)
class Quantity:
    _units: int

    def __post_init__(self) -> None:
        if self._units < 0:
            raise NegativeQuantityError(self._units)

    def limited_to(self, ceiling: "Quantity") -> "Quantity":
        return Quantity(min(self._units, ceiling._units))

    def decremented(self) -> "Quantity":
        return Quantity(max(0, self._units - 1))
```

## Regra 4 — Coleções de primeira classe

Classe que contém coleção **não contém mais nada** e expõe comportamento, não a coleção.

| Coleção | Encapsula | Métodos |
|---|---|---|
| `PurchasePlan` | `tuple[Quantity, ...]` | `clamped_to`, `decremented_at`, `with_quantity_at`, `non_empty_positions`, `total_units` |
| `ReplenishmentScenario` | `tuple[ReplenishmentItem, ...]` | `total_cost_of(plan)`, `required_quantities`, `most_expensive_position_among`, `size` |
| `Population` | `tuple[PurchasePlan, ...]` | `ranked_by(policy)`, `best`, `top(n)`, `extended_with`, `size` |
| `StockSnapshots` | `tuple[StockSnapshot, ...]` | `latest_per_product`, `features_matrix_rows` |
| `WeeklyDemandForecasts` | `Mapping[Sku, WeeklyDemandForecast]` | `for_sku`, `iterate` |
| `GenerationHistory` | `tuple[GenerationReport, ...]` | `appended_with`, `best_fitness`, `as_curve_points` |

**Proibido:** `List[int]` como parâmetro ou retorno de método de domínio; expor `.items` ou `.plans` como atributo público.

## Regra 5 — Um ponto por linha (Lei de Demeter)

```python
# RUIM
cost = scenario.items()[position].catalog_item().unit_price().total_for(quantity)

# BOM — diga, nao pergunte
cost = scenario.cost_at(position, quantity)
```

Cadeia de acesso é sintoma de que o comportamento está no objeto errado. Exceção: encadeamento **fluente** sobre o mesmo tipo (`Quantity.limited_to(...).decremented()`) é permitido — cada chamada devolve o próprio tipo, não navega estrutura alheia.

## Regra 6 — Não abrevie

| Proibido | Use |
|---|---|
| `qtd`, `qty` | `quantity` |
| `pop` | `population` |
| `gen` | `generation` |
| `calc` | `calculate` / nome do resultado |
| `idx`, `i` (fora de `range`) | `position`, `index` |
| `req` | `required_quantity` / `request` |
| `prod` | `product` |
| `cfg` | `settings` |
| `tmp`, `aux`, `data`, `info`, `obj` | nome do conceito real |

Se o nome ficou longo demais, o problema é a responsabilidade da classe, não o nome.

## Regra 7 — Mantenha todas as entidades pequenas

| Unidade | Limite |
|---|---|
| Classe | **≤ 50 linhas** |
| Método | **≤ 5 linhas** |
| Arquivo/módulo | **≤ 200 linhas**, uma classe pública por arquivo |
| Pacote | **≤ 10 arquivos** (mais que isso: crie subpacote) |
| Parâmetros por método | **≤ 3** (mais que isso: crie Value Object agrupador) |

É por isso que os parâmetros do AG viram `EvolutionSettings` em vez de 8 argumentos soltos.

## Regra 8 — No máximo 2 atributos de instância

A regra que mais dói — e a que mais melhora o desenho. Resolve-se por **composição**, não por exceção:

```python
# RUIM — 3 atributos
class ReplenishmentItem:
    def __init__(self, sku, unit_price, required_quantity): ...

# BOM — composicao: 2 + 2
@dataclass(frozen=True, slots=True)
class CatalogItem:
    _sku: Sku
    _unit_price: UnitPrice

@dataclass(frozen=True, slots=True)
class ReplenishmentItem:
    _catalog_item: CatalogItem
    _required_quantity: Quantity
```

O mesmo padrão resolve `EvolutionEngine` (`_settings` + `_operators`) e `EvolutionOperators` (`_reproduction` + `_evaluation`, cada um agrupando duas estratégias).

**Exceções permitidas, e apenas estas:** Value Object que agrupa parâmetros de configuração (`EvolutionSettings`) e modelos Pydantic de borda. Toda exceção precisa de comentário `# OC-8: <justificativa>` na classe — sem comentário, não passa na revisão.

## Regra 9 — Sem getters, setters ou propriedades

Exponha **comportamento**, não estado.

```python
# RUIM
if plan.get_cost() > budget.get_limit(): ...

# BOM
if budget.is_exceeded_by(scenario.total_cost_of(plan)): ...
```

Acesso a estado cru é permitido **só** na fronteira de serialização, por método de nome explícito que declara a intenção:

* `value_for_serialization()` — usado exclusivamente pelos mapeadores em `api/mappers/` e `infrastructure/`.
* **Proibido** `@property`, `get_*`, `set_*` e atributo público em `domain/`.
* Objetos de domínio são imutáveis; "mudar" é devolver nova instância.

---

## 10. Como verificar automaticamente

```bash
# Regra 2 — nenhum else/elif no dominio
grep -rnE "^\s*(else:|elif )" backend/src/domain backend/src/application && echo "VIOLACAO OC-2"

# Regra 9 — nenhum getter/setter/property no dominio
grep -rnE "@property|def get_|def set_" backend/src/domain && echo "VIOLACAO OC-9"

# Regra 7 — arquivos acima de 200 linhas
find backend/src/domain -name "*.py" -exec awk 'END{if(NR>200) print FILENAME": "NR" linhas"}' {} \;

# Regra 3 — tipos primitivos em assinaturas publicas do dominio
grep -rnE "def [a-z_]+\(self[^)]*: (int|float|str|bool)" backend/src/domain | grep -v "__post_init__\|_for_serialization"
```

Complementos no CI: `ruff` (com `PLR0912` complexidade, `PLR0913` nº de argumentos, `C901`), `mypy --strict`, e os greps acima como passo de lint. Ver `04-estrategia-de-testes.md`.

## 11. Exceções por camada (lista fechada)

| Camada | Exceção permitida | Motivo |
|---|---|---|
| `api/schemas/` | Modelos Pydantic com N campos primitivos e sem comportamento | São contrato de borda, traduzidos imediatamente para Value Objects |
| `api/mappers/` | Acesso a `value_for_serialization()` | É a fronteira de serialização |
| `infrastructure/forecasting/` | Arrays NumPy, DataFrames, `float` cru | Exigência das bibliotecas de ML; convertido para Value Object antes de sair do adaptador |
| `infrastructure/dataset/` | Laços com múltiplos níveis na geração do dataset sintético | Fidelidade à sequência de sorteios do notebook (ver `01-dominio-e-negocio/03-previsao-de-demanda.md`) |
| `core/container.py` | Muitas instanciações concretas em sequência | É o único lugar que conhece classes concretas (DIP) |
| `tests/` | Dublês simples com atributos públicos | Legibilidade de teste |

Fora desta tabela, as 9 regras valem sem negociação. Nenhuma exceção vale para `domain/`.
