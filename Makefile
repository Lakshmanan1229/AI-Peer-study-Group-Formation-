# =============================================================================
# AI Peer Study Group Formation System — Makefile
# =============================================================================
# Usage: make <target>
# Run `make help` for a list of all available targets.

.PHONY: help dev install test \
        docker-up docker-down \
        migrate seed lint \
        frontend-install frontend-dev frontend-build

# Default Python / Uvicorn settings (override on the command line as needed)
APP          := app.main:app
HOST         := 0.0.0.0
PORT         := 8000
WORKERS      := 1

# Frontend directory
FRONTEND_DIR := frontend

# Test settings
PYTEST_ARGS  := --cov=app --cov-report=term-missing --cov-report=html -v

# Colour helpers
BOLD  := \033[1m
RESET := \033[0m
GREEN := \033[32m
CYAN  := \033[36m

# ─── Help ─────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "$(BOLD)AI Peer Study Group Formation System$(RESET)"
	@echo "$(CYAN)────────────────────────────────────────────────────────$(RESET)"
	@echo "  $(GREEN)make dev$(RESET)               Start API server with hot-reload (uvicorn)"
	@echo "  $(GREEN)make install$(RESET)           Install Python dependencies"
	@echo "  $(GREEN)make test$(RESET)              Run pytest with coverage report"
	@echo "  $(GREEN)make lint$(RESET)              Run flake8 + black --check + isort --check"
	@echo "  $(GREEN)make migrate$(RESET)           Apply Alembic migrations (upgrade head)"
	@echo "  $(GREEN)make seed$(RESET)              Generate and load synthetic data"
	@echo "  $(GREEN)make docker-up$(RESET)         Build and start all Docker services"
	@echo "  $(GREEN)make docker-down$(RESET)       Stop and remove all Docker containers"
	@echo "  $(GREEN)make frontend-install$(RESET)  Install Node dependencies for the frontend"
	@echo "  $(GREEN)make frontend-dev$(RESET)      Start the Vite development server"
	@echo "  $(GREEN)make frontend-build$(RESET)    Build the React SPA for production"
	@echo "$(CYAN)────────────────────────────────────────────────────────$(RESET)"
	@echo ""

# ─── Backend ──────────────────────────────────────────────────────────────────

## Start the FastAPI development server with auto-reload
dev:
	uvicorn $(APP) --reload --host $(HOST) --port $(PORT) --workers $(WORKERS)

## Install Python dependencies from requirements.txt
install:
	pip install --upgrade pip
	pip install -r requirements.txt

## Run the full test suite with coverage
test:
	pytest $(PYTEST_ARGS)

## Run flake8, black (check mode), and isort (check mode)
lint:
	flake8 app tests
	black --check app tests
	isort --check-only app tests

## Apply all pending Alembic database migrations
migrate:
	alembic upgrade head

## Seed the database with synthetic student data
seed:
	python data_pipeline/generators/synthetic_data.py

# ─── Docker ───────────────────────────────────────────────────────────────────

## Build images and start all services in detached mode
docker-up:
	docker compose up --build -d

## Stop all running services and remove containers
docker-down:
	docker compose down

# ─── Frontend ─────────────────────────────────────────────────────────────────

## Install Node.js dependencies for the React frontend
frontend-install:
	cd $(FRONTEND_DIR) && npm install

## Start the Vite development server for the frontend
frontend-dev:
	cd $(FRONTEND_DIR) && npm run dev

## Build the React SPA for production (outputs to frontend/dist/)
frontend-build:
	cd $(FRONTEND_DIR) && npm run build
