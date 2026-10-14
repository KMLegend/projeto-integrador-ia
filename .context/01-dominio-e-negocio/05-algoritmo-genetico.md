---
id: 05-algoritmo-genetico
dominio: dominio-e-negocio
palavras-chave: algoritmo genetico, AG, computacao evolutiva, cromossomo, populacao, selecao, crossover, mutacao, elitismo, geracoes, convergencia, DEAP, pygad
fonte-da-verdade: Projeto_Preditivo.ipynb (Entregavel 04, secao 5)
depende-de: [04-funcao-fitness, 02-regras-de-negocio, 06-baseline-e-indicadores]
---

# Algoritmo Genético (Computação Evolutiva)

Motor que escolhe **quanto comprar de cada produto** dentro do orçamento, maximizando a função fitness de `04-funcao-fitness.md`.

---

## 1. Por que AG e não programação linear

Alocação de orçamento com objetivos múltiplos (cobrir volume × evitar prateleira vazia) é combinatória. O AG entrega solução de alta qualidade rápido e — principal motivo de projeto — **aceita restrições não-lineares sem reformulação**: desconto escalonado por volume, espaço cúbico de caminhão, penalidade de validade. Com PL, cada uma dessas exigiria remodelar o problema; aqui, basta trocar a `FitnessPolicy` ou o `PlanRepair`.

> Resposta honesta à banca: para **este** cenário de 6 produtos, o ótimo também sairia de um guloso simples (comprar do mais barato ao mais caro). O AG se justifica pela extensibilidade e porque o problema cresce rápido com o número de SKUs e de restrições. Nesta PoC, o fato de o guloso e o AG concordarem é usado como **validação** do AG (ver `06-baseline-e-indicadores.md`).

## 2. Representação

**Cromossomo = `PurchasePlan`**: vetor de inteiros, uma posição por item do cenário, **na mesma ordem do `ReplenishmentScenario`** (ordenado por nome de produto).

```
Posição:  0           1          2                 3           4              5
Item:     Arroz 5kg   Café 500g  Detergente 500ml  Feijão 1kg  Leite UHT 1L   Refrigerante 2L
Plano:    [0,         22,        0,                0,          98,            0]
```

* Gene = quantidade a comprar de um produto. Domínio do gene: `0 ≤ gene ≤ required_quantity(i)` (RN-04).
* `PurchasePlan` é **imutável** e é uma *first-class collection* (regra 4 de Object Calisthenics): encapsula `tuple[Quantity, ...]` e expõe comportamento (`clamped_to`, `decremented_at`, `with_quantity_at`, `non_empty_positions`), nunca a tupla crua.
* Cada operação devolve **novo** plano. Nenhuma mutação in-place — é o que torna elitismo e histórico seguros.

## 3. Parâmetros (padrões = valores do notebook)

| Parâmetro | Padrão | Faixa válida | Origem |
|---|---|---|---|
| `population_size` | 60 | 10–500 | Requisição (`ga_parameters.population_size`) |
| `generations` | 100 | 1–1000 | Requisição (`ga_parameters.generations`) |
| `mutation_rate` | 0.20 | 0.0–1.0 | Requisição (opcional) |
| `parents_size` | 20 | 2–`population_size` | Requisição (opcional) |
| `elite_size` | 2 | 0–`parents_size` | Requisição (opcional) |
| `mutation_range` | ±10 unidades | ≥ 1 | Configuração |
| `random_seed` | 42 | ≥ 0 | Requisição (opcional) |
| `progress_every` | 10 gerações | ≥ 1 | Configuração |

Validações cruzadas (falha com `422` na borda, `InvalidParametersError` no domínio):
`elite_size ≤ parents_size ≤ population_size` e `population_size ≥ 2`.

Agrupar tudo num único Value Object `EvolutionSettings` — **não** passe 8 argumentos soltos para o motor (viola Object Calisthenics e SRP).

## 4. Operadores (normativos)

### 4.1 Inicialização — `PlanFactory.random_plan()`

```
para cada item i:
    gene(i) = random_integer_inclusive(0, required_quantity(i))   se required_quantity(i) > 0
    gene(i) = 0                                                   caso contrário
devolver repair(plano)
```

### 4.2 Seleção — truncamento (`TruncationSelection`)

```
ordenar a população por fitness DESC (desempate: ordem estável de inserção)
pais = os primeiros parents_size (20) indivíduos
```

Depois, cada par de progenitores é sorteado **com reposição** e de forma independente do grupo de pais (`uniform`). Pode sortear o mesmo indivíduo duas vezes — comportamento do notebook, mantido.

### 4.3 Crossover — uniforme (`UniformCrossover`)

```
para cada posição i:
    gene_filho(i) = gene_pai_a(i)   se random_ratio() < 0.5
                  = gene_pai_b(i)   caso contrário
devolver repair(filho)
```

### 4.4 Mutação — perturbação local (`LocalShiftMutation`)

```
se random_ratio() >= mutation_rate:  devolver plano inalterado
posicao  = random_integer_below(numero_de_itens)
variacao = random_integer_inclusive(-10, +10)
gene(posicao) = max(0, gene(posicao) + variacao)
devolver repair(plano)
```

* Probabilidade de mutação é **por indivíduo**, não por gene.
* **Ineficiência conhecida e mantida:** a posição sorteada pode ser um item com necessidade 0, e o reparo zera a mudança — mutação desperdiçada. Fidelidade ao notebook tem prioridade. Melhoria opcional (`NeedAwareMutation`, sorteando só entre posições com necessidade > 0) deve ser **classe nova** e opt-in, nunca mudança do padrão.

### 4.5 Elitismo

Os `elite_size` (2) melhores indivíduos da geração passam **intactos** — sem crossover, sem mutação. Garante que o melhor fitness é **monotonicamente não-decrescente** ao longo das gerações; é o que dá a curva de convergência bem-comportada do gráfico do frontend.

## 5. Laço evolutivo (ordem normativa — reproduz o notebook)

```
populacao = [ random_plan() for _ in range(population_size) ]
history = []

para generation em 0 .. generations-1:
    1. avaliados  = ordenar(populacao por fitness DESC)
    2. history.append( fitness(avaliados[0]) )          # registra ANTES de evoluir
    3. notificar_progresso(generation, fitness(avaliados[0]))   # respeitando progress_every
    4. pais       = avaliados[:parents_size]
    5. nova       = pais[:elite_size]                   # elitismo
    6. enquanto len(nova) < population_size:
           pai_a = pais[random_integer_below(len(pais))]
           pai_b = pais[random_integer_below(len(pais))]
           nova.append( mutate( crossover(pai_a, pai_b) ) )
    7. populacao = nova

melhor = max(populacao, key=fitness)
devolver EvolutionResult(melhor, history)
```

Pontos que **não** podem mudar:

* O histórico registra o melhor da geração **antes** de gerar a próxima. Logo, `history[0]` é o melhor da população aleatória inicial (no notebook: **777,67**) e `history[-1]` é o melhor da última geração (**816,92**).
* O resultado final é o melhor da **última** população — correto porque o elitismo impede regressão.
* `history` tem exatamente `generations` elementos.

## 6. Observabilidade (progresso em tempo real)

O contrato de WebSocket exige `{generation, max_fitness, status}`. O domínio **não** conhece Redis nem WebSocket:

```python
# domain/ports/evolution_observer.py
class EvolutionObserver(Protocol):
    def on_generation(self, report: GenerationReport) -> None: ...
```

| Implementação | Camada | Papel |
|---|---|---|
| `NullEvolutionObserver` | `domain/` | Padrão Null Object — evita `if observer is not None` (regra "sem else" + OCP) |
| `ThrottledEvolutionObserver` | `application/` | Decorator: repassa 1 em cada `progress_every` gerações, **sempre** incluindo a primeira e a última |
| `RedisProgressPublisher` | `infrastructure/messaging/` | Publica no canal Pub/Sub `progress:{task_id}` |
| `RecordingEvolutionObserver` | `tests/` | Acumula relatórios para assertivas |

O endpoint WebSocket do FastAPI assina o canal Redis e repassa ao cliente. Falha de publicação de progresso **nunca** derruba a otimização: o publisher trata erro de rede, registra log e segue.

## 7. Estrutura de classes

| Classe | Camada | Responsabilidade única | Atributos |
|---|---|---|---|
| `EvolutionEngine` | `domain/evolution/` | Executar o laço evolutivo | `_settings`, `_operators` |
| `EvolutionOperators` | `domain/evolution/` | Agrupar as 4 estratégias injetadas | `_reproduction`, `_evaluation` |
| `TruncationSelection` | `domain/evolution/` | Selecionar progenitores | `_parents_size` |
| `UniformCrossover` | `domain/evolution/` | Combinar dois planos | `_random_source`, `_repair` |
| `LocalShiftMutation` | `domain/evolution/` | Perturbar um gene | `_random_source`, `_repair` |
| `PlanFactory` | `domain/evolution/` | Criar planos aleatórios viáveis | `_random_source`, `_repair` |
| `Population` | `domain/evolution/` | First-class collection de planos | `_plans` |
| `EvolutionResult` | `domain/evolution/` | Melhor plano + histórico | `_best_assessment`, `_history` |
| `GenerationReport` | `domain/evolution/` | Um ponto da curva | `_generation`, `_best_fitness` |

Nenhuma dessas classes importa `numpy`, `deap` ou `pygad`.

## 8. Aleatoriedade determinística (`RandomSource`)

```python
# domain/ports/random_source.py
class RandomSource(Protocol):
    def ratio(self) -> float: ...                                  # [0, 1)
    def integer_below(self, exclusive_limit: int) -> int: ...       # [0, limit)
    def integer_inclusive(self, minimum: int, maximum: int) -> int: ...
```

* Adaptador de produção: `SeededRandomSource` sobre `random.Random(seed)` (stdlib basta; o AG não precisa de numpy).
* Adaptador de teste: `ScriptedRandomSource`, que devolve uma sequência pré-definida — é o que permite testar crossover e mutação de forma exata, sem flakiness.
* **Proibido** chamar `random`/`np.random` diretamente em qualquer camada acima de `infrastructure`.

## 9. Sobre DEAP e PyGAD

`00-arquitetura-tecnica/vis_o_geral_da_arquitetura.md` menciona "DEAP ou PyGAD". **Decisão: implementação própria** (ver D-02 em `04-decisoes-e-roadmap/01-divergencias-e-decisoes.md`). Motivos:

1. Fidelidade exata ao notebook, incluindo o operador de reparo customizado — valores-ouro precisam bater com o que foi apresentado.
2. O domínio fica livre de dependência externa, o que é pré-requisito da regra de dependência e das exigências SOLID/Object Calisthenics.
3. O código do AG é a entrega acadêmica central de Computação Evolutiva; terceirizá-lo a uma biblioteca esvaziaria a avaliação.

Se no futuro DEAP/PyGAD forem desejados, entram como **adaptador alternativo** de uma porta `OptimizationEngine` em `infrastructure/`, sem tocar no domínio.

## 10. Checklist de aceite do AG

1. Com `random_seed=42` e cenário de referência, encontra plano com fitness **816,92** e custo **R$ 987,44**.
2. `history` tem `generations` elementos e é **não-decrescente** (consequência do elitismo) — testar com 1.000 gerações.
3. Duas execuções com a mesma semente dão resultado byte-a-byte idêntico; sementes diferentes podem variar, mas nunca produzir plano inviável.
4. Todo plano de toda geração respeita orçamento e necessidade (teste de invariante com observer que inspeciona cada geração).
5. `population_size=2, generations=1, elite_size=2` roda sem erro (caso degenerado).
6. Cenário sem nenhuma necessidade → plano todo zero, fitness 1000, sem laço infinito.
7. Trocar `FitnessPolicy`, `PlanRepair`, seleção, crossover ou mutação **não exige alterar** `EvolutionEngine` (provado por teste que injeta dublês).
8. Nenhum uso de `random` global: `grep -rn "import random\|np.random" domain/ application/` não retorna nada além da porta.
