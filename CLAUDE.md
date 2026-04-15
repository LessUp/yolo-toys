# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YOLO-Toys is a multi-model real-time vision recognition platform supporting YOLO, HuggingFace Transformers, and multimodal models via WebSocket streaming.

**Tech Stack:** Python 3.11+, FastAPI, Ultralytics YOLOv8, HuggingFace Transformers, PyTorch, OpenCV

## Development Commands

```bash
# Setup
pip install -r requirements.txt          # Install runtime deps
pip install -r requirements-dev.txt      # Install dev deps (pytest, pre-commit, ruff)
pre-commit install                       # Install git hooks

# Development
make lint                                # Run Ruff lint + format check
make format                              # Auto-fix with Ruff
make test                                # Run pytest (SKIP_WARMUP=1 auto-set)
make run                                 # Start uvicorn with --reload

# Docker
make compose-up                          # Start with docker-compose
make compose-down                        # Stop containers
```

## Code Style

- **Line length:** 100 characters
- **Python version:** 3.11+
- **Linter/formatter:** Ruff (configured in `pyproject.toml`)
- **Import style:** Absolute imports from `app.*`
- **Type hints:** Required for function signatures
- **Docstrings:** Use for public functions and classes (Chinese or English acceptable)

## Architecture

### Strategy Pattern (Model Handlers)

All model inference follows the Strategy Pattern via `BaseHandler`:

```
BaseHandler (abstract)
├── YOLOHandler        # YOLO detection/segmentation/pose
├── DETRHandler        # Facebook DETR
├── OWLViTHandler      # Open-vocabulary detection
├── GroundingDINOHandler  # Text-prompted detection
├── BLIPCaptionHandler # Image captioning
└── BLIPVQAHandler     # Visual question answering
```

**Key files:**
- `app/handlers/base.py` — Abstract base class defining `load()` and `infer()` interface
- `app/handlers/registry.py` — `MODEL_REGISTRY` dict and `HandlerRegistry` class for model-to-handler mapping
- `app/handlers/*.py` — Concrete handler implementations

### Adding a New Model

1. Create handler class extending `BaseHandler` in `app/handlers/`
2. Implement `load(model_id)` → returns `(model, processor)`
3. Implement `infer(model, processor, image, **params)` → returns `dict`
4. Add category constant to `ModelCategory` in `registry.py`
5. Register in `_CATEGORY_HANDLER_MAP` and `MODEL_REGISTRY`

### Request Flow

```
HTTP Request → routes.py → ModelManager.infer()
                            ↓
                     HandlerRegistry.get_handler(model_id)
                            ↓
                     handler.load() [cached] → handler.infer()
                            ↓
                     BaseHandler.make_result() → JSON response
```

### Key Design Patterns

- **Registry Pattern:** `MODEL_REGISTRY` maps model IDs to metadata; `HandlerRegistry` resolves model ID to handler instance
- **Dependency Injection:** Device string passed to handlers at construction
- **Template Method:** `BaseHandler` provides `make_result()`, `_to_device()`, `_model_to_device()` utilities
- **Lazy Loading:** Models loaded on first inference, then cached in `ModelManager._cache`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `MODEL_NAME` | `yolov8s.pt` | Default model ID |
| `CONF_THRESHOLD` | `0.25` | Detection confidence threshold |
| `IOU_THRESHOLD` | `0.45` | NMS IoU threshold |
| `MAX_DET` | `300` | Max detections per frame |
| `DEVICE` | `auto` | Inference device (`cpu`/`cuda:0`/`mps`) |
| `SKIP_WARMUP` | `false` | Skip model warmup on startup |
| `ALLOW_ORIGINS` | `*` | CORS allowed origins |
| `MAX_UPLOAD_MB` | `10` | Max upload size in MB |
| `MAX_CONCURRENCY` | `4` | Max concurrent inference requests |

## Testing

Tests are located in `tests/test_api.py` and use pytest with FastAPI's `TestClient`.

**Key test patterns:**
- `monkeypatch.setattr()` for mocking `model_manager.infer()`
- `client.websocket_connect()` for WebSocket tests
- Fixtures handle `SKIP_WARMUP=1` automatically

## Common Tasks

### Modify Default Inference Parameters

Edit `app/config.py` defaults or pass query params to `/infer`.

### Add New REST Endpoint

1. Add route handler in `app/routes.py`
2. Add response schema in `app/schemas.py` if needed
3. Add test in `tests/test_api.py`

### Debug Model Loading Issues

- Check `MODEL_REGISTRY` for model ID registration
- Verify handler `load()` method handles import errors gracefully
- Set `SKIP_WARMUP=1` to bypass startup model loading

### Optimize Performance

- Use FP16 (`half=true`) on CUDA devices
- Reduce `imgsz` for faster inference
- Set appropriate `conf` threshold to filter detections
- Use WebSocket for streaming (avoids HTTP overhead)
