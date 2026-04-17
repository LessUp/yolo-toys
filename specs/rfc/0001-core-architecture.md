# RFC-0001: Core Architecture

| Status | Author | Created | Updated |
|--------|--------|---------|---------|
| Active | YOLO-Toys Team | 2025-02-13 | 2026-04-17 |

---

## Summary

This RFC defines the core architecture of YOLO-Toys, a multi-model real-time vision recognition platform supporting YOLO, HuggingFace Transformers, and multimodal models via WebSocket streaming.

---

## Motivation

Traditional vision inference services face several challenges:

1. **Model Diversity** — Different model families (YOLO, DETR, BLIP) have different APIs and preprocessing requirements
2. **Deployment Flexibility** — Need to support CPU, CUDA, and Apple Silicon (MPS) devices
3. **Concurrency Control** — Multiple simultaneous requests must be managed to prevent resource exhaustion
4. **Extensibility** — Adding new models should be straightforward without modifying existing code

This architecture addresses these challenges through design patterns that promote loose coupling and high cohesion.

---

## Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │  Camera    │ │  Canvas    │ │  API Client│ │ WebSocket  │   │
│  │  Module    │ │  Renderer  │ │  (HTTP)    │ │  Client    │   │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘   │
│         └──────────────┴──────────────┴────────────────┘        │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ REST / WebSocket
┌─────────────────────────────────┴───────────────────────────────┐
│                     FastAPI Backend Layer                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ModelManager (Router/Cache)                 │   │
│  │       load_model() → cache    infer() → delegate         │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────┴────────────────────────────────┐   │
│  │              HandlerRegistry (Factory)                   │   │
│  │    MODEL_REGISTRY → resolve handler → instantiate        │   │
│  └────┬──────────┬──────────┬──────────┬──────────┬────────┘   │
│       │          │          │          │          │             │
│  ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐       │
│  │  YOLO  │ │  DETR  │ │OWLViT  │ │Ground. │ │  BLIP  │       │
│  │Handler │ │Handler │ │Handler │ │ DINO   │ │Handler │       │
│  └──┬─────┘ └──┬─────┘ └──┬─────┘ └──┬─────┘ └──┬─────┘       │
│     │          │          │          │          │              │
│     └──────────┴──────────┴──────────┴──────────┘              │
│                    BaseHandler (Abstract)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **ModelManager** | Model lifecycle, caching, concurrency control |
| **HandlerRegistry** | Model-to-handler resolution, factory pattern |
| **BaseHandler** | Abstract interface for all model inference |
| **Concrete Handlers** | Model-specific `load()` and `infer()` implementations |

---

## Design Patterns

### 1. Strategy Pattern (Handler System)

All model types implement a common interface:

```python
class BaseHandler(ABC):
    @abstractmethod
    def load(self, model_id: str) -> tuple[Any, Any | None]:
        """Load model and processor"""
        pass

    @abstractmethod
    def infer(self, model, processor, image, **params) -> dict:
        """Run inference and return formatted results"""
        pass
```

**Benefits:**

- New model types can be added without modifying existing code
- Consistent interface across all model implementations
- Easy testing with mock handlers

### 2. Registry Pattern

Centralized model registration and lookup:

```python
MODEL_REGISTRY = {
    "yolov8n.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Nano",
        "task": "detect"
    },
    # ... more models
}

_CATEGORY_HANDLER_MAP = {
    ModelCategory.YOLO_DETECT: YOLOHandler,
    ModelCategory.HF_DETR: DETRHandler,
    # ... more mappings
}
```

**Benefits:**

- Single source of truth for model metadata
- Dynamic handler resolution
- Runtime model discovery

### 3. Template Method Pattern

BaseHandler provides common utilities:

```python
class BaseHandler(ABC):
    def make_result(self, image, detections, task, **kwargs) -> dict:
        """Standardized result format"""
        return {
            "width": image.shape[1],
            "height": image.shape[0],
            "task": task,
            "detections": detections,
            "inference_time": kwargs.get("inference_time"),
            "model": kwargs.get("model")
        }
```

**Benefits:**

- Consistent result format across handlers
- Shared utility methods
- Reduced code duplication

### 4. Factory Pattern

HandlerRegistry acts as a factory:

```python
class HandlerRegistry:
    def get_handler(self, model_id: str) -> BaseHandler:
        category = MODEL_REGISTRY[model_id]["category"]
        handler_class = _CATEGORY_HANDLER_MAP[category]
        return handler_class(self.device)
```

**Benefits:**

- Encapsulated object creation
- Easy to extend with new handler types
- Centralized configuration injection

---

## Request Lifecycle

### Startup Sequence

```
1. FastAPI lifespan starts
        │
        ▼
2. Create ModelManager instance
        │
        ▼
3. (Optional) Warmup default model
        │
        ▼
4. Accept connections
```

### Per-Request Sequence

```
1. Receive request (HTTP/WebSocket)
        │
        ▼
2. Acquire semaphore slot
   (limits concurrent inference)
        │
        ▼
3. Load model (if not cached)
   - Handler.load()
   - Cache result
        │
        ▼
4. Run inference
   - Handler.infer()
        │
        ▼
5. Format response
        │
        ▼
6. Release semaphore
```

---

## Configuration

### Environment-Driven Configuration

All configuration is managed via Pydantic Settings:

```python
class AppSettings(BaseSettings):
    model_config = {"env_file": ".env"}

    # Server settings
    port: int = Field(default=8000, alias="PORT")

    # Model settings
    model_name: str = Field(default="yolov8n.pt", alias="MODEL_NAME")
    device: str = Field(default="auto", alias="DEVICE")

    # Performance settings
    max_concurrency: int = Field(default=4, alias="MAX_CONCURRENCY")
```

### Device Auto-Detection

```python
def get_device(preferred: str = "auto") -> str:
    if preferred != "auto":
        return preferred
    if torch.cuda.is_available():
        return "cuda:0"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"
```

---

## Performance Characteristics

### Caching Strategy

- Models loaded on first use and cached in memory
- Cache key: `model_id` string
- Cache value: `(model, processor)` tuple
- Models persist until server restart

### Concurrency Control

- `asyncio.Semaphore` limits concurrent inference
- Default limit: 4 concurrent requests
- Additional requests queue and wait

### Memory Management

- Each cached model occupies GPU/CPU memory
- Larger models = more memory usage
- Use smaller models or reduce `MAX_CONCURRENCY` if OOM

---

## Future Considerations

1. **Model Hot-Reloading** — Ability to update models without restart
2. **Distributed Inference** — Multi-node model serving
3. **Request Prioritization** — Priority queue for inference requests
4. **Batch Inference** — Automatic request batching for throughput

---

## References

- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Registry Pattern](https://martinfowler.com/eaaCatalog/registry.html)

---

## Changelog

| Date | Change |
|------|--------|
| 2025-02-13 | Initial architecture design |
| 2025-11-25 | Added multi-model support |
| 2026-02-13 | Refactored to Strategy Pattern |
| 2026-04-17 | Formalized as RFC-0001 |
