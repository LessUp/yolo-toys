# 处理器模式

策略模式在模型推理中的深度实现解析。

<p align="center">
  <a href="handlers.md">English</a> •
  <a href="./">⬅ 返回架构文档</a>
</p>

---

## 🎯 概述

处理器系统实现了**策略模式**，允许不同的 AI 模型通过通用接口互换使用。每个处理器封装了特定模型类型的加载和推理逻辑。

```python
# 使用示例 - 相同接口，不同实现
handler = registry.get_handler("yolov8n.pt")  # 返回 YOLOHandler
handler = registry.get_handler("Salesforce/blip-vqa-base")  # 返回 BLIPVQAHandler

# 无论模型类型如何，API 都相同
model, processor = handler.load(model_id)
result = handler.infer(model, processor, image, **params)
```

---

## 🏗️ BaseHandler 接口

所有处理器都继承自 `BaseHandler`，必须实现两个抽象方法：

```python
from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional
import numpy as np

class BaseHandler(ABC):
    """所有模型处理器的抽象基类。"""

    def __init__(self, device: str = "cpu"):
        self.device = device

    @abstractmethod
    def load(self, model_id: str) -> Tuple[Any, Optional[Any]]:
        """
        加载模型和可选处理器。

        参数:
            model_id: 模型的唯一标识符

        返回:
            (model, processor) 元组
            - model: 已加载准备推理的模型
            - processor: 可选预处理器（可以为 None）
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
        在图像上运行推理。

        参数:
            model: load() 加载的模型
            processor: load() 的可选处理器
            image: 输入图像（BGR 格式的 numpy 数组）
            **params: 推理参数（conf、iou、max_det 等）

        返回:
            标准化的检测结果字典
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
        创建标准化的结果字典。

        这是一个模板方法 - 子类可以覆盖但通常不需要。
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
        """将 PyTorch 模型移动到配置的设备。"""
        if hasattr(model, 'to'):
            return model.to(self.device)
        return model

    def _to_device(self, tensor: Any) -> Any:
        """将张量移动到配置的设备。"""
        if hasattr(tensor, 'to'):
            return tensor.to(self.device)
        return tensor

    @staticmethod
    def bgr_to_pil(image: np.ndarray) -> "PIL.Image":
        """将 OpenCV BGR 图像转换为 PIL RGB。"""
        from PIL import Image
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
```

---

## 📦 处理器实现

### YOLOHandler

处理所有 Ultralytics YOLO 模型（检测、分割、姿态）。

```python
from ultralytics import YOLO
import cv2
import numpy as np
import time

class YOLOHandler(BaseHandler):
    """YOLOv8 检测、分割和姿态模型的处理器。"""

    def load(self, model_id: str) -> tuple:
        """加载 YOLO 模型。"""
        model = YOLO(model_id)
        # YOLO 不使用独立的处理器
        return model, None

    def infer(self, model, processor, image, **params):
        """运行 YOLO 推理。"""
        start = time.perf_counter()

        # 提取参数（带默认值）
        conf = params.get("conf", 0.25)
        iou = params.get("iou", 0.45)
        max_det = params.get("max_det", 300)

        # 运行推理
        results = model(
            image,
            conf=conf,
            iou=iou,
            max_det=max_det,
            verbose=False
        )[0]

        # 根据任务类型解析结果
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
        """将 YOLO 结果解析为标准格式。"""
        detections = []

        # 检测框
        if results.boxes is not None:
            for box in results.boxes:
                det = {
                    "bbox": box.xyxy[0].tolist(),
                    "score": float(box.conf),
                    "label": results.names[int(box.cls)]
                }

                # 如有分割掩膜则添加
                if results.masks is not None:
                    det["polygons"] = self._extract_polygons(results.masks)

                # 如有关键点则添加
                if results.keypoints is not None:
                    det["keypoints"] = self._extract_keypoints(results.keypoints)

                detections.append(det)

        return detections

    def _get_task(self, results) -> str:
        """从结果确定任务类型。"""
        if results.keypoints is not None:
            return "pose"
        elif results.masks is not None:
            return "segment"
        return "detect"
```

### DETRHandler

处理 Facebook DETR（检测 Transformer）模型。

```python
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
import time

class DETRHandler(BaseHandler):
    """DETR 目标检测模型的处理器。"""

    def load(self, model_id: str) -> tuple:
        """加载 DETR 模型和处理器。"""
        processor = DetrImageProcessor.from_pretrained(model_id)
        model = DetrForObjectDetection.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor

    def infer(self, model, processor, image, **params):
        """运行 DETR 推理。"""
        start = time.perf_counter()

        conf = params.get("conf", 0.25)

        # BGR 转 PIL
        pil_image = self.bgr_to_pil(image)

        # 预处理
        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = {k: self._to_device(v) for k, v in inputs.items()}

        # 推理
        with torch.no_grad():
            outputs = model(**inputs)

        # 后处理
        target_sizes = torch.tensor([pil_image.size[::-1]])
        results = processor.post_process_object_detection(
            outputs,
            threshold=conf,
            target_sizes=target_sizes
        )[0]

        # 格式化检测
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

处理 BLIP 图像描述。

```python
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
import time

class BLIPCaptionHandler(BaseHandler):
    """BLIP 图像描述的处理器。"""

    def load(self, model_id: str) -> tuple:
        """加载 BLIP 描述模型。"""
        processor = BlipProcessor.from_pretrained(model_id)
        model = BlipForConditionalGeneration.from_pretrained(model_id)
        model = self._model_to_device(model)
        model.eval()
        return model, processor

    def infer(self, model, processor, image, **params):
        """生成图像描述。"""
        start = time.perf_counter()

        max_length = params.get("max_length", 50)

        # BGR 转 PIL
        pil_image = self.bgr_to_pil(image)

        # 预处理
        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = {k: self._to_device(v) for k, v in inputs.items()}

        # 生成
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_length=max_length
            )

        # 解码
        caption = processor.decode(output_ids[0], skip_special_tokens=True)

        inference_time = (time.perf_counter() - start) * 1000

        return {
            "caption": caption,
            "inference_time": inference_time,
            "model": model.name_or_path
        }
```

---

## 🔌 处理器注册

### ModelCategory 枚举

```python
from enum import Enum

class ModelCategory(Enum):
    """模型分类类别。"""
    YOLO_DETECT = "yolo_detect"
    YOLO_SEGMENT = "yolo_segment"
    YOLO_POSE = "yolo_pose"
    HF_DETR = "hf_detr"
    HF_OWL_VIT = "hf_owl_vit"
    HF_GROUNDING_DINO = "hf_grounding_dino"
    HF_BLIP_CAPTION = "hf_blip_caption"
    HF_BLIP_VQA = "hf_blip_vqa"
```

### 类别到处理器映射

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

### 模型注册表

```python
MODEL_REGISTRY = {
    # YOLO 检测
    "yolov8n.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Nano",
        "description": "最快的检测模型"
    },
    "yolov8s.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Small",
        "description": "速度与精度平衡"
    },

    # DETR
    "facebook/detr-resnet-50": {
        "category": ModelCategory.HF_DETR,
        "name": "DETR ResNet-50",
        "description": "端到端目标检测"
    },

    # BLIP
    "Salesforce/blip-image-captioning-base": {
        "category": ModelCategory.HF_BLIP_CAPTION,
        "name": "BLIP Caption",
        "description": "图像描述模型"
    },
}
```

---

## 🆕 添加新处理器

### 步骤 1：创建处理器类

```python
# app/handlers/my_handler.py
from app.handlers.base import BaseHandler
import time

class MyModelHandler(BaseHandler):
    """MyModel 的处理器。"""

    def load(self, model_id: str) -> tuple:
        """加载模型和处理器。"""
        # 你的加载逻辑
        model = load_my_model(model_id)
        processor = load_my_processor(model_id) if needed else None

        if hasattr(model, 'to'):
            model = model.to(self.device)

        return model, processor

    def infer(self, model, processor, image, **params):
        """运行推理。"""
        start = time.perf_counter()

        # 预处理
        if processor:
            inputs = processor(image)
        else:
            inputs = self._preprocess(image)

        # 移动到设备
        if isinstance(inputs, dict):
            inputs = {k: self._to_device(v) for k, v in inputs.items()}
        else:
            inputs = self._to_device(inputs)

        # 推理
        with torch.no_grad():
            outputs = model(**inputs)

        # 后处理和格式化
        detections = self._parse_outputs(outputs, params)

        inference_time = (time.perf_counter() - start) * 1000

        return self.make_result(
            image=image,
            detections=detections,
            task="detect",  # 或你的任务类型
            inference_time=inference_time,
            model=getattr(model, 'name_or_path', str(model))
        )
```

### 步骤 2：在工厂中注册

```python
# app/handlers/registry.py
from app.handlers.my_handler import MyModelHandler

# 添加新类别
class ModelCategory(Enum):
    # ... 现有类别
    MY_MODEL = "my_model"

# 注册处理器
_CATEGORY_HANDLER_MAP = {
    # ... 现有映射
    ModelCategory.MY_MODEL: MyModelHandler,
}

# 添加到注册表
MODEL_REGISTRY["my-model-id"] = {
    "category": ModelCategory.MY_MODEL,
    "name": "My Model",
    "description": "我的模型描述"
}
```

### 步骤 3：添加测试

```python
# tests/test_api.py
def test_my_model_handler():
    handler = MyModelHandler(device="cpu")
    model, processor = handler.load("my-model-id")

    # 创建测试图像
    image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    result = handler.infer(model, processor, image, conf=0.5)

    assert "detections" in result
    assert "inference_time" in result
```

---

## 🔗 相关文档

- 🏗️ **[架构概述](./overview.zh-CN.md)** — 高层次系统设计
- 📖 **[添加模型](../guides/adding-models.zh-CN.md)** — 分步指南
- 🔍 **[REST API](../api/rest-api.zh-CN.md)** — API 端点参考

---

<div align="center">

**[⬆ 返回顶部](#处理器模式)**

</div>
