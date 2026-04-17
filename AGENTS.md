# AGENTS.md

This file provides instructions for AI programming assistants working with the YOLO-Toys repository.

---

## Project Overview

YOLO-Toys is a **multi-model real-time vision recognition platform** built with Python 3.11+ and FastAPI. It unifies multiple computer vision models under a single API:

- **YOLOv8** (Ultralytics) - Object detection, segmentation, pose estimation
- **Facebook DETR** - Transformer-based object detection
- **OWL-ViT** - Open-vocabulary zero-shot detection
- **Grounding DINO** - Text-prompted detection
- **BLIP** - Image captioning and visual question answering

### Key Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.115+ |
| Vision Models | Ultralytics YOLOv8, HuggingFace Transformers |
| Runtime | Uvicorn with WebSocket support |
| Device Support | CPU, NVIDIA CUDA, Apple MPS |
| Caching | cachetools (TTL+LRU hybrid) |
| Metrics | Prometheus client |
| Testing | pytest, pytest-asyncio |
| Linting | Ruff |

---

## Development Commands

```bash
# Setup
pip install -r requirements.txt          # Install production dependencies
pip install -r requirements-dev.txt      # Install dev dependencies (pytest, ruff, pre-commit)
pre-commit install                       # Install git hooks

# Development
make run                                 # Start uvicorn with --reload
make test                                # Run pytest (SKIP_WARMUP=1 auto-set)
make lint                                # Run Ruff lint + format check
make format                              # Auto-fix with Ruff

# Docker
make compose-up                          # Start with docker-compose
make compose-down                        # Stop containers
make compose-monitor                     # Start with Prometheus + Grafana
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `MODEL_NAME` | `yolov8s.pt` | Default model ID |
| `CONF_THRESHOLD` | `0.25` | Detection confidence threshold (0.0-1.0) |
| `IOU_THRESHOLD` | `0.45` | NMS IoU threshold (0.0-1.0) |
| `MAX_DET` | `300` | Max detections per frame (1-1000) |
| `DEVICE` | `auto` | Inference device (`cpu`/`cuda:0`/`mps`) |
| `SKIP_WARMUP` | `false` | Skip model warmup at startup |
| `ALLOW_ORIGINS` | `*` | CORS allowed origins |
| `MAX_UPLOAD_MB` | `10` | Max upload size in MB |
| `MAX_CONCURRENCY` | `4` | Max concurrent inference requests |
| `MODEL_CACHE_MAXSIZE` | `10` | Maximum cached models |
| `MODEL_CACHE_TTL` | `3600` | Model cache TTL in seconds |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## Code Organization

```
app/
├── main.py              # FastAPI entry point with lifespan management
├── config.py            # Pydantic Settings for environment variables
├── routes.py            # Router composition (imports from api/)
├── schemas.py           # Pydantic models for API responses
├── model_manager.py     # ModelManager singleton with caching
├── metrics.py           # Prometheus metrics definitions
├── middleware.py        # Custom middleware (rate limit, timeout, security)
├── api/                 # API route modules
│   ├── system.py        # /health, /system/stats, /system/cache/clear
│   ├── models.py        # /models, /models/{id}, /labels
│   ├── inference.py     # /infer, /caption, /vqa
│   ├── websocket.py     # /ws (WebSocket streaming)
│   └── utils.py         # Shared utilities (image validation, parsing)
└── handlers/            # Model handler implementations
    ├── base.py          # BaseHandler abstract class
    ├── registry.py      # HandlerRegistry and MODEL_REGISTRY
    ├── yolo_handler.py  # YOLOHandler for detection/segmentation/pose
    ├── hf_handler.py    # DETRHandler, OWLViTHandler, GroundingDINOHandler
    └── blip_handler.py  # BLIPCaptionHandler, BLIPVQAHandler

tests/
├── conftest.py          # Shared pytest fixtures
└── test_api.py          # API and unit tests

specs/                   # Spec-Driven Development documents
├── api/
│   └── openapi.yaml     # OpenAPI 3.1.0 specification
├── rfc/
│   ├── 0001-core-architecture.md
│   └── 0002-handler-pattern.md
└── testing/
    └── rest-api.feature # BDD test specifications

deployments/
├── docker/
│   ├── Dockerfile       # Multi-stage build (deps/runtime/development)
│   ├── Dockerfile.cuda  # CUDA-enabled variant
│   └── docker-compose.yml
└── monitoring/
    ├── prometheus/
    └── grafana/

frontend/                # Static HTML/JS demo interface
```

---

## Architecture

### Handler Pattern (Strategy Pattern)

All model inference follows a unified interface via `BaseHandler`:

```python
class BaseHandler(ABC):
    @abstractmethod
    def load(self, model_id: str) -> tuple[Any, Any | None]:
        """加载模型，返回 (model, processor)"""
        
    @abstractmethod
    def infer(self, model, processor, image, **params) -> dict:
        """执行推理，返回标准结果字典"""
```

**Handler Registry:**

| Model Category | Handler | Models |
|----------------|---------|--------|
| `yolo_detect` | `YOLOHandler` | yolov8n/s/m/l/x.pt |
| `yolo_segment` | `YOLOHandler` | yolov8n/s/m-seg.pt |
| `yolo_pose` | `YOLOHandler` | yolov8n/s/m-pose.pt |
| `hf_detr` | `DETRHandler` | facebook/detr-resnet-50/101 |
| `hf_owlvit` | `OWLViTHandler` | google/owlvit-base-patch32 |
| `hf_grounding_dino` | `GroundingDINOHandler` | IDEA-Research/grounding-dino-tiny |
| `multimodal_caption` | `BLIPCaptionHandler` | Salesforce/blip-image-captioning-base/large |
| `multimodal_vqa` | `BLIPVQAHandler` | Salesforce/blip-vqa-base |

### Request Flow

```
HTTP/WebSocket Request → routes.py → ModelManager.infer()
                                         ↓
                            HandlerRegistry.get_handler(model_id)
                                         ↓
                            handler.load() [cached] → handler.infer()
                                         ↓
                            BaseHandler.make_result() → JSON response
```

---

## Code Style Guidelines

### Ruff Configuration (pyproject.toml)

- **Line length:** 100 characters
- **Target Python:** 3.11+
- **Quote style:** Double quotes
- **Import style:** Absolute imports from `app.*`

### Key Rules

| Rule Set | Description |
|----------|-------------|
| `E`, `W` | pycodestyle errors and warnings |
| `F` | Pyflakes |
| `I` | isort (import sorting) |
| `UP` | pyupgrade |
| `B` | flake8-bugbear |
| `SIM` | flake8-simplify |
| `C4` | flake8-comprehensions |

**Ignored:**
- `E501` - Line too long (handled by formatter)
- `B008` - Function call in argument defaults (FastAPI File/Query pattern)

### Naming Conventions

- **Handlers:** `*Handler` suffix (e.g., `YOLOHandler`)
- **Private methods:** `_` prefix (e.g., `_to_device`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MODEL_REGISTRY`)
- **Settings:** Lowercase with underscore, alias to UPPER for env vars

---

## Testing Instructions

### Test Organization

Tests are in `tests/test_api.py` using pytest with FastAPI's `TestClient`.

**Key fixtures (from conftest.py):**
- `client` - FastAPI TestClient with SKIP_WARMUP=1
- `image_bytes` - 32x32 PNG test image
- `mock_infer` - Mocked model_manager.infer() with different responses per model type
- `mock_load_model` - Mocked model loading

### Running Tests

```bash
# All tests (with coverage)
make test

# Specific test
pytest tests/test_api.py::test_health_ok -v

# With coverage report
pytest --cov=app --cov-report=html
```

### Test Patterns

```python
# Mocking model_manager
from app.model_manager import model_manager

def test_example(client: TestClient, monkeypatch):
    def fake_infer(*, model_id, image, **kwargs):
        return {"detections": [], "inference_time": 1.0, "task": "detect"}
    
    monkeypatch.setattr(model_manager, "infer", fake_infer)
    # ... test code
```

---

## Adding a New Model

1. **Create Handler** (if new category):
   ```python
   # app/handlers/my_handler.py
   class MyHandler(BaseHandler):
       def load(self, model_id: str) -> tuple[Any, Any | None]:
           ...
       
       def infer(self, model, processor, image, **params) -> dict:
           ...
   ```

2. **Add Category and Register** (in `app/handlers/registry.py`):
   ```python
   class ModelCategory:
       MY_MODEL = "my_model"
   
   _CATEGORY_HANDLER_MAP = {
       ...
       ModelCategory.MY_MODEL: MyHandler,
   }
   
   MODEL_REGISTRY = {
       "my-model-id": {
           "category": ModelCategory.MY_MODEL,
           "name": "My Model",
           "description": "...",
           "speed": "快",
           "accuracy": "高",
       },
   }
   ```

3. **Add Tests** in `tests/test_api.py`

4. **Update OpenAPI spec** in `specs/api/openapi.yaml`

---

## Spec-Driven Development (SDD)

This project follows **Spec-Driven Development**. Before implementing:

1. **Check specs** in `/specs/` directory
2. **Update specs first** for new features (RFCs, OpenAPI changes)
3. **Implement to spec** - code must match spec definitions exactly
4. **Test against spec** - verify acceptance criteria

**Spec Directories:**
- `/specs/product/` - Feature definitions and acceptance criteria
- `/specs/rfc/` - Technical design documents
- `/specs/api/` - API interface definitions
- `/specs/testing/` - BDD test case specifications

---

## Security Considerations

### Existing Safeguards

| Feature | Implementation |
|---------|---------------|
| Path traversal prevention | URL decode + forbidden pattern check in `ModelManager.load_model()` |
| MIME type validation | Magic number check in `validate_image_mime()` |
| File size limits | `MAX_UPLOAD_MB` enforces upload limits |
| Rate limiting | `RateLimitMiddleware` (per-IP, in-memory) |
| Security headers | `SecurityHeadersMiddleware` adds X-Frame-Options, etc. |
| CORS protection | Configurable `ALLOW_ORIGINS` |
| Model ID validation | Rejects `../`, `..\`, `/`, `\`, `\x00` patterns |

### Security Testing

Security tests are included in `test_api.py`:
- Path traversal attacks (`../etc/passwd`)
- URL-encoded path traversal (`%2e%2e%2f`)
- Double URL-encoding attacks
- Invalid model ID patterns

---

## Metrics and Observability

Prometheus metrics are exposed at `/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `yolo_toys_info` | Info | Application info (version, framework) |
| `inference_requests_total` | Counter | Total inference requests (labels: model, task, status) |
| `inference_duration_seconds` | Histogram | Inference latency |
| `inference_input_size_bytes` | Histogram | Input image file sizes |
| `model_cache_size` | Gauge | Current number of cached models |
| `model_memory_usage_ratio` | Gauge | Memory usage ratio |
| `websocket_connections_active` | Gauge | Active WebSocket connections |
| `http_request_duration_seconds` | Histogram | HTTP request duration |

---

## API Endpoints

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check + system info |
| `/models` | GET | List all models by category |
| `/models/{id}` | GET | Get model info |
| `/labels` | GET | Get class labels for model |
| `/infer` | POST | General inference (detect/segment/pose/VQA) |
| `/caption` | POST | Image captioning |
| `/vqa` | POST | Visual question answering |
| `/metrics` | GET | Prometheus metrics |
| `/system/stats` | GET | System statistics |
| `/system/cache/clear` | POST | Clear model cache |

### WebSocket Protocol

Connect to `/ws?model={model_id}&conf=0.25&...`

**Client → Server:**
- Binary: JPEG/PNG image frame
- Text (JSON): `{"type": "config", "model": "...", "conf": 0.5}`

**Server → Client:**
- `{"type": "ready", "model": "...", "version": "..."}`
- `{"type": "result", "data": {...}}`
- `{"type": "config_updated", "model": "..."}`
- `{"type": "error", "detail": "..."}`

---

## Configuration System

Settings use Pydantic Settings with environment variable aliases:

```python
class AppSettings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    
    port: int = Field(default=8000, alias="PORT")
    model_name: str = Field(default="yolov8s.pt", alias="MODEL_NAME")
    # ...
```

Access via `get_settings()` (cached singleton):

```python
from app.config import get_settings

settings = get_settings()
print(settings.port)  # 8000 or from env
```

---

## Deployment

### Docker Multi-Stage Build

- **deps stage:** Install Python dependencies
- **runtime stage:** Production image (non-root user)
- **development stage:** Includes pytest, uvicorn --reload

### Production Checklist

- [ ] Set `SKIP_WARMUP=false` for warmup on startup
- [ ] Configure `MAX_CONCURRENCY` based on GPU memory
- [ ] Set proper `ALLOW_ORIGINS` (don't use `*` in production)
- [ ] Enable monitoring profile: `make compose-monitor`
- [ ] Configure external Prometheus/Grafana if needed
