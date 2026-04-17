# AGENTS.md

This file provides instructions for AI programming assistants (Claude Code, Cursor, etc.) working with this repository.

---

# Project Philosophy: Spec-Driven Development (SDD)

This project strictly follows **Spec-Driven Development** paradigm. All code implementation must use the `/specs` directory documents as the **Single Source of Truth**.

---

## Directory Context

| Directory | Purpose |
|-----------|---------|
| `/specs/product/` | Product feature definitions and acceptance criteria |
| `/specs/rfc/` | Technical design documents (RFCs) |
| `/specs/api/` | API interface definitions (OpenAPI, etc.) |
| `/specs/db/` | Database model definitions |
| `/specs/testing/` | BDD test case specifications |

---

## AI Agent Workflow Instructions

When you (AI) are asked to develop a new feature, modify existing functionality, or fix a bug, **you must strictly follow this workflow, skipping no steps**:

### Step 1: Review Specs

- Before writing any code, first read relevant product documents, RFCs, and API definitions in `/specs`
- If user instructions conflict with existing Specs, **stop coding immediately**, point out the conflict, and ask if Specs need to be updated first

### Step 2: Spec-First Update

- If this is a new feature or requires changes to existing interfaces/database structures, **you must first propose modifications or create corresponding Spec documents** (e.g., `openapi.yaml` or RFC documents)
- Only proceed to code implementation after user confirms Spec changes

### Step 3: Implementation

- When writing code, you must **100% comply with Spec definitions** (including variable naming, API paths, data types, status codes, etc.)
- Do not add features not defined in Specs (No Gold-Plating)

### Step 4: Test Against Spec

- Write unit and integration tests based on acceptance criteria in `/specs`
- Ensure test cases cover all edge cases described in Specs

---

## Project Overview

YOLO-Toys is a multi-model real-time vision recognition platform supporting YOLO, HuggingFace Transformers, and multimodal models via WebSocket streaming.

**Tech Stack:** Python 3.11+, FastAPI, Ultralytics YOLOv8, HuggingFace Transformers, PyTorch, OpenCV

---

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

---

## Code Style

- **Line length:** 100 characters
- **Python version:** 3.11+
- **Linter/formatter:** Ruff (configured in `pyproject.toml`)
- **Import style:** Absolute imports from `app.*`
- **Type hints:** Required for function signatures
- **Docstrings:** Use for public functions and classes (Chinese or English acceptable)

---

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

| File | Purpose |
|------|---------|
| `app/handlers/base.py` | Abstract base class defining `load()` and `infer()` interface |
| `app/handlers/registry.py` | `MODEL_REGISTRY` dict and `HandlerRegistry` class for model-to-handler mapping |
| `app/handlers/*.py` | Concrete handler implementations |

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

| Pattern | Implementation |
|---------|----------------|
| **Registry Pattern** | `MODEL_REGISTRY` maps model IDs to metadata; `HandlerRegistry` resolves model ID to handler instance |
| **Dependency Injection** | Device string passed to handlers at construction |
| **Template Method** | `BaseHandler` provides `make_result()`, `_to_device()`, `_model_to_device()` utilities |
| **Lazy Loading** | Models loaded on first inference, then cached in `ModelManager._cache` |

---

## Adding a New Model

1. **Create Handler** — Extend `BaseHandler` in `app/handlers/`
2. **Implement Methods:**
   - `load(model_id)` → `(model, processor)`
   - `infer(model, processor, image, **params)` → `dict`
3. **Register Model:**
   - Add category constant to `ModelCategory` in `registry.py`
   - Add to `_CATEGORY_HANDLER_MAP`
   - Add metadata to `MODEL_REGISTRY`
4. **Add Tests** — Verify model loading and inference

**IMPORTANT:** Before adding any new model, update `/specs/rfc/` with the technical design and `/specs/api/` with the API changes.

---

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

---

## Testing

Tests are located in `tests/test_api.py` and use pytest with FastAPI's `TestClient`.

**Key test patterns:**

- `monkeypatch.setattr()` for mocking `model_manager.infer()`
- `client.websocket_connect()` for WebSocket tests
- Fixtures handle `SKIP_WARMUP=1` automatically

---

## Code Generation Rules

- **Any API changes exposed externally must synchronize modifications to `/specs/api/openapi.yaml`**
- **If uncertain about technical details, consult `/specs/rfc/` architecture agreements — do not fabricate design patterns**
- **All new features require corresponding Spec documents before implementation**

---

## Common Tasks

### Modify Default Inference Parameters

Edit `app/config.py` defaults or pass query params to `/infer`.

### Add New REST Endpoint

1. Update `/specs/api/openapi.yaml` with endpoint definition
2. Add route handler in `app/routes.py`
3. Add response schema in `app/schemas.py` if needed
4. Add test in `tests/test_api.py`

### Debug Model Loading Issues

- Check `MODEL_REGISTRY` for model ID registration
- Verify handler `load()` method handles import errors gracefully
- Set `SKIP_WARMUP=1` to bypass startup model loading

### Optimize Performance

- Use FP16 (`half=true`) on CUDA devices
- Reduce `imgsz` for faster inference
- Set appropriate `conf` threshold to filter detections
- Use WebSocket for streaming (avoids HTTP overhead)
