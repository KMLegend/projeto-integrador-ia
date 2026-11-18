# Atividade 07 — Rodada 2: reimplementação via engenharia de prompt

**Projeto Integrador IV** · Gestão Preditiva de Estoque com IA
**Integrantes:** Carlos Eduardo, Adryan Kevin, Eduardo Mendonça, Gabriel e Kevin Maykel
**Encontros:** 11/11 e 18/11/2026

---

## A mesma funcionalidade, sem digitar código

Refizemos do zero a decisão de reposição sob restrição orçamentária — a mesma funcionalidade
da Rodada 1 — orquestrando um agente de codificação (Claude Code) apenas por prompt.

**Regra que seguimos:** o grupo não escreveu código de produção. Escrevemos especificação,
lemos o que o agente produziu, executamos, e corrigimos **por prompt**.

### Prova de que é a mesma funcionalidade

```bash
python3.12 doc-projeto/etapa_08_equivalencia.py
```

| Caso | Rodada 1 | Rodada 2 |
|---|---:|---:|
| Baseline | fitness 236,5753 | fitness 236,5753 |
| Plano ótimo | fitness **816,9178** | fitness **816,9178** |
| 3.000 planos aleatórios | — | **0 divergências** |

---

## Como os prompts foram estruturados

A descoberta mais importante da rodada: **pedir o sistema direto não funciona**. A primeira
tentativa produziu código que ignorava regras de negócio e inventava números.

Mudamos a abordagem para três camadas:

### Camada 1 — especificação antes de qualquer código

Em vez de pedir "construa o sistema", escrevemos primeiro uma base de contexto que o agente
lê antes de codar: **25 documentos, 4.292 linhas**, em `.context/`.

| Pasta | Conteúdo |
|---|---|
| `01-dominio-e-negocio/` | Regras, função fitness, algoritmo genético, valores de referência |
| `02-padroes-de-engenharia/` | SOLID, Object Calisthenics, modularidade, testes |
| `03-implementacao/` | Estrutura de pastas, contratos de código, Docker |
| `04-decisoes-e-roadmap/` | Decisões, 41 tarefas, registro de correções |

O prompt que iniciou a rodada, em essência:

> "Com base na arquitetura descrita na pasta `.context`, crie arquivos RAG para outros
> agentes realizarem a implantação. Além do contexto de arquitetura é necessário criar a
> lógica de negócio com função fitness e AG, usando o arquivo `Projeto_Preditivo.ipynb`.
> O projeto deve ter: SOLID, Object Calisthenics, Docker e modularidade."

### Camada 2 — tarefas atômicas

A implementação foi quebrada em **41 tarefas** (`03-tasks-de-implementacao.md`), cada uma com
o que fazer, o que ler antes, o que entregar, o critério de aceite e **o que não fazer**.

O campo "não fazer" foi o que mais evitou retrabalho. Exemplo real:

> "**Não fazer:** não 'corrija' a mutação para sortear só posições com necessidade > 0 — a
> ineficiência é fiel ao notebook e documentada."

Sem esse travamento, o agente "melhorava" o algoritmo e quebrava a equivalência com a
Rodada 1.

### Camada 3 — verificação independente

Prompts de auditoria, separados dos de implementação:

> "Valide se está de acordo com o que era necessário e foi descrito."

Foi essa camada que encontrou os defeitos. **Nenhum deles veio do relato do agente.**

---

## Onde o agente precisou de correção

**21 defeitos registrados** em `.context/04-decisoes-e-roadmap/04-correcoes-pendentes.md`,
todos com evidência reproduzível.

| Categoria | Qtd. |
|---|---:|
| Defeitos funcionais, só visíveis executando o sistema | 6 |
| Portões de qualidade não atendidos (lint, tipagem, cobertura) | 7 |
| Escopo simplesmente não entregue (README, CI, versões) | 4 |
| Teste que mascarava o próprio defeito | 1 |
| Inconsistência inventada na documentação | 1 |
| Desvios de projeto não registrados | 1 |
| Erro da nossa própria especificação | 1 |

### Os casos mais instrutivos

**O agente ignorava um parâmetro da tela inteiro.**
O campo de orçamento não chegava ao algoritmo: com teto de R$ 1,00 o sistema devolvia um
plano de R$ 987,44 — 987 vezes o limite. Os conversores corretos existiam no código, mas
**nunca eram chamados**: eram código morto. Passou por duas auditorias porque ambas usaram
R$ 1.000, justamente o valor em que a requisição coincide com o padrão interno.
*Correção por prompt:* "o `budget_limit` da requisição é ignorado — use `to_budget_constraint()`".

**O teste tolerava o defeito em vez de acusá-lo.**
O teste ponta a ponta consultava em laço com `sleep`, absorvendo um erro `404` real. Suíte
verde, defeito vivo.
*Correção por prompt:* escrever um teste que **falhasse** com o código atual antes de corrigir.

**O agente declarou conclusão duas vezes com defeitos abertos.**
Em ambas, o relatório afirmava "todas as pendências implementadas e validadas". Em ambas,
uma verificação independente encontrou defeitos reproduzíveis.

**O agente inventou fatos sobre o próprio trabalho.**
O relatório final citou "5 produtos em risco" (eram 2) e nomeou o produto em falta como
"Açúcar refinado" — que não existe no catálogo. O código estava correto; o texto sobre o
código, não.

**Um erro foi nosso, não do agente.**
Especificamos como valor-ouro um número (777,67) que dependia do gerador de aleatórios do
NumPy, enquanto outra tarefa exigia o gerador da biblioteca padrão. Requisitos mutuamente
inviáveis — o agente seguiu o correto, e a especificação é que foi corrigida.

---

## Ajustes que o agente não fez sozinho

| Onde | O que precisou de prompt explícito |
|---|---|
| Rota da API | Registrar a tarefa antes de despachar, para não devolver `404` logo após aceitar |
| WebSocket | Encerrar o laço no desligamento, senão a API travava ao recarregar |
| Frontend | Tirar efeito colateral de dentro do atualizador de estado (o React 18 o executa duas vezes) |
| Apresentação | Tabela sobrepondo o gráfico, por um parâmetro de posição que o gerador ignorava |

---

## Resultado da rodada

| Métrica | Valor |
|---|---:|
| Módulos Python | 128 |
| Linhas de backend | 4.342 |
| Arquivos TypeScript | 26 |
| Testes automatizados | 145 backend + 30 frontend |
| Cobertura do domínio | 96% |
| Decisões de arquitetura registradas | 18 |
| Serviços em contêiner | 4 |

**Tempo:** _não registrado_ — mesma lacuna da Rodada 1, declarada na Atividade 08.

---

## Conclusão da rodada

O agente escreveu 100% do código de produção. O grupo escreveu **a especificação e as
correções** — e foi aí que o trabalho se concentrou.

A lição que levamos: *o agente produz código muito mais rápido do que produz confiança*.
Sem a Rodada 1 para nos dar o número de referência (816,92), não teríamos como saber se o
sistema estava certo.
