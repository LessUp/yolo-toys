PY?=python
PIP?=$(PY) -m pip
UVICORN?=uvicorn
APP=app.main:app
PORT?=8000
HOST?=0.0.0.0
ENV_FILE?=config/.env.example

# Docker configurations
DOCKERFILE?=deployments/docker/Dockerfile
DOCKER_IMAGE?=yolo-toys:latest

.PHONY: help
help:
	@echo "Development Commands:"
	@echo "  install       Install production dependencies"
	@echo "  dev           Install dev dependencies and setup"
	@echo "  run           Run development server with auto-reload"
	@echo "  test          Run test suite"
	@echo "  lint          Run linting checks"
	@echo "  format        Auto-format code"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-build-cuda  Build CUDA (GPU) Docker image"
	@echo "  docker-run    Run Docker container"
	@echo "  compose-up    Start with docker-compose"
	@echo "  compose-down  Stop docker-compose"
	@echo "  compose-monitor  Start with monitoring stack"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean         Clean cache and temporary files"
	@echo "  setup         Setup development environment"

.PHONY: install
install:
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

.PHONY: dev
dev:
	$(PIP) install -r requirements-dev.txt
	pre-commit install

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: format
format:
	ruff check --fix .
	ruff format .

.PHONY: test
test:
	SKIP_WARMUP=1 $(PY) -m pytest

.PHONY: run
run:
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --reload

# Docker commands
.PHONY: docker-build
docker-build:
	docker build -f $(DOCKERFILE) -t $(DOCKER_IMAGE) .

.PHONY: docker-build-cuda
docker-build-cuda:
	docker build -f deployments/docker/Dockerfile.cuda -t yolo-toys:cuda .

.PHONY: docker-run
docker-run:
	docker run --rm -it -p $(PORT):$(PORT) --env-file $(ENV_FILE) $(DOCKER_IMAGE)

.PHONY: compose-up
compose-up:
	docker compose up --build -d

.PHONY: compose-down
compose-down:
	docker compose down --remove-orphans

.PHONY: compose-monitor
compose-monitor:
	docker compose --profile monitoring up --build -d

# Utility commands
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .ruff_cache .pytest_cache htmlcov .coverage

.PHONY: setup
setup:
	@bash scripts/dev.sh setup
