.PHONY: help install install-dev dev test lint typecheck format docker-build docker-up docker-down sandbox-build update clean

PYTHON := python
UV := uv
SA_PORT ?= 8080

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Installation ────────────────────────────────────────────────────────────

install: ## Install package and runtime dependencies
	$(UV) pip install -e .

install-dev: ## Install with dev dependencies
	$(UV) pip install -e ".[dev,pdf]"

sync: ## Sync all dependencies from lockfile
	$(UV) sync

lock: ## Regenerate uv.lock
	$(UV) lock

# ─── Development ─────────────────────────────────────────────────────────────

dev: ## Start API server in dev mode (auto-reload)
	$(UV) run uvicorn security_agent.api.app:create_app \
		--factory --host 0.0.0.0 --port $(SA_PORT) --reload

ui-install: ## Install React UI dependencies
	cd src/security_agent/ui && npm install

ui-build: ## Build React UI for production
	cd src/security_agent/ui && npm run build

ui-dev: ## Run Vite dev server for UI (port 5173 with proxy to 8080)
	cd src/security_agent/ui && npm run dev

# ─── Quality ─────────────────────────────────────────────────────────────────

test: ## Run all tests
	$(UV) run pytest tests/ -v --tb=short

test-unit: ## Run unit tests only
	$(UV) run pytest tests/unit/ -v

test-integration: ## Run integration tests only
	$(UV) run pytest tests/integration/ -v

lint: ## Run linter (ruff)
	$(UV) run ruff check src/ scripts/

format: ## Format code (ruff)
	$(UV) run ruff format src/ scripts/

typecheck: ## Run type checker (mypy)
	$(UV) run mypy src/

coverage: ## Run tests with coverage report
	$(UV) run coverage run -m pytest tests/unit/
	$(UV) run coverage report -m

# ─── Docker & Sandbox ────────────────────────────────────────────────────────

docker-build: ## Build all Docker images
	docker compose -f docker/docker-compose.yml build

sandbox-build: ## Build only the Kali sandbox image
	docker build -f docker/Dockerfile.sandbox -t security-agent-sandbox:latest docker/

docker-up: ## Start full stack (API + sandbox + DB)
	docker compose -f docker/docker-compose.yml up -d

docker-up-dev: ## Start stack in dev mode
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up

docker-down: ## Stop all containers
	docker compose -f docker/docker-compose.yml down

docker-logs: ## Tail container logs
	docker compose -f docker/docker-compose.yml logs -f

# ─── Version Management ───────────────────────────────────────────────────────

update: ## Update all components to latest
	$(UV) run python scripts/update.py update all

update-component: ## Update a single component: make update-component COMPONENT=tools.nmap
	$(UV) run python scripts/update.py update $(COMPONENT)

rollback: ## Rollback: make rollback COMPONENT=providers.anthropic VERSION=1.2.0
	$(UV) run python scripts/update.py rollback $(COMPONENT) $(VERSION)

versions: ## List current versions of all components
	$(UV) run python scripts/update.py list

# ─── Cleanup ─────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/

clean-data: ## Remove runtime data (DB, artifacts, reports)
	rm -rf data/
