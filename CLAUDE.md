# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YOLO-Toys is a multi-model real-time vision recognition platform supporting YOLO, HuggingFace Transformers, and multimodal models via WebSocket streaming.

## Build, Test & Lint Commands

```bash
make lint      # Run Ruff lint + format check
make format    # Auto-fix with Ruff
make test      # Run pytest (SKIP_WARMUP=1 is set automatically)
make run       # Start uvicorn with --reload
```

## Code Style

- Line length: 100 characters
- Python 3.11+
- Ruff handles linting and formatting (pyproject.toml config)

## Architecture

- **Strategy Pattern**: `BaseHandler` abstract class with model-specific implementations in `app/handlers/`
- **Registry Pattern**: `MODEL_REGISTRY` + `HandlerRegistry` for model-to-handler mapping
- Adding a new model: Create handler extending `BaseHandler`, register in `_CATEGORY_HANDLER_MAP` and `MODEL_REGISTRY`

## Environment Variables

Key variables for local dev (see `app/config.py` for full list):
- `SKIP_WARMUP=1` — Skip model warmup for faster startup
- `MODEL_NAME` — Default model (e.g., `yolov8s.pt`)
- `DEVICE` — `cpu`, `mps`, or `cuda:0`
