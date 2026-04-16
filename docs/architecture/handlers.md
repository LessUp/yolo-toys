# Handler Pattern

Deep dive into the Strategy Pattern implementation for model inference.

<p align="center">
  <a href="handlers.zh-CN.md">简体中文</a> •
  <a href="./">⬅ Back to Architecture</a>
</p>

---

## 🎯 Overview

The Handler system implements the **Strategy Pattern**, allowing different AI models to be used interchangeably through a common interface. Each handler encapsulates the loading and inference logic for a specific model type.

```python
# Usage example - same interface, different implementations
handler = registry.get_handler("yolov8n.pt")  # Returns YOLOHandler
handler = registry.get_handler("Salesforce/blip-vqa-base")  # Returns BLIPVQAHandler

# Same API regardless of model type
model, processor = handler.load(model_id)
result = handler.infer(model, processor, image, **params)
```

---

## 🏗️ BaseHandler Interface

All handlers inherit from `BaseHandler` and must implement two abstract methods:

```python
from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional
import numpy as np

class BaseHandler(ABC):
    """Abstract base class for all model handlers."""
    
    def __init__(self, device: str = "cpu"):
        self.device = device
    
    @abstractmethod
    def load(self, model_id: str) -> Tuple[Any, Optional[Any]]:
        """
        Load model and optional processor.
        
        Args:
            model_id: Unique identifier for the model
            
        Returns:
            Tuple of (model, processor)
            - model: The loaded model ready for inference
            - processor: Optional preprocessor (can be None)
        """
        pass
    
    @abstractmethod
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
            model: Loaded model from load()
            processor: Optional processor from load()
            image: Input image as numpy array (BGR format)
            **params: Inference parameters (conf, iou, max_det, etc.)
            
        Returns:
            Dictionary with standardized detection results
        """
        pass
    
    def make_result(
        self,
        image: np.ndarray,
        detections: list,
        task: str,
        inference_time: float,
        model: str,
        **kwargs
    ) -> dict:
        """
        Create standardized result dictionary.
        
        This is a template method - subclasses can override
        but usually don't need to.
        """
        return {
            "width": image.shape[1],
            "height": image.shape[0],
            "task": task,
            "detections": detections,
            "inference_time": inference_time,
            "model": model,
            **kwargs
        }
    
    def _model_to_device(self, model: Any) -> Any:
        """Move PyTorch model to configured device."""
        if hasattr(model, 'to'):
            return model.to(self.device)
        return model
    
    def _to_device(self, tensor: Any) -> Any:
        """Move tensor to configured device."""
        if hasattr(tensor, 'to'):
            return tensor.to(self.device)
        return tensor
    
    @staticmethod
    def bgr_to_pil(image: np.ndarray) -> "PIL.Image":
        """Convert OpenCV BGR image to PIL RGB."""
        from PIL import Image
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
```

---

## 📦 Handler Implementations

### YOLOHandler

Handles all Ultralytics YOLO models (detection, segmentation, pose).

```python
from ultralytics import YOLO
import cv2
import numpy as np
import time

class YOLOHandler(BaseHandler):
    """Handler for YOLOv8 detection, segmentation, and pose models."""
    
    def load(self, model_id: str) -> tuple:
        """Load YOLO model."""
        model = YOLO(model_id)
        # YOLO doesn't use a separate processor
        return model, None
    
    def infer(self, model, processor, image, **params):
        """Run YOLO inference."""
        start = time.perf_counter()
        
        # Extract parameters with defaults
        conf = params.get("conf", 0.25)
        iou = params.get("iou", 0.45)
        max_det = params.get("max_det", 300)
        
        # Run inference
        results = model(
            image,
            conf=conf,
            iou=iou,
            max_det=max_det,
            verbose=False
        )[0]
        
        # Parse results based on task type
        detections = self._parse_results(results)
        
        inference_time = (time.perf_counter() - start) * 1000
        
        return self.make_result(
            image=image,
            detections=detections,
            task=self._get_task(results),
            inference_time=inference_time,
            model=model.ckpt_path
        )
    
    def _parse_results(self, results) -> list:
        """Parse YOLO results into standardized format."""
        detections = []
        
        # Detection boxes
        if results.boxes is not None:
            for box in results.boxes:
                det = {
                    "bbox": box.xyxy[0].tolist(),
                    "score": float(box.conf),
                    "label": results.names[int(box.cls)]
                }
                
                # Add segmentation mask if available
                if results.masks is not None:
                    det["polygons"] = self._extract_polygons(results.masks)
                
                # Add keypoints if available
                if results.keypoints is not None:
                    det["keypoints"] = self._extract_keypoints(results.keypoints)
                
                detections.append(det)
        
        return detections
    
    def _get_task(self, results) -> str:
        """Determine task type from results."""
        if results.keypoints is not None:
            return "pose"
        elif results.masks is not None:
            return "segment"
        return "detect"
```

### DETRHandler

Handles Facebook DETR (Detection Transformer) models.

```python
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
import time

class DETRHandler(BaseHandler):
    """Handler for DETR object detection models."""
    
    def load(self, model_id: str) -> tuple:
        """Load DETR model and processor."""
        processor = DetrImageProcessor.from_pretrained(model_id)
        model = DetrForObjectDetection.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor
    
    def infer(self, model, processor, image, **params):
        """Run DETR inference."""
        start = time.perf_counter()
        
        conf = params.get("conf", 0.25)
        
        # Convert BGR to PIL
        pil_image = self.bgr_to_pil(image)
        
        # Preprocess
        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = {k: self._to_device(v) for k, v in inputs.items()}
        
        # Inference
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Post-process
        target_sizes = torch.tensor([pil_image.size[::-1]])
        results = processor.post_process_object_detection(
            outputs,
            threshold=conf,
            target_sizes=target_sizes
        )[0]
        
        # Format detections
        detections = []
        for score, label, box in zip(
            results["scores"],
            results["labels"],
            results["boxes"]
        ):
            detections.append({
                "bbox": box.tolist(),
                "score": float(score),
                "label": model.config.id2label[int(label)]
            })
        
        inference_time = (time.perf_counter() - start) * 1000
        
        return self.make_result(
            image=image,
            detections=detections,
            task="detect",
            inference_time=inference_time,
            model=model.name_or_path
        )
```

### BLIPCaptionHandler

Handles BLIP image captioning.

```python
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
import time

class BLIPCaptionHandler(BaseHandler):
    """Handler for BLIP image captioning."""
    
    def load(self, model_id: str) -> tuple:
        """Load BLIP caption model."""
        processor = BlipProcessor.from_pretrained(model_id)
        model = BlipForConditionalGeneration.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor
    
    def infer(self, model, processor, image, **params):
        """Generate image caption."""
        start = time.perf_counter()
        
        max_length = params.get("max_length", 50)
        
        # Convert BGR to PIL
        pil_image = self.bgr_to_pil(image)
        
        # Preprocess
        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = {k: self._to_device(v) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_length=max_length
            )
        
        # Decode
        caption = processor.decode(output_ids[0], skip_special_tokens=True)
        
        inference_time = (time.perf_counter() - start) * 1000
        
        return {
            "caption": caption,
            "inference_time": inference_time,
            "model": model.name_or_path
        }
```

---

## 🔌 Handler Registration

### ModelCategory Enum

```python
from enum import Enum

class ModelCategory(Enum):
    """Categories for model classification."""
    YOLO_DETECT = "yolo_detect"
    YOLO_SEGMENT = "yolo_segment"
    YOLO_POSE = "yolo_pose"
    HF_DETR = "hf_detr"
    HF_OWL_VIT = "hf_owl_vit"
    HF_GROUNDING_DINO = "hf_grounding_dino"
    HF_BLIP_CAPTION = "hf_blip_caption"
    HF_BLIP_VQA = "hf_blip_vqa"
```

### Category-to-Handler Mapping

```python
_CATEGORY_HANDLER_MAP = {
    ModelCategory.YOLO_DETECT: YOLOHandler,
    ModelCategory.YOLO_SEGMENT: YOLOHandler,
    ModelCategory.YOLO_POSE: YOLOHandler,
    ModelCategory.HF_DETR: DETRHandler,
    ModelCategory.HF_OWL_VIT: OWLViTHandler,
    ModelCategory.HF_GROUNDING_DINO: GroundingDINOHandler,
    ModelCategory.HF_BLIP_CAPTION: BLIPCaptionHandler,
    ModelCategory.HF_BLIP_VQA: BLIPVQAHandler,
}
```

### Model Registry

```python
MODEL_REGISTRY = {
    # YOLO Detection
    "yolov8n.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Nano",
        "description": "Fastest detection model"
    },
    "yolov8s.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Small",
        "description": "Balanced speed and accuracy"
    },
    
    # DETR
    "facebook/detr-resnet-50": {
        "category": ModelCategory.HF_DETR,
        "name": "DETR ResNet-50",
        "description": "End-to-end object detection"
    },
    
    # BLIP
    "Salesforce/blip-image-captioning-base": {
        "category": ModelCategory.HF_BLIP_CAPTION,
        "name": "BLIP Caption",
        "description": "Image captioning model"
    },
}
```

---

## 🆕 Adding a New Handler

### Step 1: Create Handler Class

```python
# app/handlers/my_handler.py
from app.handlers.base import BaseHandler
import time

class MyModelHandler(BaseHandler):
    """Handler for MyModel."""
    
    def load(self, model_id: str) -> tuple:
        """Load model and processor."""
        # Your loading logic here
        model = load_my_model(model_id)
        processor = load_my_processor(model_id) if needed else None
        
        if hasattr(model, 'to'):
            model = model.to(self.device)
        
        return model, processor
    
    def infer(self, model, processor, image, **params):
        """Run inference."""
        start = time.perf_counter()
        
        # Preprocess
        if processor:
            inputs = processor(image)
        else:
            inputs = self._preprocess(image)
        
        # Move to device
        if isinstance(inputs, dict):
            inputs = {k: self._to_device(v) for k, v in inputs.items()}
        else:
            inputs = self._to_device(inputs)
        
        # Inference
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Post-process and format
        detections = self._parse_outputs(outputs, params)
        
        inference_time = (time.perf_counter() - start) * 1000
        
        return self.make_result(
            image=image,
            detections=detections,
            task="detect",  # or your task type
            inference_time=inference_time,
            model=getattr(model, 'name_or_path', str(model))
        )
```

### Step 2: Register in Factory

```python
# app/handlers/registry.py
from app.handlers.my_handler import MyModelHandler

# Add new category
class ModelCategory(Enum):
    # ... existing categories
    MY_MODEL = "my_model"

# Register handler
_CATEGORY_HANDLER_MAP = {
    # ... existing mappings
    ModelCategory.MY_MODEL: MyModelHandler,
}

# Add to registry
MODEL_REGISTRY["my-model-id"] = {
    "category": ModelCategory.MY_MODEL,
    "name": "My Model",
    "description": "Description of my model"
}
```

### Step 3: Add Tests

```python
# tests/test_api.py
def test_my_model_handler():
    handler = MyModelHandler(device="cpu")
    model, processor = handler.load("my-model-id")
    
    # Create test image
    image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    result = handler.infer(model, processor, image, conf=0.5)
    
    assert "detections" in result
    assert "inference_time" in result
```

---

## 🔗 Related Documentation

- 🏗️ **[Architecture Overview](./overview.md)** — High-level system design
- 📖 **[Adding Models](../guides/adding-models.md)** — Step-by-step guide
- 🔍 **[REST API](../api/rest-api.md)** — API endpoint reference

---

<div align="center">

**[⬆ Back to Top](#handler-pattern)**

</div>
