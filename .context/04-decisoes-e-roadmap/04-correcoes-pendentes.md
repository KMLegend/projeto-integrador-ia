---
id: 04-correcoes-pendentes
dominio: decisoes
palavras-chave: correcoes, bugs, defeitos, auditoria, pendencias, fix, remediacao, portoes de qualidade, conformidade
fonte-da-verdade: auditoria executada em 14/10/2026 contra a implementacao no diretorio de trabalho
depende-de: [03-tasks-de-implementacao, 01-divergencias-e-decisoes]
---

# Correções Pendentes (auditoria 14/10/2026 · 2 revalidações)

Resultado da validação da implementação contra `03-tasks-de-implementacao.md` e `02-padroes-de-engenharia/`. Cada `FIX` é uma ordem de serviço autocontida, no mesmo formato das TASKs: um agente pega **um** FIX, corrige, prova pelo *Aceite* e para.

**Toda evidência abaixo foi reproduzida**, não inferida. Os comandos de *Evidência* reproduzem a falha.

---

## Situação geral

### O que já está correto — não regredir

Validado no stack containerizado em execução (`POST /api/v1/optimize` → `GET /api/v1/status`):

| Indicador | Esperado | Obtido |
|---|---|---|
| `total_cost` · `fitness` | R$ 987,44 · 816,92 | idêntico |
| cobertura · itens em risco | 120/146 = 82,2% · 1 | idêntico |
| baseline | 314,32 · 36 un · 24,7% · 2 · 236,58 | idêntico |
| MAE do modelo | 4,76 | idêntico |

Também aprovados: `lint-imports` 3/3 contratos *KEPT*; `check_calisthenics.sh` (regras 2, 3, 7-arquivos, 9); regra 8 com as 8 exceções todas justificadas por `# OC-8`; decisões D-01, D-03, D-06 respeitadas; cobertura de `domain/` em 95%; frontend com `tsc` e `eslint --max-warnings 0` limpos e 27 testes verdes.

> **Guarda de regressão:** nenhum FIX pode alterar função fitness, pesos (10/5), operador de reparo ou operadores do AG. Se um FIX parecer exigir isso, pare e registre `D-nn` em `01-divergencias-e-decisoes.md` antes.

### Ordem de execução recomendada

```
FIX 1 → FIX 2 → FIX 3      (defeitos: quebram a demonstração)
FIX 4 → FIX 8              (portões: impedem que a regressão volte)
FIX 9 → FIX 12             (escopo da Fase 7, nao entregue)
FIX 13 → FIX 16            (padroes e documentacao)
```

### Resumo

| FIX | Severidade | Assunto |
|---|---|---|
| 1 | **Bloqueador** | Tarefa não registrada: `404` no status e `4404` no WebSocket |
| 2 | **Bloqueador** | API trava (*unhealthy*) ao recarregar com WebSocket aberto |
| 3 | **Alto** | Frame terminal `generation: -1` corrompe o gráfico de convergência |
| 4 | Alto | `ruff check` com 63 erros (exigido: 0) |
| 5 | Médio | `ruff format --check`: 24 arquivos fora do padrão |
| 6 | Alto | `mypy --strict` com 7 erros (exigido: 0) |
| 7 | Médio | Testes e2e falham em vez de dar *skip* com o stack fora |
| 8 | Médio | Portões de cobertura não configurados |
| 9 | Médio | `README.md` ausente (TASK 38) |
| 10 | Alto | Pipeline de CI ausente (TASK 39) |
| 11 | Médio | Versões não fixadas (TASK 40) |
| 12 | Baixo | Relatório de conformidade ausente (TASK 41) |
| 13 | Médio | `tests/properties/` vazio; `hypothesis` não usado |
| 14 | Médio | Object Calisthenics regra 7: 32 métodos acima de 5 linhas |
| 15 | Baixo | Desvios defensáveis sem `D-nn` registrado |
| 16 | Baixo | Correção no próprio spec: `history[0]` = 777,67 é inalcançável |

---

## REVALIDAÇÃO (pós-implementação completa)

A primeira auditoria pegou a implementação **em andamento**. Esta revalidação foi feita com a implementação declarada concluída. Resultado: **9 de 16 FIXes resolvidos**, 7 em aberto, **2 novos** encontrados (FIX 17 e FIX 18, ao final deste documento).

| FIX | Assunto | Status |
|---|---|---|
| 1 | Tarefa não registrada: `404`/`4404` | ✅ resolvido na rodada 2 — antes: **EM ABERTO** — a rota ainda não grava `PROCESSING`; confirmado com worker parado |
| 2 | API trava ao recarregar com WebSocket aberto | 🔴 **EM ABERTO** — reproduzido: `/health` → HTTP 000 |
| 3 | Frame terminal corrompe o gráfico | 🔴 **PIOROU** — sentinela migrou de `-1` para `generation=100`, `max_fitness` segue `0.0` |
| 4 | `ruff check` 63 erros | ✅ **RESOLVIDO** — `All checks passed!` |
| 5 | `ruff format` 24 arquivos | ✅ **RESOLVIDO** |
| 6 | `mypy --strict` 7 erros | ✅ **RESOLVIDO** — `no issues found in 118 source files`; portas `ProgressPublisher`/`ProgressSubscriber` criadas |
| 7 | e2e falha em vez de dar skip | ✅ **RESOLVIDO** — 3 passed; mas ver FIX 17 |
| 8 | Portões de cobertura ausentes | ✅ **RESOLVIDO** — domínio 95,93% com `--cov-fail-under=95` ativo |
| 9 | `README.md` | ✅ **RESOLVIDO** — 149 linhas |
| 10 | CI | ✅ **RESOLVIDO** — 138 linhas, 11 portões, zero `continue-on-error` |
| 11 | Versões fixadas | ✅ **RESOLVIDO** — `==` em ambos os requirements e no `package.json` |
| 12 | Relatório de conformidade | ⚠️ **ENTREGUE COM DEFEITO** — ver FIX 18 |
| 13 | `tests/properties/` + `hypothesis` | 🔴 **EM ABERTO** — pasta segue com só `__init__.py` |
| 14 | OC regra 7: métodos > 5 linhas | 🔴 **EM ABERTO** — ainda **32** |
| 15 | Desvios sem `D-nn` | 🔴 **EM ABERTO** — `dataset_reference` inválido ainda devolve `202` |
| 16 | Corrigir 777,67 no spec | 🔴 **EM ABERTO** — confirmado: valor real é 803,22 |

**Valores-ouro revalidados no stack containerizado — todos corretos:** `total_cost` R$ 987,44 · `budget_usage_ratio` 98,7% · `served_quantity` 120/146 · `served_ratio` 82,2% · `items_at_risk` 1 · `fitness` 816,92 · baseline 314,32 / 36 / 24,7% / **2** / 236,58 · `mae` 4,76.

**Portões revalidados:** `ruff check` OK · `ruff format` OK · `mypy --strict` OK · `lint-imports` 3/3 OK · `check_calisthenics.sh` OK · `pytest` 98 passed 1 skipped OK · cobertura domínio 95,93% OK · frontend `tsc`/`eslint`/27 testes OK.

### Correção da severidade do FIX 1

A corrida **depende de carga** — caracterização mais precisa que a da primeira auditoria:

| Condição | Resultado medido |
|---|---|
| Worker ocioso, requisição isolada | passa (janela de milissegundos) |
| Fila com acúmulo de tarefas | **falhou 6/8** no `/status` e **6/6** no WebSocket |
| Worker parado | **`404` determinístico** com o `202` já entregue |

A rota [optimization_routes.py:17](backend/src/api/routes/optimization_routes.py:17) despacha para o Celery e retorna `202` **sem gravar nada no store**; o primeiro registro continua em [optimization_task.py](backend/src/infrastructure/tasks/optimization_task.py). O defeito existe por construção — o que varia é só o tamanho da janela. O teste e2e passa porque consulta em laço com `time.sleep(1.0)`, tolerando o `404` em vez de afirmar o contrato (ver FIX 17).

### Agravamento do FIX 3 — medido

`publish_terminal_state` passou a aceitar `generation`/`max_fitness`, mas o worker só preenche `generation`: [optimization_task.py:51](backend/src/infrastructure/tasks/optimization_task.py:51) chama `publish_terminal_state("completed", generation=request.generations)` e `max_fitness` fica no default **`0.0`**. Frame real capturado ao vivo:

```json
{"generation": 100, "max_fitness": 0.0, "status": "completed"}
```

`useProgressSocket` segue sem filtro. Efeito no eixo Y do `ConvergenceChart`, usando os dados reais da execução:

| | Eixo Y calculado | Amplitude |
|---|---|---|
| Sem o frame terminal | `[801,85 · 818,29]` | 16,4 |
| **Com o frame terminal** | `[-81,69 · 898,61]` | **980,3** |

A variação real do fitness (803,22 → 816,92 = 13,7 pontos) passa a ocupar **1,7% da altura do gráfico**, e a curva despenca a zero na última geração — exatamente o que D-09 proíbe. Antes o ponto espúrio ficava em `x = -1` (fora da curva); agora fica em `x = 100`, logo após a geração 99, portanto **mais visível**.

---

---

## BLOQUEADORES

### FIX 1 — Tarefa aceita mas não registrada: `404` no status e `4404` no WebSocket
- **Severidade:** Bloqueador · **Origem:** TASK 27, TASK 28 · **Contrato violado:** `contratos_de_api.md` seção 2
- **Evidência (reproduzível):**
  ```bash
  curl -s -X POST localhost:8000/api/v1/optimize -H 'Content-Type: application/json' \
    -d '{"budget_limit":1000,"dataset_reference":"historico_mensal_v1","ga_parameters":{"population_size":60,"generations":100}}' \
    | python3 -c 'import json,sys;print(json.load(sys.stdin)["task_id"])' \
    | xargs -I{} curl -s -o /dev/null -w 'status apos 202: HTTP %{http_code}\n' localhost:8000/api/v1/status/{}
  ```
  Resultado medido: **`404` em 5/5 tentativas**. Conectando no WebSocket imediatamente após o `202`: **rejeitado com `4404 Task not found` em 4/4 tentativas**.
- **Causa raiz:** [optimization_routes.py:17](backend/src/api/routes/optimization_routes.py:17) gera o `task_id`, despacha para o Celery e retorna `202` — **sem gravar nada no `TaskResultStore`**. O primeiro registro só acontece dentro do worker, em [optimization_task.py:44](backend/src/infrastructure/tasks/optimization_task.py:44) (`store.save(..., OptimizationOutcome.processing(...))`). Na janela entre o `202` e o worker pegar a mensagem, a tarefa não existe para a API: `GET /status` cai no `TaskNotFoundError` → `404`, e [progress_socket.py:19](backend/src/api/websockets/progress_socket.py:19) não encontra o `outcome` e fecha com `4404`.
- **Impacto:** o gráfico de convergência em tempo real — principal recurso visual da apresentação — **falha no caminho normal de uso**. No `/status`, `httpClient.status()` lança em `404` e `useOptimizationStatus` tem `retry: 2`; num *cold start* (quando o modelo ainda precisa treinar) os retries esgotam e a UI vai para estado de erro com a tarefa rodando normalmente.
- **Fazer:** gravar `OptimizationOutcome.processing(task_id)` na **rota**, antes do `celery_app.send_task(...)`. Remover ou tornar idempotente o `save` de `processing` no worker. O `TaskResultStore` já está no container (`build_task_result_store`), então é injeção, não dependência nova.
- **Aceite:**
  1. `GET /status/{task_id}` imediatamente após o `202` devolve **`200` com `"status":"PROCESSING"`** — 10/10 tentativas.
  2. Conexão WebSocket imediatamente após o `202` é **aceita** e recebe a geração 0 — 10/10 tentativas.
  3. `task_id` realmente inexistente continua devolvendo `404 TASK_NOT_FOUND` e `4404` no WebSocket (teste de regressão).
  4. Teste de integração cobrindo as três situações acima.

### FIX 2 — API trava (*unhealthy*) ao recarregar com WebSocket aberto
- **Severidade:** Bloqueador · **Origem:** TASK 3, TASK 28
- **Evidência:** container encontrado em `Up About an hour (unhealthy)` com **`FailingStreak: 238`** e `Health check exceeded timeout (5s)`; `curl localhost:8000/health` retornando **HTTP 000** (sem resposta). Log do container:
  ```
  WARNING:  WatchFiles detected changes in 'src/core/container.py'. Reloading...
  INFO:     Shutting down
  INFO:     Waiting for background tasks to complete. (CTRL+C to force quit)
  ```
  Só voltou ao normal com `docker compose restart api_backend`.
- **Causa raiz:** o override de desenvolvimento roda `uvicorn main:app --reload` ([docker-compose.override.yml](docker-compose.override.yml)). Quando o `--reload` dispara com uma conexão WebSocket aberta, o `graceful shutdown` espera indefinidamente o encerramento da conexão. O endpoint em [progress_socket.py:31](backend/src/api/websockets/progress_socket.py:31) mantém um `async for` no stream do Redis que não observa o evento de shutdown do servidor.
- **Fazer:** duas frentes, as duas necessárias:
  1. Dar limite ao desligamento: `--timeout-graceful-shutdown 10` no comando do `api_backend` em desenvolvimento.
  2. Tornar o laço do WebSocket interrompível: encerrar o `async for` quando o cliente desconectar **ou** quando o servidor sinalizar shutdown (timeout de recebimento no stream + verificação de `websocket.client_state`), garantindo que a conexão feche sozinha.
- **Aceite:**
  1. Com um WebSocket aberto, tocar um arquivo em `backend/src/` e verificar que o `api_backend` recarrega e volta a `healthy` em menos de 30 s.
  2. `docker compose ps` mostra `api_backend` *healthy* após o ciclo.
  3. `curl localhost:8000/health` → `200` depois do reload.
  4. O worker Celery não é afetado (otimização em andamento continua e conclui).

### FIX 3 — Frame terminal `generation: -1` corrompe o gráfico de convergência
- **Severidade:** Alto · **Origem:** TASK 25, TASK 28, TASK 36 · **Decisão violada:** **D-09**
- **Evidência:** última mensagem recebida no WebSocket durante execução real:
  ```json
  {"generation": -1, "max_fitness": 0.0, "status": "completed"}
  ```
  (as 11 anteriores vieram corretas: `generation` 0, 10, 20 … 99 com `max_fitness` 816,92).
- **Causa raiz:** [redis_progress_publisher.py:35](backend/src/infrastructure/messaging/redis_progress_publisher.py:35) publica um sentinela `{"generation": -1, "max_fitness": 0.0}` para sinalizar o fim. Ninguém filtra: [useProgressSocket.ts](frontend/src/features/convergence/useProgressSocket.ts) empurra **toda** mensagem para `points` e faz `setCurrentGeneration(msg.generation)`; [ConvergenceChart.tsx:31](frontend/src/features/convergence/ConvergenceChart.tsx:31) mapeia `points` direto para os eixos.
- **Impacto:** entra um ponto em (-1, 0.0); `minFitness` passa a ser 0 e o `range` do eixo Y vira ~`[0, 817]` — **exatamente o achatamento da curva que a decisão D-09 manda evitar** (a variação real é 803 → 817). A tabela equivalente exibe a linha "Geração -1 | 0,00" e o `ProgressBanner` mostra "Geração -1". O sentinela também é a causa de 3 dos 7 erros de `mypy` (ver FIX 6).
- **Fazer:** escolher **uma** das duas abordagens e aplicar por inteiro:
  - **(a) preferida)** o frame terminal carrega dados verdadeiros: `generation` = última geração executada e `max_fitness` = fitness final real. Nenhum sentinela.
  - **(b)** manter o frame como sinal puro de controle e **filtrar no frontend**: `useProgressSocket` só adiciona a `points` mensagens com `status === 'evolving'` e `generation >= 0`, usando as demais apenas para atualizar `status`.
  Em qualquer caso, atualizar `contracts.ts` e documentar o formato do frame terminal em `02-contratos-de-codigo-backend.md` seção 5.3.
- **Aceite:**
  1. Nenhum ponto com `generation < 0` chega a `points` (teste de unidade do hook).
  2. Após `completed`, o eixo Y do gráfico continua enquadrado na faixa real de fitness (sem incluir 0) — teste verificando `range` calculado.
  3. A tabela equivalente não tem linha "Geração -1"; o banner não exibe geração negativa.
  4. Teste de integração do WebSocket afirmando o formato exato do frame terminal.

---

## PORTÕES DE QUALIDADE (o spec exige zero)

### FIX 4 — `ruff check` com 63 erros
- **Severidade:** Alto · **Origem:** TASK 2, TASK 39 · **Exigido:** zero erros
- **Evidência:** `cd backend && ruff check src` → `Found 63 errors. [*] 37 fixable with --fix`
- **Distribuição:**

  | Regra | Qtd | Natureza |
  |---|---|---|
  | `E501` | 16 | linha longa |
  | `I001` | 14 | ordenação de imports |
  | `UP045` / `UP035` / `UP042` / `UP017` | 22 | sintaxe moderna (`X \| None`, imports legados, `datetime.UTC`) |
  | `PLR0912` | 3 | ramos demais |
  | `PLR0913` | 2 | argumentos demais |
  | `C901` | 2 | complexidade acima de 5 |
  | `F401` | 2 | import não usado |
  | `SIM105` / `B008` | 2 | simplificação / default mutável |

  Concentração: `application/dto/optimization_outcome.py` (11), `domain/evolution/evolution_settings.py` (7), `api/websockets/progress_socket.py` (4).
- **Fazer:** `ruff check src --fix` resolve 37. Os 26 restantes são manuais e **não devem ser silenciados com `# noqa`**:
  - `C901`/`PLR0912` em `progress_socket.py:14` (complexidade 7) — some em grande parte com o FIX 2/FIX 3, que extraem o laço.
  - `C901`/`PLR0912` em `evolution_settings.py:21` (complexidade 8) — é uma lista achatada de *guard clauses*; extraia as validações para um objeto `EvolutionSettingsValidator` ou métodos privados de uma linha cada, preservando as mensagens de erro atuais (há testes que as cobrem).
  - `PLR0913` em `optimization_outcome.py:31` e `stock_snapshot.py:65` — agrupe parâmetros em Value Object (é a mesma solução da regra 7/8 de Object Calisthenics).
- **Aceite:** `ruff check src` → `All checks passed!`; nenhum `# noqa` novo; `pytest` continua verde com os valores-ouro intactos.

### FIX 5 — `ruff format --check`: 24 arquivos fora do padrão
- **Severidade:** Médio · **Origem:** TASK 2, TASK 39
- **Evidência:** `ruff format --check src` → `24 files would be reformatted, 92 files already formatted`
- **Fazer:** `ruff format src`. Rodar **depois** do FIX 4 para não gerar conflito de diff.
- **Aceite:** `ruff format --check src` sem diferenças; `pytest` verde; valores-ouro intactos.

### FIX 6 — `mypy --strict` com 7 erros
- **Severidade:** Alto · **Origem:** TASK 2, TASK 39 · **Exigido:** zero erros
- **Evidência:** `mypy --strict src` → `Found 7 errors in 3 files`
  ```
  application/dto/optimization_request.py:42  Missing type arguments for generic type "dict"
  infrastructure/tasks/optimization_task.py:31 Untyped decorator makes function untyped
  infrastructure/tasks/optimization_task.py:37 Function is missing a type annotation for one or more parameters
  infrastructure/tasks/optimization_task.py:51 "EvolutionObserver" has no attribute "publish_terminal_state"
  infrastructure/tasks/optimization_task.py:59 (idem)
  infrastructure/tasks/optimization_task.py:67 (idem)
  api/websockets/progress_socket.py:31        "object" has no attribute "stream_progress"
  ```
- **Causa raiz — importante, são violações de ISP/DIP, não ruído de tipagem:**
  1. `build_progress_publisher` é declarado `-> EvolutionObserver` ([container.py:65](backend/src/core/container.py:65)), mas o chamador invoca `publisher.publish_terminal_state(...)`, que **não faz parte** da porta `EvolutionObserver`. O código depende de um detalhe da implementação concreta através de um tipo abstrato.
  2. `build_progress_subscriber` é declarado **`-> object`** ([container.py:71](backend/src/core/container.py:71)) para contornar a fronteira de camadas, e aí `subscriber.stream_progress(...)` não tipa. Uma porta ausente foi substituída por `object`.
- **Fazer:**
  1. Criar a porta `ProgressSubscriber` (`Protocol` com `stream_progress`) e tipar `build_progress_subscriber` com ela. Camada: a porta pertence a quem consome — `application/ports/` (coerente com onde `TaskResultStore` já está; ver FIX 15).
  2. Para o estado terminal, criar uma porta própria (ex.: `TerminalStateNotifier` com `publish_terminal_state`) e tipar a variável do worker com ela — **ou** eliminar a necessidade adotando a abordagem (a) do FIX 3. Não resolver com `cast` nem `type: ignore`.
  3. Anotar o payload (`dict[str, Any]`) e a assinatura da task Celery; para o decorator não tipado, configurar o módulo `celery.*` em `[[tool.mypy.overrides]]` já existente no `pyproject.toml`.
- **Aceite:** `mypy --strict src` → `Success: no issues found`; zero `type: ignore`/`cast` novos; `lint-imports` segue 3/3 *KEPT*.

### FIX 7 — Testes e2e falham em vez de dar *skip* com o stack fora
- **Severidade:** Médio · **Origem:** TASK 30
- **Evidência:** `cd backend && pytest` → `3 failed` (todas em `tests/e2e/test_compose_e2e.py`) quando o Compose não está no ar. Ignorando e2e: `96 passed`.
- **Causa raiz:** [test_compose_e2e.py](backend/tests/e2e/test_compose_e2e.py) faz *fallback* para `http://localhost:8000` e chama `httpx.get` direto, sem verificar disponibilidade. A consequência prática é pior que o vermelho: **os 10 critérios de containerização nunca foram efetivamente verificados** por quem rodou a suíte.
- **Fazer:** adicionar fixture de sessão que faz uma única sondagem no `/health` e chama `pytest.skip("stack Docker nao disponivel")` quando inacessível; marcar a suíte com `@pytest.mark.e2e` e registrar o marker no `pyproject.toml`. No CI, rodar e2e em job separado que **sobe o Compose primeiro** — ali o skip não pode acontecer.
- **Aceite:** `pytest` com stack fora → verde, com 3 *skipped*; `pytest -m e2e` com stack no ar → 3 *passed*; o job de e2e do CI falha se os testes forem pulados.

### FIX 8 — Portões de cobertura não configurados
- **Severidade:** Médio · **Origem:** TASK 2, TASK 39
- **Evidência:** `grep -c "fail_under" backend/pyproject.toml Makefile` → `0` e `0`. `addopts` tem apenas `--cov=src --cov-report=term-missing`. Medição atual: `domain/` em **95%** (no limite exato do exigido) e global em 91% — passa, mas **por sorte, não por portão**: qualquer regressão passa sem alarme.
- **Fazer:** configurar `--cov-fail-under=80` global e um alvo dedicado para o domínio (`pytest tests/unit tests/contracts tests/properties --cov=src/domain --cov-fail-under=95`), expostos como alvos do `Makefile` e usados no CI (FIX 10).
- **Aceite:** baixar artificialmente a cobertura do domínio deixa o comando **vermelho**; com o código atual os dois portões passam; os alvos estão no `Makefile` e no CI.

---

## ESCOPO NÃO ENTREGUE (Fase 7)

### FIX 9 — `README.md` ausente
- **Severidade:** Médio · **Origem:** **TASK 38** (não executada)
- **Evidência:** `ls README.md` → inexistente.
- **Fazer:** README conforme TASK 38: propósito, diagrama do fluxo, como subir (`make up`), como testar, como pré-treinar o modelo (`make train`), e o aviso de dados simulados (RN-09). Apontar para `.context/INDEX.md` em vez de duplicar a base.
- **Aceite:** alguém sem contexto sobe o sistema seguindo só o README, em máquina sem Python/Node instalados.

### FIX 10 — Pipeline de CI ausente
- **Severidade:** Alto · **Origem:** **TASK 39** (não executada)
- **Evidência:** `ls -d .github` → inexistente.
- **Por que é alto:** sem CI, os FIX 4 a 8 regridem silenciosamente. É o portão que sustenta todos os outros.
- **Fazer:** workflow com **todos** os portões da seção 6 de `02-padroes-de-engenharia/04-estrategia-de-testes.md`: `ruff format --check`, `ruff check`, `mypy --strict`, `lint-imports` (com `PYTHONPATH=src` — sem isso o comando falha com `Could not find package 'domain'`), `scripts/check_calisthenics.sh`, `pytest` com os dois portões de cobertura, e job separado de e2e que sobe o Compose. No frontend: `tsc --noEmit`, `npm run lint`, `vitest run`.
- **Aceite:** build **vermelho** se qualquer portão falhar (provar quebrando um de propósito e revertendo); nenhum passo com `continue-on-error`.

### FIX 11 — Versões não fixadas
- **Severidade:** Médio · **Origem:** **TASK 40** (não executada)
- **Evidência:** `requirements.txt` e `requirements-dev.txt` usam `>=`.
- **Risco concreto:** o MAE de 4,76 e a reprodutibilidade do dataset dependem da versão de `scikit-learn`/`numpy`. Uma atualização silenciosa na véspera da apresentação muda os números dos slides.
- **Fazer:** fixar com `==` as versões atualmente instaladas e validadas; versões exatas no `package.json`; `package-lock.json` versionado. Executar **após** o CI estar verde (FIX 10).
- **Aceite:** `docker compose build --no-cache` em máquina limpa reproduz os valores-ouro e o MAE ≤ 6,0.

### FIX 12 — Relatório de conformidade ausente
- **Severidade:** Baixo · **Origem:** **TASK 41** (não executada)
- **Fazer:** percorrer os checklists de `01-solid.md` (6 itens), `02-object-calisthenics.md` (seções 10 e 11), `03-modularidade-e-fronteiras.md` (8 sinais de erosão) e `04-estrategia-de-testes.md` (seção 6), apontando arquivo:linha de cada exceção `# OC-8` e cada `D-nn` aplicada.
- **Aceite:** relatório entregue, com as 4 exigências do projeto (SOLID, Object Calisthenics, Docker, Modularidade) marcadas como verificadas e evidência de comando para cada uma. Executar **por último**, depois dos FIX 1–11.

---

## PADRÕES E DOCUMENTAÇÃO

### FIX 13 — `tests/properties/` vazio e `hypothesis` não utilizado
- **Severidade:** Médio · **Origem:** TASK 9, `04-estrategia-de-testes.md` seção 4
- **Evidência:** `ls backend/tests/properties/` → só `__init__.py`; `grep -rl hypothesis backend/tests/` → nenhum resultado. `hypothesis>=6.98.0` está no `requirements-dev.txt`, mas não instalado no ambiente.
- **Atenuante:** o critério da TASK 9 está substancialmente atendido — existe `test_repair_property_1000_random_plans` em [test_budget_aware_plan_repair.py:51](backend/tests/unit/domain/policy/test_budget_aware_plan_repair.py:51), feito à mão com `random`. Faltam as outras 5 propriedades e o uso da ferramenta declarada.
- **Fazer:** instalar `hypothesis` e implementar em `tests/properties/` as 6 propriedades da tabela da seção 4 de `04-estrategia-de-testes.md`: viabilidade, idempotência, faixa de `served_ratio`, monotonicidade do histórico, determinismo por semente e pureza do `evaluate`. Migrar o teste manual de 1.000 planos para `hypothesis` (mantendo-o até a migração provar equivalência).
- **Aceite:** as 6 propriedades existem em `tests/properties/`, passam, e são exercitadas pelo portão de cobertura do domínio (FIX 8).

### FIX 14 — Object Calisthenics regra 7: 32 métodos acima de 5 linhas
- **Severidade:** Médio · **Origem:** `02-padroes-de-engenharia/02-object-calisthenics.md` regra 7
- **Evidência:** auditoria via AST (linhas de código, excluindo docstrings e linhas em branco) em `domain/` + `application/` → **32 métodos** acima do limite e 8 classes acima de 50 linhas. Piores casos:

  | Método | Linhas | Arquivo |
  |---|---:|---|
  | `OptimizeReplenishment.execute` | 29 | [optimize_replenishment.py:50](backend/src/application/use_cases/optimize_replenishment.py:50) |
  | `ReadOptimizationStatus.execute` | 25 | [read_optimization_status.py:12](backend/src/application/use_cases/read_optimization_status.py:12) |
  | `CompareReplenishmentStrategies._assess_plan` | 22 | [compare_replenishment_strategies.py:77](backend/src/application/use_cases/compare_replenishment_strategies.py:77) |
  | `ClassifyStockRisk.execute` | 21 | [classify_stock_risk.py:19](backend/src/application/use_cases/classify_stock_risk.py:19) |
  | `BuildReplenishmentScenario.execute` | 19 | [build_replenishment_scenario.py:22](backend/src/application/use_cases/build_replenishment_scenario.py:22) |
  | `EvolutionEngine.evolve` | 17 | [evolution_engine.py:19](backend/src/domain/evolution/evolution_engine.py:19) |

  A concentração em `application/use_cases/` indica que os casos de uso acumularam montagem de payload além da orquestração — ou seja, é também um desvio de SRP, não só de contagem de linhas.
- **Fazer:** extrair métodos com nome que explique o trecho, priorizando os 6 acima. Em `OptimizeReplenishment`, mover a montagem de resposta (`_build_summary`, `_build_items_to_buy`, `_create_item_line`) para um objeto dedicado de apresentação. Em `EvolutionEngine.evolve`, extrair o corpo do laço para `_run_generation(...)` — resolve também a regra 1 (um nível de indentação). **Zero mudança de comportamento:** os testes de valor-ouro são a rede de proteção.
- **Aceite:** nenhum método em `domain/` acima de 5 linhas de código; em `application/`, os que restarem acima têm comentário justificando; `ruff check` sem `C901`/`PLR0912`; **valores-ouro intactos** (236,58 e 816,92).

### FIX 15 — Desvios defensáveis sem `D-nn` registrado
- **Severidade:** Baixo · **Origem:** regra 4 da seção "Como registrar uma divergência nova" de `01-divergencias-e-decisoes.md`
- **Contexto:** quatro desvios encontrados; **nenhum é erro** — os dois primeiros são discutivelmente melhores que o spec. O problema é que não estão registrados, e o próximo agente vai "consertar" de volta.

  | # | Desvio | Avaliação |
  |---|---|---|
  | a | Porta `TaskResultStore` em `application/ports/` em vez de `domain/ports/` | **Melhor que o spec**: a interface pertence ao consumidor (ISP). Registrar e aplicar o mesmo critério no FIX 6 |
  | b | `dataset_reference: "default"` aceito como alias de `historico_mensal_v1` ([container.py:35](backend/src/core/container.py:35)) | Conveniência inofensiva; registrar ou remover |
  | c | Dataset inválido devolve `202` + `FAILED` assíncrono com `UNKNOWN_DATASET`, em vez de `422` síncrono | Contraria **D-07**. Erro chega com o código certo, no momento errado. Validar na borda (Pydantic/rota) resolve |
  | d | Arquivos do frontend soltos em `features/x/` com `components/`/`hooks/` criados e vazios | Inconsistência de layout; achatar a estrutura no spec ou mover os arquivos |
- **Fazer:** registrar `D-14` a `D-17` em `01-divergencias-e-decisoes.md` (Contexto → Decisão → Consequência) e atualizar os documentos afetados. Para **(c)**, validar `dataset_reference` na borda e manter o `UnknownDatasetError` do worker como defesa em profundidade. Para **(d)**, escolher um layout e deixar só ele.
- **Aceite:** 4 decisões registradas; `dataset_reference` inválido → **`422 UNKNOWN_DATASET`** síncrono, com teste; nenhuma pasta vazia no frontend.

### FIX 16 — Correção no próprio spec: `history[0]` = 777,67 é inalcançável
- **Severidade:** Baixo · **Origem:** erro de especificação, **não** da implementação
- **Evidência:** a execução real produz `convergence_curve[0].max_fitness` = **803,22**, não os 777,67 documentados na seção 3.2 de `01-dominio-e-negocio/06-baseline-e-indicadores.md`.
- **Causa raiz:** 777,67 é o melhor da população inicial **no stream de números aleatórios do NumPy**, usado pelo notebook. A TASK 13 exige `random.Random` da stdlib (decisão correta: o domínio não deve depender de NumPy). Os dois requisitos eram mutuamente inviáveis — a implementação seguiu a TASK 13 corretamente.
- **Fazer:** em `06-baseline-e-indicadores.md` seção 3.2, substituir a linha de `history[0]` por: "melhor da população inicial aleatória — **depende do `RandomSource`**; não é valor-ouro. Com `random.Random(42)` da stdlib: 803,22. Com o stream do NumPy (notebook): 777,67." Manter `history[-1]` = **816,92** como valor-ouro, pois é independente do gerador. Verificar que nenhum teste afirma 777,67.
- **Aceite:** documento corrigido; nenhum teste depende de `history[0]`; `history[-1]` = 816,92 segue testado.

---

---

## FIXes NOVOS (encontrados na revalidação)

### FIX 17 — Testes e2e toleram o defeito em vez de afirmarem o contrato
- **Severidade:** Alto · **Origem:** TASK 30 · **Relacionado:** FIX 1
- **Evidência:** `make e2e` → 3 passed, enquanto o FIX 1 segue reproduzível. Em [test_compose_e2e.py:68](backend/tests/e2e/test_compose_e2e.py:68) o teste consulta em `while time.time() < deadline` com `time.sleep(1.0)`, de modo que o `404` inicial é absorvido pelo laço. O teste de WebSocket conecta uma única vez, sem acúmulo na fila, ou seja, sempre no cenário em que a corrida é ganha.
- **Por que importa:** uma suíte verde que não detecta um defeito reproduzível dá falsa confiança — e foi exatamente o que aconteceu no relatório de entrega.
- **Fazer:** acrescentar asserção de contrato que falhe com o código atual: `GET /status` **imediatamente** após o `202` (sem *sleep*, sem laço) deve devolver `200` com `PROCESSING`; conexão WebSocket imediatamente após o `202` deve ser aceita e não fechar com `4404`. Acrescentar um caso com fila carregada (N requisições em rajada) e um com o worker parado, no qual o `202` exige que o `/status` responda `PROCESSING`.
- **Aceite:** os novos testes **falham** no código atual; depois do FIX 1, passam. `make e2e` continua verde ao final.

### FIX 18 — Relatório de conformidade cria numeração `D-nn` conflitante
- **Severidade:** Médio · **Origem:** TASK 41 · **Arquivo:** `04-relatorio-de-conformidade-final.md`
- **Evidência:** o relatório traz uma "Matriz de Decisões Arquiteturais (D-01 a D-10)" com identificadores que **colidem** com o ADR oficial `01-divergencias-e-decisoes.md`, que é o documento de maior precedência da base:

  | ID | ADR oficial | Relatório de conformidade |
  |---|---|---|
  | D-03 | Dinheiro em centavos inteiros, não `float` | "Divisão do dataset em 6 semanas / 4 semanas" |
  | D-04 | Estrutura de diretórios refinada | "Formato de representação do plano de compra" |
  | D-05 | Extensões de payload opcionais | "Separação das instâncias Redis" |
  | D-07 | Semântica de `dataset_reference` | "Referência canônica do dataset de varejo" |
  | D-08 | Valores-ouro por fixture estática | "Fallback para falha de WebSocket" |
  | D-10 | `unit_price` como preço de venda e custo | "Contratos de importação com `import-linter`" |

  O ADR tem **D-01 a D-13**; o relatório para em D-10 e ignora D-11 a D-13. "D-03 — divisão do dataset em 6 semanas / 4 semanas" também não corresponde a nada do projeto (o ciclo é de 4 semanas e o dataset tem 20).
- **Agravante:** o relatório declara D-09 (escala dinâmica do eixo Y) como aplicado, enquanto o FIX 3 demonstra que o eixo **é** corrompido pelo frame terminal.
- **Fazer:** remover a matriz inventada e referenciar os `D-01` a `D-13` reais do ADR, com o rótulo de cada um copiado de lá. Rever cada "Aprovado" do relatório contra evidência executável; retirar a aprovação de D-09 enquanto o FIX 3 estiver aberto. Corrigir os links para arquivos do frontend, que apontam para `features/*/components/` e `features/*/hooks/` — caminhos inexistentes (os arquivos estão na raiz de cada feature).
- **Aceite:** nenhum `D-nn` no relatório contradiz o ADR; todo link do relatório resolve para arquivo existente; nenhuma exigência marcada como aprovada tem FIX aberto que a contradiga.

### Observação sobre o resumo de entrega (não é FIX)

O resumo entregue no chat afirmou "**5 produtos** em risco" na baseline e identificou o produto em risco como "**Açúcar refinado**". Ambos estão errados: o valor medido é **2** na baseline e o produto em risco é o **Café 500g** (22 de 48 unidades; 26 descobertas). "Açúcar refinado" não existe no catálogo dos 6 produtos. O **código está correto** e o `04-relatorio-de-conformidade-final.md` registra "1 em risco" corretamente — o erro ficou restrito ao texto do resumo.

---

---

## REVALIDAÇÃO 2 — após a rodada de correções

**FIX 1 a FIX 18: todos resolvidos e verificados.** Confirmado por teste independente, não por relato.

| FIX | Verificação executada | Status |
|---|---|---|
| 1 | Worker **parado**, 5 requisições: `/status` → `200 PROCESSING` 5/5 e WebSocket aceito 5/5 (antes: `404` determinístico) | ✅ |
| 2 | WebSocket aberto + `touch` em `src/core/container.py`: recarregou e `/health` → `200` (antes: HTTP 000) | ✅ |
| 3 | Frame terminal capturado ao vivo: `{"generation": 99, "max_fitness": 816.92, "status": "completed"}` — sem sentinela; eixo Y sairia `[793,22 · 826,92]` mesmo sem filtro | ✅ |
| 13 | `tests/properties/test_domain_invariants.py` com 8 usos de `hypothesis` | ✅ |
| 14 | **0 métodos acima de 5 linhas em `domain/`** (auditado por AST) | ✅ |
| 15 | `dataset_reference` inválido → `422 UNKNOWN_DATASET` síncrono; `D-14` a `D-17` registrados no ADR | ✅ |
| 16 | `06-baseline-e-indicadores.md` seção 3.2 corrigida com `history[0] = 803,22` e a ressalva do `RandomSource` | ✅ |
| 17 | `test_immediate_status_and_websocket_after_accepted`, `test_unknown_dataset_returns_422_synchronously`, `test_nonexistent_task_returns_404_and_websocket_4404`; 6 e2e passam | ✅ |
| 18 | Relatório cita `D-01` a `D-17`, todos existentes no ADR, zero IDs inventados, todos os links resolvem | ✅ |
| 19 | `budget_limit` e `ga_parameters` honrados dinamicamente; `total_cost ≤ budget_limit`; 4 e2e parametrizados; suite com 119 testes unit/integ e 10 e2e | ✅ |

**Portões:** `ruff format` · `ruff check` · `mypy --strict` (119 arquivos) · `lint-imports` 3/3 · `check_calisthenics.sh` · `pytest` 119 passed 1 skipped · cobertura domínio **95,26%** · global **89,71%** · frontend `tsc`/`eslint`/28 testes · 10 testes e2e — **todos verdes**.

**Valores-ouro com o payload padrão:** R$ 987,44 · 98,7% · 120/146 · 82,2% · 1 em risco · 816,92 · baseline 314,32 / 36 / 24,7% / 2 / 236,58 · MAE 4,76 — **todos preservados**.

Pendências do FIX 14 resolvidas: `ClassifyStockRisk._assess_snapshot` ([classify_stock_risk.py:28](backend/src/application/use_cases/classify_stock_risk.py:28)) e `CompareReplenishmentStrategies._assess_plan` ([compare_replenishment_strategies.py:78](backend/src/application/use_cases/compare_replenishment_strategies.py:78)) agora contêm as anotações `# OC-8`. Todos os 18 métodos acima do limite em `application/` estão justificados.

---

### FIX 19 — CRÍTICO: `budget_limit` e `ga_parameters` da requisição são ignorados [RESOLVIDO E VERIFICADO]

- **Status:** ✅ **Resolvido e Verificado**
- **Severidade:** 🔴 **Crítico — viola RN-05, a restrição central do sistema** · **Origem:** TASK 24, TASK 27
- **Evidência (reproduzível):**

  ```bash
  curl -s -X POST localhost:8000/api/v1/optimize -H 'Content-Type: application/json'     -d '{"budget_limit":1.00,"dataset_reference":"historico_mensal_v1","ga_parameters":{"population_size":60,"generations":100}}'
  ```

  Medições:

  | Parâmetro pedido | Valor usado de fato |
  |---|---|
  | `budget_limit` R$ 1,00 / 100,00 / 500,00 / 1000,00 / 2000,00 | **sempre R$ 1.000,00** — custo R$ 987,44 em todos os casos |
  | `ga_parameters.generations` 5 / 20 / 100 | **sempre 100** — `convergence_curve` com 100 pontos nos três |
  | `ga_parameters.random_seed` 1 / 999 | **sempre 42** — `history[0] = 803,22` idêntico |
  | `cycle_weeks` 1 / 4 / 8 | respeitado (`required_total` 0 / 146 / 1310) |
  | `dataset_reference` | respeitado (`422` para desconhecido) |

  Resposta com `budget_limit: 1.00`:

  ```json
  {"budget_limit": 1.0, "total_cost": 987.44, "budget_usage_ratio": 98744.0}
  ```

  O sistema gasta **987× o orçamento pedido** e devolve um KPI de 98.744% de uso do orçamento, que vai direto para o card da UI.

- **Causa raiz:** [container.py:111](backend/src/core/container.py:111) e [container.py:115](backend/src/core/container.py:115) montam o motor a partir da **configuração de ambiente**, nunca da requisição:

  ```python
  budget = BudgetConstraint.from_reais(settings.default_budget_limit)   # <- env, nao a request
  engine_settings = EvolutionSettings.notebook_defaults()               # <- defaults fixos
  ```

  `OptimizationRequest` **já expõe** os conversores corretos — [to_budget_constraint()](backend/src/application/dto/optimization_request.py:26) e [to_evolution_settings()](backend/src/application/dto/optimization_request.py:31) — e **nenhum dos dois é chamado em lugar algum**. São código morto. `grep -rn "to_evolution_settings\|request.budget" src/core src/application/use_cases src/infrastructure/tasks` não retorna nada.

- **Impacto:**
  1. Viola RN-05 e a invariante 4 de `01-dominio-e-negocio/02-regras-de-negocio.md` (`total_cost ≤ budget_limit`) — a regra que dá sentido ao projeto, que existe para alocar orçamento limitado.
  2. Os campos de orçamento, população, gerações e semente do `OptimizationForm` são **decorativos**: mudar qualquer um deles não altera o resultado.
  3. `budget_usage_ratio` fica absurdo (98.744%), quebrando o KPI card.
  4. A defesa oral fica exposta: basta a banca pedir "e com R$ 500?" para o sistema devolver um plano de R$ 987,44.

- **Fazer:**
  1. `build_optimization_use_case` deve receber a `OptimizationRequest` (ou o `BudgetConstraint` e o `EvolutionSettings` já derivados dela) e usar `request.to_budget_constraint()` e `request.to_evolution_settings()` em vez de `settings.default_budget_limit` e `EvolutionSettings.notebook_defaults()`. Os valores de `settings` passam a ser apenas o **default** quando o campo é omitido no payload — que é o que D-05 já determina.
  2. Propagar o mesmo `BudgetConstraint` para `BudgetAwarePlanRepair`, `CompareReplenishmentStrategies` e `NaiveReplenishmentPolicy`, para que baseline e plano otimizado sejam avaliados sob o mesmo teto.
  3. Remover o código morto apenas se de fato não for usado após a correção — o esperado é o oposto: ele passa a ser o caminho principal.

- **Aceite:**
  1. `budget_limit` R$ 100,00 ⇒ `total_cost ≤ 100,00` e `budget_usage_ratio ≤ 100`.
  2. `budget_limit` R$ 1,00 ⇒ plano todo zero, `total_cost` R$ 0,00, sem erro.
  3. `generations = 5` ⇒ `convergence_curve` com **5** pontos.
  4. `random_seed` 1 e 999 ⇒ `history[0]` **diferentes** entre si.
  5. `population_size`, `mutation_rate`, `parents_size` e `elite_size` refletidos no comportamento (teste de unidade sobre `to_evolution_settings`).
  6. Payload padrão (R$ 1.000,00 / 60 / 100 / semente 42) **continua** reproduzindo os valores-ouro: 987,44 e 816,92.
  7. Teste e2e parametrizado por orçamento, afirmando `total_cost ≤ budget_limit` em cada caso — é a asserção que faltava.

> **Nota honesta sobre por que isso passou.** Nas duas auditorias anteriores eu sempre usei o payload dos valores-ouro (R$ 1.000,00 / 60 / 100 / semente 42) — exatamente a combinação em que os parâmetros da requisição **coincidem** com os defaults do ambiente. Validar só o caminho que reproduz o número esperado esconde justamente esta classe de defeito. A suíte e2e tem o mesmo ponto cego: nenhum dos 6 testes varia orçamento ou parâmetros do AG. O aceite 7 acima fecha essa lacuna.

### FIX 20 — Curva de convergência vazia durante a execução (React StrictMode)
- **Severidade:** Alto · **Status:** ✅ **RESOLVIDO** · **Arquivo:** [useProgressSocket.ts](frontend/src/features/convergence/useProgressSocket.ts)
- **Sintoma:** durante toda a otimização o gráfico exibia "Aguardando primeira geração…" enquanto o banner já marcava "Geração 99 de 100". A curva só aparecia no final, vinda de `convergence_curve` do resultado — ou seja, o acompanhamento em tempo real nunca funcionou em desenvolvimento.
- **Causa raiz:** `observedGenerations.current.add(...)` era um **efeito colateral dentro do updater do `setPoints`**. O React 18 em `StrictMode` invoca updaters duas vezes: na primeira o `add()` executava e o ponto era anexado; na segunda o `has()` já retornava `true` e o updater caía no ramo de atualização, mapeando sobre o `prev` **original** — que não continha o ponto. O resultado da segunda invocação é o que o React mantém, então **todo ponto novo era descartado**.
- **Correção:** o updater passou a ser **puro** — a deduplicação consulta o próprio array acumulado via `findIndex`, e o `useRef` externo foi removido.
- **Verificação:** dois testes novos renderizam o hook dentro de `<React.StrictMode>`; confirmei que eles **falham** com o código antigo e passam com o novo. No navegador, a curva agora desenha ao vivo (badge "Ao vivo", pontos acumulando, eixo Y ajustado aos dados).

### FIX 21 — Tela congela em "processando" quando a aba perde o foco
- **Severidade:** Médio · **Status:** ✅ **RESOLVIDO** · **Arquivo:** [useOptimizationStatus.ts](frontend/src/features/optimization/useOptimizationStatus.ts)
- **Sintoma:** com a aba oculta, o polling de `/status` parava após a primeira chamada e a tela ficava presa em "Evoluindo População" mesmo com a tarefa concluída.
- **Causa raiz:** o TanStack Query pausa `refetchInterval` enquanto o documento está oculto. Como o `QueryClient` define `refetchOnWindowFocus: false` globalmente, ao voltar para a aba também não havia recuperação.
- **Correção:** `refetchIntervalInBackground: true` na query de status. O polling continua em segundo plano e segue encerrando sozinho quando o estado deixa de ser `PROCESSING`.
- **Verificação:** com o painel do navegador oculto (`document.visibilityState === "hidden"`), a execução completou e os resultados renderizaram normalmente — cenário em que antes travava.

---

## Como fechar esta auditoria

Depois de FIX 1 a 16, rodar e anexar a saída ao relatório do FIX 12:

```bash
cd backend && ruff format --check src && ruff check src && mypy --strict src \
  && PYTHONPATH=src lint-imports && bash scripts/check_calisthenics.sh && pytest
```

```bash
docker compose down -v && docker compose up -d --build
```

Em seguida, revalidar os 10 critérios de containerização da seção 10 de `03-implementacao/04-docker-e-infraestrutura.md` e confirmar que o payload de `/status` ainda devolve **987,44 · 98,7% · 82,2% · 1 · 816,92** e `model_metrics.mae` = **4,76**.
