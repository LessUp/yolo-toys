#!/bin/bash
# Development script for YOLO-Toys

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

show_help() {
    cat << EOF
YOLO-Toys Development Helper

Usage: ./scripts/dev.sh [command]

Commands:
    setup       Setup development environment
    run         Run development server
    test        Run tests
    lint        Run non-mutating lint and format checks
    typecheck   Run BasedPyright type checking
    format      Format code
    hooks       Run all pre-commit hooks
    docker      Build and run Docker container
    clean       Clean cache and temporary files
    help        Show this help

EOF
}

setup() {
    echo "Setting up development environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pre-commit install
    echo "Setup complete!"
}

run_dev() {
    echo "Starting development server..."
    source .venv/bin/activate 2>/dev/null || true
    export SKIP_WARMUP=1
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

run_tests() {
    echo "Running tests..."
    source .venv/bin/activate 2>/dev/null || true
    export SKIP_WARMUP=1
    python3 -m pytest tests/ -v "${@:2}"
}

run_lint() {
    echo "Running linters..."
    ruff check .
    ruff format --check .
}

run_format() {
    echo "Formatting code..."
    ruff check --fix .
    ruff format .
}

run_typecheck() {
    echo "Running type checker..."
    basedpyright
}

run_hooks() {
    echo "Running pre-commit hooks..."
    pre-commit run --all-files
}

docker_run() {
    echo "Building and running Docker container..."
    docker compose up --build
}

clean() {
    echo "Cleaning up..."
    rm -rf .ruff_cache
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf app/__pycache__
    rm -rf tests/__pycache__
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    echo "Clean complete!"
}

# Main
case "${1:-help}" in
    setup) setup ;;
    run) run_dev ;;
    test) run_tests "$@" ;;
    lint) run_lint ;;
    typecheck) run_typecheck ;;
    format) run_format ;;
    hooks) run_hooks ;;
    docker) docker_run ;;
    clean) clean ;;
    help|*) show_help ;;
esac
