.PHONY: up down train test test-domain-cov test-global-cov lint calisthenics logs e2e frontend-test frontend-lint ci

up:        ## Sobe todos os servicos (dev, com hot reload)
	docker compose up --build

down:      ## Derruba e remove volumes
	docker compose down -v

train:     ## Pre-treina o modelo de previsao
	docker compose --profile tools run --rm model_trainer

test:      ## Testes do backend dentro do container
	docker compose run --rm api_backend pytest tests/unit tests/integration

test-domain-cov: ## Verifica cobertura minima de 95% no dominio
	docker compose run --rm api_backend pytest tests/unit tests/integration -o addopts="" --cov=domain --cov-fail-under=95

test-global-cov: ## Verifica cobertura minima de 80% global
	docker compose run --rm api_backend pytest tests/unit tests/integration --cov=src --cov-fail-under=80

lint:      ## Lint, formatacao, tipos e fronteiras de modulo do backend
	docker compose run --rm api_backend sh -c "ruff format --check src && ruff check src && mypy --strict src && PYTHONPATH=src lint-imports"

calisthenics: ## Verifica regras de Object Calisthenics
	docker compose run --rm api_backend bash /app/scripts/check_calisthenics.sh

frontend-lint: ## Verificacao de tipos e lint do frontend
	docker compose run --rm frontend sh -c "npx tsc --noEmit && npm run lint"

frontend-test: ## Testes unitarios e componentes do frontend
	docker compose run --rm frontend npm test -- --run

e2e:       ## Executa os testes ponta a ponta no compose
	docker compose run --rm api_backend pytest tests/e2e

ci: lint calisthenics test-domain-cov test-global-cov frontend-lint frontend-test e2e ## Executa todos os portoes de qualidade do projeto
	@echo "Todos os portoes de CI foram verificados com sucesso!"

logs:      ## Logs do worker Celery
	docker compose logs -f celery_worker
