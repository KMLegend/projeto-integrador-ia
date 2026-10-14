# Infraestrutura e Containerização (Docker Compose)

O ambiente deve ser orquestrado via `docker-compose.yml` contendo os seguintes serviços.

## Serviços (Services Overview)

### 1. `frontend`
*   **Imagem Base:** `node:18-alpine` ou `node:20-alpine`
*   **Comando:** `npm run dev` (em desenvolvimento) ou servir a pasta `dist` via Nginx (produção).
*   **Portas:** Expõe a porta 3000 ou 5173 (Vite).

### 2. `api_backend`
*   **Imagem Base:** `python:3.11-slim`
*   **Comando:** `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
*   **Portas:** Expõe a porta 8000.
*   **Dependências Principais no Dockerfile:** `fastapi`, `uvicorn`, `celery`, `redis`, `pydantic`.

### 3. `celery_worker`
*   **Imagem Base:** Mesma imagem buildada para o `api_backend` (pois compartilha o código base e os modelos de IA).
*   **Comando:** `celery -A core.celery_app worker --loglevel=info`
*   **Dependências Específicas:** `deap` (ou `pygad`), `scikit-learn`, `pandas`, `numpy`. (Devem ser instaladas no requirements.txt compartilhado).

### 4. `redis_broker`
*   **Imagem Base:** `redis:alpine`
*   **Portas:** Expõe 6379 (opcional para debug externo, interno na rede do docker).
*   **Propósito:** Intermediar a comunicação entre a `api_backend` e o `celery_worker`.

## Rede (Network)
Todos os containers devem compartilhar uma rede bridge interna (ex: `ai_inventory_network`) para comunicação via hostname (ex: `redis://redis_broker:6379/0`).