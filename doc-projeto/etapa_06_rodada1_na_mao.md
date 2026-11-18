# Atividade 06 — Rodada 1: implementação "na mão"

**Projeto Integrador IV** · Gestão Preditiva de Estoque com IA
**Integrantes:** Carlos Eduardo, Adryan Kevin, Eduardo Mendonça, Gabriel e Kevin Maykel
**Encontros:** 28/10 e 04/11/2026

---

## A funcionalidade escolhida

**Decisão de reposição de estoque sob restrição orçamentária.** Dada a previsão de demanda de
cada produto, decidir quanto comprar de cada um sem estourar o orçamento, maximizando a
demanda atendida e minimizando produtos desabastecidos.

Escolhemos essa funcionalidade por três motivos: ela é pequena o suficiente para caber em um
notebook, é real dentro do domínio do projeto (não é exercício artificial), e é a peça que
mais concentra regra de negócio — o que torna a comparação com a Rodada 2 significativa.

**Artefato:** `Projeto_Preditivo.ipynb`, Entregável 04 (células de `ajustar_ao_orcamento` em
diante).
**Condição:** escrita manualmente, sem agente de codificação.

### Funcionando de ponta a ponta

| Etapa | Resultado |
|---|---|
| Entrada | 6 produtos com estoque, preço e previsão de demanda semanal |
| Necessidade do ciclo de 4 semanas | 146 unidades · R$ 1.475,72 para cobrir 100% |
| Orçamento | R$ 1.000,00 (déficit de R$ 475,72) |
| Saída | Plano de compra: 98 un. de Leite + 22 un. de Café |
| Indicadores | custo R$ 987,44 · cobertura 82,2% · 1 produto em risco · **fitness 816,92** |

---

## Decisões técnicas tomadas durante o desenvolvimento

### 1. Representar a solução como vetor de quantidades

Cada candidato é uma lista com a quantidade a comprar de cada produto, na ordem da tabela.
Escolhemos isso em vez de uma estrutura com nomes porque o algoritmo genético precisa cruzar
e mutar posições — e índice é mais simples de cruzar que chave.

### 2. Reparar em vez de penalizar soluções inviáveis

Esta foi a decisão mais discutida. Havia duas opções:

- **Penalizar:** deixar o algoritmo gerar planos que estouram o orçamento e dar nota baixa a eles.
- **Reparar:** consertar o plano antes de avaliar.

Escolhemos reparar. Com penalização, boa parte da população seria composta de soluções
inúteis, e o algoritmo gastaria gerações aprendendo a restrição em vez de otimizar dentro
dela. A função `ajustar_ao_orcamento` limita cada quantidade à necessidade real e remove
unidades até caber.

### 3. Remover sempre a unidade do item mais caro

Dentro do reparo, era preciso escolher de quem tirar. Optamos pelo item de maior preço
unitário — cada unidade removida custa exatamente uma unidade de cobertura, cara ou barata,
então tirar a mais cara libera o máximo de orçamento perdendo o mínimo de cobertura.

### 4. Pesos 10 e 5 na função de aptidão

```
fitness = cobertura(%) × 10 − produtos_em_risco × 5
```

A cobertura é a recompensa principal, multiplicada por 10 para dominar a nota. A penalidade
de 5 por produto desabastecido é um desempate: entre dois planos que cobrem o mesmo volume,
preferimos o que concentra a compra e deixa menos produtos zerados — em varejo, produto em
falta custa cliente, independentemente de quantas unidades faltaram.

Os valores foram escolhidos por tentativa: queríamos que a penalidade desempatasse sem
nunca superar o ganho de cobertura.

### 5. Elitismo de 2 indivíduos

Preservar os dois melhores de cada geração garante que a solução nunca piora. Sem isso, o
cruzamento e a mutação podiam destruir a melhor solução encontrada — e vimos isso acontecer
nos primeiros testes.

### 6. Semente fixa (42)

Para a demonstração ser reproduzível ao vivo. Sem semente, cada execução daria um plano
ligeiramente diferente, e não teríamos um número estável para comparar depois.

---

## Tempo gasto

> **Não registramos.** O roteiro pedia o registro do tempo durante os encontros de 28/10 e
> 04/11, e o grupo não anotou. Preferimos declarar a ausência a estimar um número agora, de
> memória, que entraria na comparação da Atividade 08 como se fosse medição.

| | Valor |
|---|---|
| Tempo até funcionar | _não registrado_ |
| Tempo de depuração | _não registrado_ |

O que **é** mensurável no artefato:

| Métrica | Valor |
|---|---:|
| Linhas de código do fitness + AG | 115 |
| Funções escritas | 6 |
| Arquivos | 1 |
| Testes automatizados | 0 |
| Tipagem estática | nenhuma |

---

## O que esta rodada nos deu

Escrever o fitness à mão obrigou o grupo a **decidir o que "boa compra" significa** — essa
decisão não é delegável a um agente, e foi exatamente ela que virou especificação na
Rodada 2.

E produziu o valor de referência — **fitness 816,92** — com o qual conferimos, depois, se a
reimplementação por prompt estava correta.
