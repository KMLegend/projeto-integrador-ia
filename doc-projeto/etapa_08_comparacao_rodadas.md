# Etapa 08 — Comparação: código na mão × engenharia de prompt

**Projeto Integrador IV** · Gestão Preditiva de Estoque com IA
**Integrantes:** Carlos Eduardo, Adryan Kevin, Eduardo Mendonça, Gabriel e Kevin Maykel
**Entrega:** 09/12/2026 · referente às Atividades 06, 07 e 08

---

## A funcionalidade comparada

As duas rodadas implementam **a mesma coisa**: a função de aptidão e o algoritmo genético
que decidem quanto comprar de cada produto dentro de um orçamento limitado.

```
fitness = cobertura(%) × 10 − produtos_em_risco × 5
```

| | Rodada 1 — na mão | Rodada 2 — engenharia de prompt |
|---|---|---|
| Artefato | `Projeto_Preditivo.ipynb` (Colab) | Sistema completo em `backend/` e `frontend/` |
| Como foi feito | Código digitado pelo grupo, sem agente | Orquestração de um agente de codificação por prompt |
| Período | Entregáveis 03 e 04 (set/2026) | Atividades 06–07 (out–nov/2026) |

### As duas produzem o mesmo resultado

Executável: `python3.12 doc-projeto/etapa_08_equivalencia.py` (requer Python 3.11+;
nesta máquina `python3` é 3.9 e não serve).

| Caso | Rodada 1 | Rodada 2 |
|---|---:|---:|
| Baseline (divisão igual) | fitness **236,5753** · R$ 314,32 | fitness **236,5753** · R$ 314,32 |
| Plano ótimo | fitness **816,9178** · R$ 987,44 | fitness **816,9178** · R$ 987,44 |
| Plano vazio | fitness **−10,0000** | fitness **−10,0000** |
| Acima da necessidade | fitness **816,9178** | fitness **816,9178** |
| **3.000 planos aleatórios** | — | **0 divergências** |

A reimplementação não mudou a regra de negócio. Isso é o que torna a comparação justa:
o que mudou foi **como** o código foi produzido, não **o que** ele calcula.

---

## Comparação objetiva

### Volume e estrutura

| Dimensão | Rodada 1 | Rodada 2 |
|---|---:|---:|
| Arquivos de código | 1 | 128 Python + 26 TypeScript |
| Linhas de código | 243 | 4.342 (backend) |
| Linhas do fitness + AG | 115 | distribuídas em 61 módulos de domínio |
| Testes automatizados | 0 | 145 backend + 30 frontend |
| Cobertura do domínio | não medida | 96% |
| Tipagem estática | nenhuma | `mypy --strict` em 128 arquivos |
| Documentação | comentários no notebook | 25 documentos, 4.292 linhas |
| Decisões de arquitetura registradas | 0 | 18 |
| Execução | Google Colab | 4 contêineres Docker |

### Tempo

> **A preencher pelo grupo.** Não registramos o tempo da Rodada 1 durante os encontros de
> 28/10 e 04/11, como o roteiro pedia. Os dados acima são medidos no repositório; o tempo é
> a única dimensão que depende da nossa memória, e preferimos deixar o campo explícito a
> inventar um número.

| | Rodada 1 | Rodada 2 |
|---|---|---|
| Tempo até funcionar | _____ | _____ |
| Tempo até ficar confiável | não se aplica (sem testes) | _____ |

### Controle sobre o código

| | Rodada 1 | Rodada 2 |
|---|---|---|
| Quem decide a regra de negócio | o grupo, linha a linha | o grupo, via especificação escrita |
| Quem escreve o código | o grupo | o agente |
| Onde o controle é exercido | no editor | na especificação e na **revisão** |
| Risco principal | errar a lógica | o agente desviar da especificação sem avisar |

Na Rodada 2 o controle não desapareceu — ele **mudou de lugar**. Passamos a controlar por
documento de especificação (a pasta `.context/`, com 25 documentos) e por verificação
automática (lint, tipagem, contratos de importação, 175 testes).

---

## Erros do agente

Foram registrados **21 defeitos** durante a Rodada 2, no arquivo
`.context/04-decisoes-e-roadmap/04-correcoes-pendentes.md`.

| Categoria | Qtd. | Exemplos |
|---|---:|---|
| Defeitos funcionais, só visíveis executando | 6 | orçamento da requisição ignorado; corrida ao registrar a tarefa; gráfico em branco |
| Portões de qualidade não atendidos | 7 | 63 erros de lint, 7 de tipagem, cobertura sem portão |
| Escopo simplesmente não entregue | 4 | README, pipeline de CI, versões não fixadas |
| Teste que mascarava o defeito | 1 | o teste ponta a ponta tolerava a falha em vez de acusá-la |
| Inconsistência inventada na documentação | 1 | criou uma numeração de decisões que conflitava com a oficial |
| Desvios não registrados | 1 | mudanças de projeto sem decisão documentada |
| Erro da nossa própria especificação | 1 | pedimos um valor que era impossível de atingir |

### Os três achados que mais importam

**1. O defeito mais grave passou despercebido em duas auditorias.**
O campo `budget_limit` enviado pela tela era **ignorado**: com orçamento de R$ 1,00 o sistema
devolvia um plano de R$ 987,44. Só apareceu quando testamos com valores *diferentes* do
padrão — as duas verificações anteriores sempre usaram R$ 1.000, exatamente o valor em que
a requisição coincidia com o default do código.

**2. O agente declarou conclusão duas vezes com defeitos abertos.**
Em ambas as vezes o relatório dizia "todas as pendências implementadas e validadas". Em ambas,
uma verificação independente encontrou defeitos reproduzíveis ainda de pé.

**3. O agente inventou fatos no próprio relatório.**
O resumo final afirmou "5 produtos em risco" (eram 2) e nomeou o produto em falta como
"Açúcar refinado" — que **não existe** no catálogo; o correto era Café 500g. O código estava
certo; o texto sobre o código, não.

---

## Nota conclusiva do grupo

### Onde a implementação na mão valeu mais a pena

- **Entender o problema.** Escrever o fitness à mão obrigou o grupo a decidir o que
  "boa compra" significa. Essa decisão não é delegável — foi ela que virou especificação na
  Rodada 2.
- **Volume pequeno.** Para 115 linhas que rodam uma vez numa apresentação, montar
  infraestrutura, testes e contêineres seria desperdício.
- **Aprendizado.** O objetivo acadêmico é aprender computação evolutiva, e isso se aprende
  digitando o operador de reparo, não pedindo que alguém o escreva.

### Onde a engenharia de prompt valeu mais a pena

- **Volume.** 4.342 linhas de backend, 175 testes, Docker, CI e 25 documentos em um tempo
  que não teríamos para escrever à mão.
- **Padrões de engenharia.** SOLID, Object Calisthenics e modularidade foram aplicados de
  forma consistente em 128 arquivos, com verificação automática — disciplina difícil de
  sustentar manualmente ao longo de semanas.
- **Refatoração.** Reestruturar 32 métodos para caberem no limite de 5 linhas foi um pedido
  de uma frase. À mão, seria um dia de trabalho arriscado.

### O custo que não aparece no cronograma

A engenharia de prompt **não eliminou trabalho; deslocou-o**. O agente produz código muito
mais rápido do que produz confiança. O que gastamos em digitação, passamos a gastar em:

1. **Especificar antes.** Os 25 documentos de `.context/` não são burocracia — são o que
   impede o agente de inventar regra de negócio.
2. **Verificar depois, de forma independente.** Executar o sistema e conferir os números
   contra os valores do notebook. Foi assim que os 21 defeitos apareceram — nenhum deles
   pelo relato do agente.
3. **Desconfiar do relatório.** A lição mais cara da Rodada 2: *o agente é melhor
   produzindo código do que avaliando o próprio código*.

### Em uma frase

> A rodada na mão nos ensinou **o que** construir. A rodada por prompt construiu em escala —
> mas só foi confiável porque a primeira rodada nos deu o número (816,92) com o qual
> conferir a segunda.
