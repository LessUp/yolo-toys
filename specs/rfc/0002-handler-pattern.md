# RFC-0002: Handler Pattern

| Status | Author | Created | Updated |
|--------|--------|---------|---------|
| Active | YOLO-Toys Team | 2026-02-13 | 2026-04-17 |

---

## Summary

This RFC defines the Handler Pattern implementation used in YOLO-Toys for supporting multiple model families with a unified interface.

---

## Motivation

Different AI model families have vastly different APIs:

| Model Family | Framework | Loading API | Inference API |
|--------------|-----------|-------------|---------------|
| YOLO | Ultralytics | `YOLO(path)` | `model(image)` |
| DETR | Transformers | `AutoModel.from_pretrained()` | `model(**inputs)` |
| BLIP | Transformers | `BlipForConditionalGeneration` | `model.generate()` |

Without a unified interface, the codebase would become fragmented and difficult to maintain.

---

## Design

### Abstract Base Class

```python
class BaseHandler(ABC):
    """所有模型处理器的基类"""

    def __init__(self, device: str):
        self._device = device

    @property
    def device(self) -> str:
        return self._device

    @abstractmethod
    def load(self, model_id: str) -> tuple[Any, Any | None]:
        """
        加载模型，返回 (model, processor)。
        processor 可为 None（如 YOLO 不需要独立 processor）。
        """

    @abstractmethod
    def infer(
        self,
        model: Any,
        processor: Any | None,
        image: np.ndarray,
        *,
        conf: float = 0.25,
        iou: float = 0.45,
        max_det: int = 300,
        device: str | None = None,
        imgsz: int | None = None,
        half: bool = False,
        text_queries: list[str] | None = None,
        question: str | None = None,
    ) -> dict[str, Any]:
        """执行推理，返回标准结果字典"""

    # 公共工具方法
    @staticmethod
    def bgr_to_pil(image: np.ndarray) -> Image.Image:
        """OpenCV BGR ndarray → PIL RGB Image"""
        return Image.fromarray(image[:, :, ::-1])

    @staticmethod
    def make_result(
        image: np.ndarray,
        *,
        detections: list[dict[str, Any]] | None = None,
        inference_time: float,
        task: str = "detect",
        **extra,
    ) -> dict[str, Any]:
        """构造标准返回字典"""
        ...

    def _model_to_device(self, model: Any) -> Any:
        """将模型移动到当前设备（GPU 场景）"""
        ...

    def _to_device(self, inputs: dict[str, Any], device: str | None = None) -> dict[str, Any]:
        """将 tensor dict 移动到指定设备"""
        ...
```

---

## Handler Implementations

### YOLOHandler

Handles YOLO detection, segmentation, and pose models.

```python
class YOLOHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, None]:
        from ultralytics import YOLO
        model = YOLO(model_id)
        return model, None

    def infer(self, model, processor, image, **params) -> dict:
        results = model(
            image,
            conf=params.get('conf', 0.25),
            iou=params.get('iou', 0.45),
            max_det=params.get('max_det', 300),
            device=self._device,
            imgsz=params.get('imgsz', 640),
            half=params.get('half', False),
        )
        # Parse results based on task type
        ...
```

**Supported Models:**

| Model ID | Task | Notes |
|----------|------|-------|
| yolov8n.pt | Detection | Nano, fastest |
| yolov8s.pt | Detection | Small |
| yolov8m.pt | Detection | Medium |
| yolov8l.pt | Detection | Large |
| yolov8x.pt | Detection | XLarge |
| yolov8n-seg.pt | Segmentation | Nano |
| yolov8s-seg.pt | Segmentation | Small |
| yolov8m-seg.pt | Segmentation | Medium |
| yolov8n-pose.pt | Pose | Nano |
| yolov8s-pose.pt | Pose | Small |
| yolov8m-pose.pt | Pose | Medium |

### DETRHandler

Handles Facebook DETR models.

```python
class DETRHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, Any]:
        from transformers import DetrImageProcessor, DetrForObjectDetection
        processor = DetrImageProcessor.from_pretrained(model_id)
        model = DetrForObjectDetection.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor

    def infer(self, model, processor, image, **params) -> dict:
        pil_image = self.bgr_to_pil(image)
        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = self._to_device(inputs)
        with torch.no_grad():
            outputs = model(**inputs)
        # Post-process and return detections
        ...
```

**Supported Models:**

| Model ID | Notes |
|----------|-------|
| facebook/detr-resnet-50 | Standard DETR |
| facebook/detr-resnet-101 | Larger backbone |

### OWLViTHandler

Handles open-vocabulary detection.

```python
class OWLViTHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, Any]:
        from transformers import OwlViTProcessor, OwlViTForObjectDetection
        processor = OwlViTProcessor.from_pretrained(model_id)
        model = OwlViTForObjectDetection.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor

    def infer(self, model, processor, image, **params) -> dict:
        text_queries = params.get('text_queries', [])
        pil_image = self.bgr_to_pil(image)
        inputs = processor(
            text=text_queries,
            images=pil_image,
            return_tensors="pt"
        )
        inputs = self._to_device(inputs)
        with torch.no_grad():
            outputs = model(**inputs)
        # Post-process with text-based labels
        ...
```

**Supported Models:**

| Model ID | Notes |
|----------|-------|
| google/owlvit-base-patch32 | Open-vocabulary detection |

### GroundingDINOHandler

Handles text-prompted detection.

```python
class GroundingDINOHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, Any]:
        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor
```

**Supported Models:**

| Model ID | Notes |
|----------|-------|
| IDEA-Research/grounding-dino-tiny | Text-prompted detection |

### BLIPCaptionHandler

Handles image captioning.

```python
class BLIPCaptionHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, Any]:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        processor = BlipProcessor.from_pretrained(model_id)
        model = BlipForConditionalGeneration.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor

    def infer(self, model, processor, image, **params) -> dict:
        pil_image = self.bgr_to_pil(image)
        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = self._to_device(inputs)
        with torch.no_grad():
            outputs = model.generate(**inputs)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        return {
            "caption": caption,
            "inference_time": inference_time,
            "model": model_id
        }
```

**Supported Models:**

| Model ID | Notes |
|----------|-------|
| Salesforce/blip-image-captioning-base | Standard captioning |
| Salesforce/blip-image-captioning-large | Higher quality |

### BLIPVQAHandler

Handles visual question answering.

```python
class BLIPVQAHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, Any]:
        from transformers import BlipProcessor, BlipForQuestionAnswering
        processor = BlipProcessor.from_pretrained(model_id)
        model = BlipForQuestionAnswering.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor

    def infer(self, model, processor, image, **params) -> dict:
        question = params.get('question', '')
        pil_image = self.bgr_to_pil(image)
        inputs = processor(images=pil_image, text=question, return_tensors="pt")
        inputs = self._to_device(inputs)
        with torch.no_grad():
            outputs = model.generate(**inputs)
        answer = processor.decode(outputs[0], skip_special_tokens=True)
        return {
            "answer": answer,
            "question": question,
            "inference_time": inference_time,
            "model": model_id
        }
```

**Supported Models:**

| Model ID | Notes |
|----------|-------|
| Salesforce/blip-vqa-base | Visual QA |

---

## Result Format

### Detection Result

```json
{
  "width": 640,
  "height": 480,
  "task": "detect",
  "detections": [
    {
      "bbox": [100.5, 200.3, 250.8, 450.2],
      "score": 0.89,
      "label": "person"
    }
  ],
  "inference_time": 12.5,
  "model": "yolov8n.pt"
}
```

### Segmentation Result

```json
{
  "width": 640,
  "height": 480,
  "task": "segment",
  "detections": [
    {
      "bbox": [100.5, 200.3, 250.8, 450.2],
      "score": 0.89,
      "label": "person",
      "polygons": [[[x1, y1], [x2, y2], ...]]
    }
  ],
  "inference_time": 25.0,
  "model": "yolov8n-seg.pt"
}
```

### Pose Result

```json
{
  "width": 640,
  "height": 480,
  "task": "pose",
  "detections": [
    {
      "bbox": [100.5, 200.3, 250.8, 450.2],
      "score": 0.89,
      "label": "person",
      "keypoints": [
        {"x": 150, "y": 220, "confidence": 0.95},
        ...
      ]
    }
  ],
  "inference_time": 15.0,
  "model": "yolov8n-pose.pt"
}
```

### Caption Result

```json
{
  "caption": "a person riding a skateboard on a street",
  "inference_time": 120.5,
  "model": "Salesforce/blip-image-captioning-base"
}
```

### VQA Result

```json
{
  "answer": "blue",
  "question": "What color is the car?",
  "inference_time": 95.2,
  "model": "Salesforce/blip-vqa-base"
}
```

---

## Adding a New Handler

To add a new model type:

1. **Create Handler Class**

```python
# app/handlers/my_handler.py
class MyHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, Any | None]:
        ...

    def infer(self, model, processor, image, **params) -> dict:
        ...
```

2. **Add Category**

```python
# app/handlers/registry.py
class ModelCategory:
    MY_MODEL = "my_model"
```

3. **Register Handler Mapping**

```python
_CATEGORY_HANDLER_MAP = {
    ...
    ModelCategory.MY_MODEL: MyHandler,
}
```

4. **Add Model Metadata**

```python
MODEL_REGISTRY = {
    ...
    "my-model-v1": {
        "category": ModelCategory.MY_MODEL,
        "name": "My Model v1",
        "description": "...",
        "task": "detect",
    },
}
```

---

## Testing Requirements

Each handler must have tests covering:

- [ ] Model loading (success and failure cases)
- [ ] Inference with valid inputs
- [ ] Edge cases (empty images, invalid parameters)
- [ ] Device handling (CPU, CUDA, MPS)
- [ ] Result format compliance

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-13 | Initial handler pattern design |
| 2026-04-17 | Formalized as RFC-0002 |
