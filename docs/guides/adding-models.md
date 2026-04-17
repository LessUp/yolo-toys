# Adding Custom Models

Step-by-step guide to extend YOLO-Toys with your own models.

<p align="center">
  <a href="adding-models.zh-CN.md">简体中文</a> •
  <a href="./">⬅ Back to Guides</a>
</p>

---

## 📋 Prerequisites

Before adding a new model, ensure you have:

- [ ] Python 3.11+ installed
- [ ] YOLO-Toys development environment set up
- [ ] Understanding of the model you want to add
- [ ] Familiarity with PyTorch or the model's framework

---

## 🚀 Quick Start

Adding a model requires 3 steps:

1. **Create Handler** — Implement `load()` and `infer()` methods
2. **Register Model** — Add to registry with metadata
3. **Add Tests** — Verify the implementation

Total time: ~30 minutes for a simple model

---

## 📝 Step 1: Create Handler

### 1.1 Create Handler File

Create a new file in `app/handlers/`:

```bash
touch app/handlers/my_model_handler.py
```

### 1.2 Implement Handler

Here's a template:

```python
# app/handlers/my_model_handler.py
"""Handler for MyModel."""

import time
from typing import Any, Optional, Tuple
import numpy as np
import torch

from app.handlers.base import BaseHandler


class MyModelHandler(BaseHandler):
    """
    Handler for MyModel inference.

    Supports: object detection, classification, etc.
    """

    def load(self, model_id: str) -> Tuple[Any, Optional[Any]]:
        """
        Load model and optional processor.

        Args:
            model_id: Model identifier (e.g., 'my-model-v1')

        Returns:
            Tuple of (model, processor)
        """
        # Example: Load from HuggingFace
        from transformers import AutoProcessor, AutoModel

        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)

        # Move to configured device
        model = self._model_to_device(model)
        model.eval()

        return model, processor

    def infer(
        self,
        model: Any,
        processor: Optional[Any],
        image: np.ndarray,
        **params: Any
    ) -> dict:
        """
        Run inference on the image.

        Args:
            model: Loaded model
            processor: Optional processor
            image: Input image (BGR format, numpy array)
            **params: Inference parameters

        Returns:
            Standardized result dictionary
        """
        start = time.perf_counter()

        # Extract parameters
        conf = params.get("conf", 0.25)

        # Preprocess
        # Convert BGR (OpenCV) to PIL if needed
        pil_image = self.bgr_to_pil(image)

        if processor:
            inputs = processor(images=pil_image, return_tensors="pt")
        else:
            # Custom preprocessing
            inputs = self._preprocess(image)

        # Move to device
        if isinstance(inputs, dict):
            inputs = {k: self._to_device(v) for k, v in inputs.items()}
        else:
            inputs = self._to_device(inputs)

        # Inference
        with torch.no_grad():
            outputs = model(**inputs)

        # Post-process
        detections = self._parse_outputs(outputs, image.shape[:2], conf)

        inference_time = (time.perf_counter() - start) * 1000

        # Return standardized format
        return self.make_result(
            image=image,
            detections=detections,
            task="detect",  # or "classify", "segment", etc.
            inference_time=inference_time,
            model=getattr(model, 'name_or_path', str(model))
        )

    def _preprocess(self, image: np.ndarray) -> torch.Tensor:
        """Custom preprocessing if no processor available."""
        # Example: Resize and normalize
        import cv2

        resized = cv2.resize(image, (224, 224))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(rgb).permute(2, 0, 1).float() / 255.0
        return tensor.unsqueeze(0)

    def _parse_outputs(
        self,
        outputs: Any,
        image_shape: Tuple[int, int],
        conf: float
    ) -> list:
        """
        Parse model outputs into standardized detection format.

        Returns list of dicts with keys:
        - bbox: [x1, y1, x2, y2] (pixel coordinates)
        - score: float (0-1)
        - label: str (class name)
        """
        detections = []

        # Example: Parse detection outputs
        # Adjust based on your model's output format
        boxes = outputs.boxes if hasattr(outputs, 'boxes') else outputs[0]
        scores = outputs.scores if hasattr(outputs, 'scores') else outputs[1]
        labels = outputs.labels if hasattr(outputs, 'labels') else outputs[2]

        for box, score, label in zip(boxes, scores, labels):
            if float(score) < conf:
                continue

            detections.append({
                "bbox": [float(b) for b in box],  # [x1, y1, x2, y2]
                "score": float(score),
                "label": str(label)
            })

        return detections
```

### 1.3 Common Patterns

#### YOLO-Style Model

```python
def load(self, model_id: str):
    from ultralytics import YOLO
    model = YOLO(model_id)
    return model, None

def infer(self, model, processor, image, **params):
    results = model(image, conf=params.get('conf', 0.25))
    # Parse YOLO results
```

#### HuggingFace Transformers

```python
def load(self, model_id: str):
    from transformers import AutoProcessor, AutoModel
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModel.from_pretrained(model_id)
    return self._model_to_device(model), processor

def infer(self, model, processor, image, **params):
    pil_image = self.bgr_to_pil(image)
    inputs = processor(images=pil_image, return_tensors="pt")
    inputs = {k: self._to_device(v) for k, v in inputs.items()}
    # Run inference
```

#### PyTorch Hub

```python
def load(self, model_id: str):
    model = torch.hub.load('repo', model_id)
    return self._model_to_device(model), None
```

---

## 🔌 Step 2: Register Model

### 2.1 Add Category (if new type)

Edit `app/handlers/registry.py`:

```python
from enum import Enum

class ModelCategory(Enum):
    # ... existing categories
    MY_MODEL = "my_model"  # Add new category
```

### 2.2 Register Handler Mapping

```python
from app.handlers.my_model_handler import MyModelHandler

_CATEGORY_HANDLER_MAP = {
    # ... existing mappings
    ModelCategory.MY_MODEL: MyModelHandler,
}
```

### 2.3 Add Model Metadata

```python
MODEL_REGISTRY = {
    # ... existing models
    "my-model-v1": {
        "category": ModelCategory.MY_MODEL,
        "name": "My Model v1",
        "description": "Custom detection model",
        "task": "detect",  # or "classify", "segment"
        "parameters": {
            "conf": {"default": 0.25, "min": 0.0, "max": 1.0}
        }
    },
}
```

### 2.4 Full Registry Example

```python
# app/handlers/registry.py

from enum import Enum
from typing import Dict, Any

from app.handlers.yolo_handler import YOLOHandler
from app.handlers.hf_handler import DETRHandler, OWLViTHandler
from app.handlers.blip_handler import BLIPCaptionHandler, BLIPVQAHandler
from app.handlers.my_model_handler import MyModelHandler  # Import new handler


class ModelCategory(Enum):
    """Model categories for handler selection."""
    YOLO_DETECT = "yolo_detect"
    YOLO_SEGMENT = "yolo_segment"
    YOLO_POSE = "yolo_pose"
    HF_DETR = "hf_detr"
    HF_OWL_VIT = "hf_owl_vit"
    HF_GROUNDING_DINO = "hf_grounding_dino"
    HF_BLIP_CAPTION = "hf_blip_caption"
    HF_BLIP_VQA = "hf_blip_vqa"
    MY_MODEL = "my_model"  # New category


# Handler factory mapping
_CATEGORY_HANDLER_MAP = {
    ModelCategory.YOLO_DETECT: YOLOHandler,
    ModelCategory.YOLO_SEGMENT: YOLOHandler,
    ModelCategory.YOLO_POSE: YOLOHandler,
    ModelCategory.HF_DETR: DETRHandler,
    ModelCategory.HF_OWL_VIT: OWLViTHandler,
    ModelCategory.HF_GROUNDING_DINO: GroundingDINOHandler,
    ModelCategory.HF_BLIP_CAPTION: BLIPCaptionHandler,
    ModelCategory.HF_BLIP_VQA: BLIPVQAHandler,
    ModelCategory.MY_MODEL: MyModelHandler,  # Register handler
}


# Model metadata registry
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # YOLO models...
    # HuggingFace models...

    # Your custom model
    "my-model-v1": {
        "category": ModelCategory.MY_MODEL,
        "name": "My Model v1",
        "description": "Custom detection model for specific use case",
        "task": "detect",
    },
}
```

---

## 🧪 Step 3: Add Tests

### 3.1 Create Test File

```python
# tests/test_my_model.py
import pytest
import numpy as np
from app.handlers.my_model_handler import MyModelHandler


class TestMyModelHandler:
    """Tests for MyModelHandler."""

    @pytest.fixture
    def handler(self):
        return MyModelHandler(device="cpu")

    @pytest.fixture
    def test_image(self):
        """Create a test image."""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def test_load(self, handler):
        """Test model loading."""
        model, processor = handler.load("my-model-v1")
        assert model is not None
        # Add model-specific assertions

    def test_infer(self, handler, test_image):
        """Test inference."""
        model, processor = handler.load("my-model-v1")
        result = handler.infer(
            model, processor, test_image,
            conf=0.5
        )

        # Verify result structure
        assert "detections" in result
        assert "inference_time" in result
        assert "task" in result

        # Verify detections format
        for det in result["detections"]:
            assert "bbox" in det
            assert "score" in det
            assert "label" in det
            assert len(det["bbox"]) == 4

    def test_device_handling(self):
        """Test device configuration."""
        handler = MyModelHandler(device="cpu")
        assert handler.device == "cpu"
        # Test GPU if available
        # handler = MyModelHandler(device="cuda:0")
```

### 3.2 Run Tests

```bash
# Run specific test
pytest tests/test_my_model.py -v

# Run all tests
make test
```

---

## 🎨 Step 4: Frontend Integration (Optional)

If your model needs special UI treatment:

### 4.1 Add Model Category Display

Edit `frontend/index.html` or `frontend/app.js`:

```javascript
// Add new category to UI
const MODEL_CATEGORIES = {
    // ... existing categories
    my_model: {
        name: 'My Models',
        icon: '🎯',
        description: 'Custom detection models'
    }
};
```

### 4.2 Special Parameters

If your model needs custom parameters:

```javascript
// Add custom parameter handling
function getModelSpecificParams(modelId) {
    if (modelId.startsWith('my-model')) {
        return {
            custom_param: document.getElementById('custom-param').value
        };
    }
    return {};
}
```

---

## 📊 Performance Optimization

### Model Caching

Models are automatically cached by ModelManager. First load may be slow.

### FP16 Inference (GPU)

```python
def load(self, model_id: str):
    model = load_model(model_id)
    model = self._model_to_device(model)

    # Enable FP16 on CUDA
    if self.device.startswith("cuda"):
        model = model.half()

    return model, processor
```

### Batch Processing

For batch inference support:

```python
def infer_batch(self, model, processor, images, **params):
    """Batch inference for multiple images."""
    # Stack images
    batch = torch.stack([self._preprocess(img) for img in images])

    with torch.no_grad():
        outputs = model(batch)

    return [self._parse_single(o) for o in outputs]
```

---

## ✅ Checklist

Before submitting your handler:

- [ ] Handler implements `load()` and `infer()`
- [ ] Model registered in `MODEL_REGISTRY`
- [ ] Category added to `ModelCategory`
- [ ] Handler mapped in `_CATEGORY_HANDLER_MAP`
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Type hints included
- [ ] Error handling implemented

---

## 🔗 Related Documentation

- 🏗️ **[Handler Pattern](../architecture/handlers.md)** — Handler implementation details
- 🏗️ **[Architecture](../architecture/overview.md)** — System architecture
- 🤝 **[Contributing](../../CONTRIBUTING.md)** — Contribution guidelines

---

<div align="center">

**[⬆ Back to Top](#adding-custom-models)**

</div>
