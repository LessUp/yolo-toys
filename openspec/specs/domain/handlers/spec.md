## Purpose

Define the Handler Pattern implementation for supporting multiple model families with a unified interface.

---

### Requirement: BaseHandler Abstract Interface

The system MUST define an abstract base class with `load()` and `infer()` methods.

```python
class BaseHandler(ABC):
    def __init__(self, device: str):
        self._device = device

    @abstractmethod
    def load(self, model_id: str) -> tuple[Any, Any | None]:
        """Load model, return (model, processor). Processor can be None."""

    @abstractmethod
    def infer(self, model, processor, image, **params) -> dict:
        """Run inference, return standard result dictionary"""
```

#### Scenario: Handler initialization
Given: A device string
When: Handler is instantiated
Then: Device is stored for later use in inference

#### Scenario: Abstract method enforcement
Given: A class extending BaseHandler
When: The class doesn't implement load() or infer()
Then: Python raises TypeError on instantiation

---

### Requirement: YOLOHandler Implementation

The system MUST provide a handler for YOLO detection, segmentation, and pose models.

```python
class YOLOHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, None]:
        from ultralytics import YOLO
        model = YOLO(model_id)
        return model, None  # No separate processor needed
```

#### Scenario: Load YOLO detection model
Given: Model ID `yolov8n.pt`
When: `load()` is called
Then: Returns `(YOLO_model, None)`

#### Scenario: Load YOLO segmentation model
Given: Model ID `yolov8n-seg.pt`
When: `load()` is called
Then: Model is loaded, inference returns `polygons` field

#### Scenario: Load YOLO pose model
Given: Model ID `yolov8n-pose.pt`
When: `load()` is called
Then: Model is loaded, inference returns `keypoints` field

#### Scenario: YOLO inference parameters
Given: A loaded YOLO model
When: `infer()` is called with `conf=0.5`, `iou=0.3`, `max_det=100`
Then: Parameters are passed to YOLO model call

---

### Requirement: DETRHandler Implementation

The system MUST provide a handler for Facebook DETR models.

```python
class DETRHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, Any]:
        processor = DetrImageProcessor.from_pretrained(model_id)
        model = DetrForObjectDetection.from_pretrained(model_id)
        return model, processor
```

#### Scenario: Load DETR model
Given: Model ID `facebook/detr-resnet-50`
When: `load()` is called
Then: Returns `(DetrForObjectDetection, DetrImageProcessor)`

#### Scenario: DETR inference
Given: A loaded DETR model and processor
When: `infer()` is called with an image
Then: Image is converted to PIL, processed, and detections returned

---

### Requirement: OWLViTHandler Implementation

The system MUST provide a handler for open-vocabulary detection with text queries.

#### Scenario: Load OWL-ViT model
Given: Model ID `google/owlvit-base-patch32`
When: `load()` is called
Then: Returns `(OwlViTForObjectDetection, OwlViTProcessor)`

#### Scenario: OWL-ViT inference with text queries
Given: A loaded OWL-ViT model and `text_queries=["cat", "dog"]`
When: `infer()` is called
Then: Detections include labels matching the text queries

---

### Requirement: GroundingDINOHandler Implementation

The system MUST provide a handler for text-prompted detection.

#### Scenario: Load Grounding DINO model
Given: Model ID `IDEA-Research/grounding-dino-tiny`
When: `load()` is called
Then: Returns `(AutoModelForZeroShotObjectDetection, AutoProcessor)`

#### Scenario: Grounding DINO inference
Given: A loaded model and `text_queries="a cat. a dog."`
When: `infer()` is called
Then: Returns detections for objects matching text descriptions

---

### Requirement: BLIPCaptionHandler Implementation

The system MUST provide a handler for image captioning.

```python
class BLIPCaptionHandler(BaseHandler):
    def infer(self, model, processor, image, **params) -> dict:
        pil_image = self.bgr_to_pil(image)
        inputs = processor(images=pil_image, return_tensors="pt")
        outputs = model.generate(**inputs)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        return {"caption": caption, "inference_time": ..., "model": model_id}
```

#### Scenario: Load BLIP caption model
Given: Model ID `Salesforce/blip-image-captioning-base`
When: `load()` is called
Then: Returns `(BlipForConditionalGeneration, BlipProcessor)`

#### Scenario: Generate caption
Given: A loaded BLIP caption model
When: `infer()` is called with an image
Then: Returns `{ "caption": "...", "inference_time": ..., "model": "..." }`

---

### Requirement: BLIPVQAHandler Implementation

The system MUST provide a handler for visual question answering.

#### Scenario: Load BLIP VQA model
Given: Model ID `Salesforce/blip-vqa-base`
When: `load()` is called
Then: Returns `(BlipForQuestionAnswering, BlipProcessor)`

#### Scenario: Answer question about image
Given: A loaded BLIP VQA model and `question="What color is the car?"`
When: `infer()` is called with an image
Then: Returns `{ "answer": "...", "question": "...", "inference_time": ..., "model": "..." }`

---

### Requirement: Result Format Consistency

All handlers MUST return results in consistent formats per task type.

#### Scenario: Detection result format
Given: Any detection handler
When: `infer()` returns a result
Then: Result contains `width`, `height`, `task: "detect"`, `detections[]`, `inference_time`, `model`

#### Scenario: Segmentation result format
Given: A segmentation handler
When: `infer()` returns a result
Then: Result contains `task: "segment"` and detections include `polygons`

#### Scenario: Pose result format
Given: A pose handler
When: `infer()` returns a result
Then: Result contains `task: "pose"` and detections include `keypoints`

#### Scenario: Caption result format
Given: A caption handler
When: `infer()` returns a result
Then: Result contains `caption`, `inference_time`, `model`

#### Scenario: VQA result format
Given: A VQA handler
When: `infer()` returns a result
Then: Result contains `answer`, `question`, `inference_time`, `model`

---

### Requirement: Adding New Handlers

The system MUST support adding new handlers through a defined process.

#### Scenario: Create new handler class
Given: A new model type to support
When: A class extending BaseHandler is created
Then: The class MUST implement `load()` and `infer()` methods

#### Scenario: Register handler category
Given: A new handler class
When: Category is added to `ModelCategory` and `_CATEGORY_HANDLER_MAP`
Then: Models in that category use the new handler

#### Scenario: Add model metadata
Given: A model ID and its category
When: Entry is added to `MODEL_REGISTRY`
Then: Model becomes discoverable via `/models` endpoint

---

### Requirement: Utility Methods

The system MUST provide common utility methods in BaseHandler.

#### Scenario: BGR to PIL conversion
Given: An OpenCV BGR ndarray image
When: `bgr_to_pil()` is called
Then: Returns a PIL RGB Image

#### Scenario: Move tensor to device
Given: A dict of tensors
When: `_to_device(inputs, device)` is called
Then: All tensors are moved to specified device

#### Scenario: Move model to device
Given: A PyTorch model
When: `_model_to_device(model)` is called
Then: Model is moved to handler's configured device
