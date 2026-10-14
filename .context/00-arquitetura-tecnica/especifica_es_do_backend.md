# Especificações Técnicas: Backend (Python + FastAPI)

## 1. Estrutura do FastAPI
A API deve ser construída seguindo princípios de Clean Architecture, separando rotas (routers), lógica de negócios (services) e esquemas de validação (Pydantic).

*   **Framework:** FastAPI
*   **Servidor ASGI:** Uvicorn
*   **Validação de Dados:** Pydantic (Modelos para entrada de orçamento, limites, restrições).

## 2. Processamento em Background (Celery + Redis)
Algoritmos Genéticos não podem rodar na thread principal da requisição HTTP devido ao tempo de execução (segundos a minutos).

*   **Broker:** Redis.
*   **Backend de Resultados:** Redis.
*   **Workers:** O Celery deve ser configurado para consumir tarefas da fila `optimization_queue`.
*   **Integração Celery-FastAPI:** A API apenas despacha a tarefa (`task.delay()`) e retorna o `task_id`.

## 3. WebSockets para Tempo Real
O módulo de IA (Worker) deve emitir atualizações de estado durante o treinamento (ex: a cada 10 gerações do AG).
*   A API FastAPI deve expor um endpoint WebSocket (ex: `/ws/progress/{task_id}`).
*   O Redis Pub/Sub pode ser utilizado para transmitir o progresso do Worker do Celery para a thread do FastAPI que mantém a conexão WebSocket com o cliente.

## 4. Estrutura de Diretórios Sugerida (AI Context)
```text
/backend
  /api
    /routes
    /websockets
  /core
    /config.py
    /celery_app.py
  /schemas
    /requests.py
    /responses.py
  /ai_engine
    /genetic_algorithm (Placeholder para lógica de fitness e cromossomos)
    /forecasting (Placeholder para modelos preditivos)
  main.py
```