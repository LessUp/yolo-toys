# System Architecture Overview

Understanding the design principles and data flow of YOLO-Toys.

<p align="center">
  <a href="overview.zh-CN.md">简体中文</a> •
  <a href="./">⬅ Back to Architecture</a>
</p>

---

## 📐 High-Level Architecture

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

---

## 🔄 Data Flow

### REST API Request Flow

```
1. HTTP Request (image file)
        │
        ▼
2. FastAPI Routes (routes.py)
   - Parse multipart form data
   - Validate parameters
   - Read image bytes
        │
        ▼
3. ModelManager.infer()
   - Check model cache
   - Load if not cached
        │
        ▼
4. HandlerRegistry.get_handler()
   - Lookup model category
   - Return handler instance
        │
        ▼
5. Handler.load() (if needed)
   - Load model weights
   - Initialize processor
   - Move to device
        │
        ▼
6. Handler.infer()
   - Preprocess image
   - Run inference
   - Postprocess results
        │
        ▼
7. BaseHandler.make_result()
   - Format detections
   - Add metadata
        │
        ▼
8. JSON Response
```

### WebSocket Streaming Flow

```
1. WebSocket Connection
   - Query parameter parsing
   - Model pre-loading
        │
        ▼
2. Binary Frame Reception
   - JPEG decoding
   - Validation
        │
        ▼
3. Inference Pipeline
   - Same as REST (steps 3-6)
        │
        ▼
4. JSON Result Push
   - Real-time delivery
   - Concurrent handling
```

---

## 🧩 Design Patterns

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

    def _to_device(self, tensor):
        """Move tensor to configured device"""
        return tensor.to(self.device)
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

## 📦 Component Details

### ModelManager

**Responsibilities:**
- Model lifecycle management (load/unload)
- Cache management
- Concurrency control

```python
class ModelManager:
    def __init__(self):
        self._device = get_device()
        self._registry = HandlerRegistry(self._device)
        self._cache: dict[str, tuple] = {}
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
```

### HandlerRegistry

**Responsibilities:**
- Model category resolution
- Handler instantiation
- Device configuration injection

### Handlers

| Handler | Models | Task |
|---------|--------|------|
| YOLOHandler | YOLOv8 (n/s/m/l/x) | Detection, Segmentation, Pose |
| DETRHandler | facebook/detr-* | Object Detection |
| OWLViTHandler | google/owlvit-* | Open-vocabulary Detection |
| GroundingDINOHandler | grounding-dino-* | Text-prompted Detection |
| BLIPCaptionHandler | Salesforce/blip-* | Image Captioning |
| BLIPVQAHandler | Salesforce/blip-vqa-* | Visual QA |

---

## 🔄 Request Lifecycle

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

## 🔧 Configuration

### Environment-Driven Configuration

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

## 📊 Performance Characteristics

### Caching Strategy

- Models are loaded on first use and cached in memory
- Cache key: model_id string
- Cache value: (model, processor) tuple
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

## 🔗 Related Documentation

- 🔌 **[Handler Pattern](./handlers.md)** — Handler implementation details
- 🔍 **[REST API](../api/rest-api.md)** — API endpoint reference
- 🔌 **[WebSocket](../api/websocket.md)** — Streaming protocol
- 📋 **[Models](../reference/models.md)** — Supported model list

---

<div align="center">

**[⬆ Back to Top](#system-architecture-overview)**

</div>
