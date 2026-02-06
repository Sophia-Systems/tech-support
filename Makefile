.PHONY: help install dev dev-up dev-down lint format test migrate seed build deploy clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Setup ===

install: ## Install backend + frontend dependencies
	cd backend && uv sync --all-extras
	cd frontend && npm install

# === Development ===

dev-up: ## Start infrastructure services (postgres, redis, langfuse)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres redis langfuse-server

dev-down: ## Stop infrastructure services
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

dev-api: ## Run API server with hot reload
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-worker: ## Run background worker
	cd backend && uv run arq app.workers.ingestion_worker.WorkerSettings

dev-frontend: ## Run frontend dev server
	cd frontend && npm run dev

dev: dev-up ## Start full dev stack (infra + api + worker)
	@echo "Starting API server and worker..."
	@trap 'kill 0' EXIT; \
		$(MAKE) dev-api & \
		$(MAKE) dev-worker & \
		wait

# === Code Quality ===

lint: ## Run linters
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .

format: ## Format code
	cd backend && uv run ruff check --fix .
	cd backend && uv run ruff format .

typecheck: ## Run type checker
	cd backend && uv run pyright

# === Testing ===

test: ## Run all tests
	cd backend && uv run pytest -v

test-unit: ## Run unit tests only
	cd backend && uv run pytest tests/unit -v

test-integration: ## Run integration tests only
	cd backend && uv run pytest tests/integration -v

test-cov: ## Run tests with coverage
	cd backend && uv run pytest --cov=app --cov-report=html

# === Database ===

migrate: ## Run database migrations
	cd backend && uv run alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	cd backend && uv run alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Rollback one migration
	cd backend && uv run alembic downgrade -1

# === Docker ===

build: ## Build all Docker images
	docker compose build

up: ## Start all services (production mode)
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Tail logs for all services
	docker compose logs -f

# === Maintenance ===

clean: ## Clean build artifacts
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	rm -rf frontend/dist frontend/node_modules/.vite
