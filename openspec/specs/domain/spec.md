## Purpose

Define the core architecture patterns for the YOLO-Toys multi-model vision inference platform.

---

### Requirement: Handler Pattern (Strategy)

The system MUST implement all model inference through a unified `BaseHandler` interface.

```python
class BaseHandler(ABC):
    @abstractmethod
    def load(self, model_id: str) -> tuple[Any, Any | None]:
        """Load model and processor"""

    @abstractmethod
    def infer(self, model, processor, image, **params) -> dict:
        """Run inference and return formatted results"""
```

#### Scenario: Load and cache model
Given: A model_id is requested for inference
When: The handler's `load()` method is called
Then: Model is loaded, cached, and returned with optional processor

#### Scenario: Execute inference
Given: A model is loaded and cached
When: The handler's `infer()` method is called with an image
Then: Results are returned in the standard format for the task type

#### Scenario: Handler returns None processor
Given: A handler like YOLOHandler that doesn't need a separate processor
When: `load()` is called
Then: Returns `(model, None)`

---

### Requirement: Registry Pattern

The system MUST resolve model IDs to handler instances via a registry.

```python
MODEL_REGISTRY = {
    "yolov8n.pt": {
        "category": "yolo_detect",
        "name": "YOLOv8 Nano",
        "task": "detect",
        ...
    }
}
```

#### Scenario: Resolve handler by model ID
Given: A valid model_id in MODEL_REGISTRY
When: HandlerRegistry.get_handler(model_id) is called
Then: The correct handler instance is returned

#### Scenario: Unknown model ID
Given: An unknown model_id
When: HandlerRegistry.get_handler(model_id) is called
Then: Returns None or raises appropriate error

---

### Requirement: Model Caching (Lazy Loading)

The system MUST cache loaded models to avoid repeated loading overhead.

#### Scenario: First model load
Given: A model_id not in cache
When: Inference is requested
Then: Model is loaded (slow) and cached for future requests

#### Scenario: Cache hit
Given: A model_id already in cache
When: Inference is requested
Then: Cached model is used immediately (fast)

#### Scenario: Cache expiration
Given: A model cached with TTL
When: TTL expires
Then: Model is reloaded on next request

---

### Requirement: Dependency Injection

The system MUST pass device configuration to handlers at construction.

```python
handler = YOLOHandler(device="cuda:0")
```

#### Scenario: Handler receives device
Given: A handler is instantiated
When: Device string is passed to constructor
Then: Handler uses specified device for all inference

#### Scenario: Auto device selection
Given: Device is set to "auto"
When: System initializes
Then: Best available device is selected (CUDA > MPS > CPU)

---

### Requirement: Concurrency Control

The system MUST limit concurrent inference requests to prevent resource exhaustion.

#### Scenario: Within concurrency limit
Given: MAX_CONCURRENCY = 4
When: 3 concurrent requests arrive
Then: All requests are processed in parallel

#### Scenario: Exceed concurrency limit
Given: MAX_CONCURRENCY = 4
When: 5 concurrent requests arrive
Then: 4th and 5th requests wait until slots are available

---

### Requirement: Request Flow

The system MUST process requests through the following pipeline:

```
HTTP/WebSocket Request → routes.py → ModelManager.infer()
                                    ↓
                          HandlerRegistry.get_handler(model_id)
                                    ↓
                          handler.load() [cached] → handler.infer()
                                    ↓
                          BaseHandler.make_result() → JSON response
```

#### Scenario: Complete request flow
Given: A valid inference request
When: The request is processed
Then: Model is resolved → Handler obtained → Inference executed → Result formatted

---

### Requirement: Template Method Pattern

The system MUST use template methods for common result formatting.

```python
@staticmethod
def make_result(image, *, detections, inference_time, task, **extra):
    """Construct standard result dictionary"""
```

#### Scenario: Format detection result
Given: Raw inference outputs
When: `make_result()` is called with task="detect"
Then: Result matches DetectionResult schema

#### Scenario: Add extra fields
Given: Additional fields to include
When: `make_result(**extra)` is called
Then: Extra fields are merged into result

---

### Requirement: Model Categories

The system MUST support the following model categories:

| Category | Task Type | Handler |
|----------|-----------|---------|
| `yolo_detect` | detect | YOLOHandler |
| `yolo_segment` | segment | YOLOHandler |
| `yolo_pose` | pose | YOLOHandler |
| `hf_detr` | detect | DETRHandler |
| `hf_owlvit` | detect | OWLViTHandler |
| `hf_grounding_dino` | detect | GroundingDINOHandler |
| `multimodal_caption` | caption | BLIPCaptionHandler |
| `multimodal_vqa` | vqa | BLIPVQAHandler |

#### Scenario: YOLO detection category
Given: Model ID `yolov8n.pt`
When: Category is resolved
Then: Category is `yolo_detect`, task is `detect`, handler is YOLOHandler

#### Scenario: Multimodal caption category
Given: Model ID `Salesforce/blip-image-captioning-base`
When: Category is resolved
Then: Category is `multimodal_caption`, task is `caption`, handler is BLIPCaptionHandler
