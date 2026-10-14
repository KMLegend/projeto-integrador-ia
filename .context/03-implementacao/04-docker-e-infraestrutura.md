---
id: 04-docker-e-infraestrutura
dominio: implementacao
palavras-chave: docker, docker compose, containerizacao, dockerfile, redis, celery, uvicorn, nginx, healthcheck, volumes, variaveis de ambiente, makefile
fonte-da-verdade: .context/00-arquitetura-tecnica/infraestrutura_docker.md
depende-de: [01-estrutura-de-diretorios, 02-contratos-de-codigo-backend]
---

# Docker e Infraestrutura

Exigência **não-negociável** nº 3: `docker compose up` sobe o sistema inteiro e a otimização roda ponta a ponta **sem Python ou Node instalados no host**.

---

## 1. Serviços

| Serviço | Imagem base | Comando (dev) | Porta | Papel |
|---|---|---|---|---|
| `frontend` | `node:20-alpine` | `npm run dev -- --host 0.0.0.0` | 5173 | UI React/Vite |
| `api_backend` | `python:3.11-slim` | `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` | 8000 | REST + WebSocket |
| `celery_worker` | **mesma imagem** do `api_backend` | `celery -A core.celery_app worker --loglevel=info -Q optimization_queue` | — | Executa ML + AG |
| `redis_broker` | `redis:7-alpine` | padrão | 6379 (interno) | Broker + resultados + Pub/Sub |
| `model_trainer` | mesma imagem do backend | `python -m infrastructure.forecasting.model_store --train` | — | One-shot (profile `tools`): pré-treina o modelo |

Rede única: `ai_inventory_network` (bridge). Comunicação por hostname: `redis://redis_broker:6379/0`.

**Decisão importante:** `celery_worker` reaproveita a imagem do `api_backend` (mesma base de código e mesmas dependências de IA) — está na arquitetura e evita divergência de versão de sklearn entre quem treina e quem prevê.

## 2. `docker-compose.yml` (produção/base)

```yaml
name: gestao-preditiva-estoque

services:
  frontend:
    build:
      context: ./frontend
      target: runtime
    ports: ["3000:80"]
    depends_on:
      api_backend: { condition: service_healthy }
    networks: [ai_inventory_network]

  api_backend:
    build: &backend_build
      context: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    environment: &backend_env
      REDIS_URL: redis://redis_broker:6379/0
      REDIS_RESULT_URL: redis://redis_broker:6379/1
      MODEL_STORE_PATH: /app/models/demand_forecaster.joblib
      DEFAULT_BUDGET_LIMIT: "1000.00"
      DEFAULT_CYCLE_WEEKS: "4"
      DEFAULT_RANDOM_SEED: "42"
      PROGRESS_EVERY_GENERATIONS: "10"
      CORS_ORIGINS: http://localhost:3000,http://localhost:5173
      LOG_LEVEL: INFO
      PYTHONPATH: /app/src
    volumes: [model_store:/app/models]
    ports: ["8000:8000"]
    depends_on:
      redis_broker: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
    networks: [ai_inventory_network]

  celery_worker:
    build: *backend_build
    command: celery -A core.celery_app worker --loglevel=info -Q optimization_queue --concurrency=2
    environment: *backend_env
    volumes: [model_store:/app/models]
    depends_on:
      redis_broker: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "celery", "-A", "core.celery_app", "inspect", "ping", "-d", "celery@$$HOSTNAME"]
      interval: 20s
      timeout: 10s
      retries: 5
      start_period: 30s
    networks: [ai_inventory_network]

  redis_broker:
    image: redis:7-alpine
    command: redis-server --appendonly no --save ""
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
    networks: [ai_inventory_network]

  model_trainer:
    build: *backend_build
    command: python -m infrastructure.forecasting.model_store --train
    environment: *backend_env
    volumes: [model_store:/app/models]
    profiles: ["tools"]
    networks: [ai_inventory_network]

volumes:
  model_store:

networks:
  ai_inventory_network:
    driver: bridge
```

## 3. `docker-compose.override.yml` (desenvolvimento)

Carregado automaticamente pelo `docker compose up`; adiciona hot reload e monta o código:

```yaml
services:
  frontend:
    build:
      context: ./frontend
      target: development
    command: npm run dev -- --host 0.0.0.0
    ports: ["5173:5173"]
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
      - /app/node_modules          # anonimo: nao sobrescreve deps do container

  api_backend:
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes: ["./backend/src:/app/src"]

  celery_worker:
    command: watchfiles --filter python "celery -A core.celery_app worker --loglevel=info -Q optimization_queue" /app/src
    volumes: ["./backend/src:/app/src"]
```

> O worker Celery **não** recarrega sozinho ao mudar o código; sem `watchfiles`, a equipe edita o AG e continua rodando o código antigo — causa clássica de horas perdidas em depuração.

## 4. `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src
WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .

FROM base AS runtime
COPY src/ ./src/
RUN useradd --create-home --uid 1000 appuser \
 && mkdir -p /app/models && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

* `requirements.txt` copiado **antes** do código: cache de camada preservado (build rápido ao editar código).
* Estágio `runtime` roda como **usuário não-root**.
* `PYTHONPATH=/app/src` permite `from domain...` sem prefixo `src.`.

## 5. `frontend/Dockerfile`

```dockerfile
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM development AS build
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

`nginx.conf` precisa de duas coisas:

1. Fallback de SPA: `try_files $uri $uri/ /index.html;`
2. Proxy de API e WebSocket (evita CORS em produção):

```nginx
location /api/ {
    proxy_pass http://api_backend:8000;
}
location /ws/ {
    proxy_pass http://api_backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 600s;
}
```

Sem `Upgrade`/`Connection`, o WebSocket de progresso falha silenciosamente atrás do Nginx.

## 6. Dependências

`backend/requirements.txt` (compartilhado entre API e worker, conforme a arquitetura):

```
fastapi
uvicorn[standard]
pydantic
pydantic-settings
celery
redis
websockets
scikit-learn
pandas
numpy
joblib
```

`backend/requirements-dev.txt`:

```
pytest
pytest-cov
pytest-asyncio
hypothesis
httpx
mypy
ruff
import-linter
watchfiles
```

Versões: fixe com `==` antes da entrega final (reprodutibilidade da banca); durante o desenvolvimento, `>=` é aceitável.

> **DEAP/PyGAD não entram** — o AG é implementação própria (decisão D-02).

## 7. Variáveis de ambiente (`.env.example`)

```
REDIS_URL=redis://redis_broker:6379/0
REDIS_RESULT_URL=redis://redis_broker:6379/1
MODEL_STORE_PATH=/app/models/demand_forecaster.joblib
DEFAULT_BUDGET_LIMIT=1000.00
DEFAULT_CYCLE_WEEKS=4
DEFAULT_RANDOM_SEED=42
PROGRESS_EVERY_GENERATIONS=10
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
LOG_LEVEL=INFO
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

`.env` **não** é versionado; `.env.example` é. Não há segredo real nesta PoC — se um dia houver (credencial de ERP), vai para variável de ambiente, nunca para o código ou para `.context/`.

## 8. Persistência do modelo

O artefato `joblib` vive no volume nomeado `model_store`, montado em `api_backend` e `celery_worker`:

1. Primeiro uso: se o arquivo não existe, o worker treina, persiste e segue (sem falhar a requisição).
2. Pré-aquecimento explícito: `docker compose --profile tools run --rm model_trainer`.
3. O artefato guarda modelo + ordem das features + semente + MAE + versão do schema.
4. Schema incompatível → descarta e retreina; nunca usa artefato incompatível.
5. `docker compose down -v` apaga o volume: o próximo start retreina. Previsto e aceitável.

## 9. `Makefile`

```makefile
up:        ## Sobe todos os servicos (dev, com hot reload)
	docker compose up --build
down:      ## Derruba e remove volumes
	docker compose down -v
train:     ## Pre-treina o modelo de previsao
	docker compose --profile tools run --rm model_trainer
test:      ## Testes do backend dentro do container
	docker compose run --rm api_backend pytest
lint:      ## Lint, tipos e fronteiras de modulo
	docker compose run --rm api_backend sh -c "ruff check src && mypy --strict src && lint-imports"
logs:      ## Logs do worker
	docker compose logs -f celery_worker
```

## 10. Verificação da containerização (critérios de aceite)

1. `docker compose build` conclui sem erro, partindo de clone limpo.
2. `docker compose up -d` deixa `redis_broker`, `api_backend` e `celery_worker` *healthy*.
3. `curl localhost:8000/health` → `200`.
4. `POST /api/v1/optimize` → `202` com `task_id`.
5. Em até 60 s, `GET /api/v1/status/{task_id}` → `COMPLETED` com plano viável.
6. WebSocket recebe ≥ 2 mensagens de progresso com `generation` crescente.
7. Frontend acessível (5173 em dev, 3000 em produção) e exibindo o resultado.
8. `docker compose down -v && docker compose up` funciona do zero.
9. Nenhum passo exige Python ou Node no host.
10. `docker compose logs` sem traceback não tratado.

## 11. Armadilhas conhecidas

| Problema | Causa | Solução |
|---|---|---|
| Worker roda código antigo | Falta de hot reload no Celery | `watchfiles` no override de dev |
| `ModuleNotFoundError: domain` | `PYTHONPATH` não aponta para `src` | `PYTHONPATH=/app/src` no Dockerfile e no compose |
| WebSocket cai atrás do Nginx | Headers de upgrade ausentes | Bloco `location /ws/` da seção 5 |
| `node_modules` do host vaza no container | Bind mount sobrescrevendo | Volume anônimo em `/app/node_modules` |
| Worker sobe antes do Redis | Sem `condition: service_healthy` | Healthcheck + `depends_on` com condição |
| Modelo retreinado em cada tarefa | Sem cache/volume | Volume `model_store` + cache em processo |
| Build lento a cada mudança de código | `COPY . .` antes do `pip install` | Copiar `requirements.txt` primeiro |
| CORS bloqueando o dev | Origem do Vite ausente | `CORS_ORIGINS` com `localhost:5173` |
