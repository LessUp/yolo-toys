# 添加自定义模型

扩展 YOLO-Toys 以支持你自己的模型的分步指南。

<p align="center">
  <a href="adding-models.md">English</a> •
  <a href="./">⬅ 返回指南</a>
</p>

---

## 📋 前提条件

在添加新模型之前，确保你具备：

- [ ] 已安装 Python 3.11+
- [ ] 已设置 YOLO-Toys 开发环境
- [ ] 理解要添加的模型
- [ ] 熟悉 PyTorch 或模型的框架

---

## 🚀 快速开始

添加模型需要 3 个步骤：

1. **创建处理器** — 实现 `load()` 和 `infer()` 方法
2. **注册模型** — 添加元数据到注册表
3. **添加测试** — 验证实现

总时间：简单模型约 30 分钟

---

## 📝 步骤 1：创建处理器

### 1.1 创建处理器文件

在 `app/handlers/` 中创建新文件：

```bash
touch app/handlers/my_model_handler.py
```

### 1.2 实现处理器

模板如下：

```python
# app/handlers/my_model_handler.py
"""MyModel 的处理器。"""

import time
from typing import Any, Optional, Tuple
import numpy as np
import torch

from app.handlers.base import BaseHandler


class MyModelHandler(BaseHandler):
    """
    MyModel 推理的处理器。
    
    支持：目标检测、分类等。
    """
    
    def load(self, model_id: str) -> Tuple[Any, Optional[Any]]:
        """
        加载模型和可选处理器。
        
        参数:
            model_id: 模型标识符（如 'my-model-v1'）
            
        返回:
            (model, processor) 元组
        """
        # 示例：从 HuggingFace 加载
        from transformers import AutoProcessor, AutoModel
        
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)
        
        # 移动到配置的设备
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
        在图像上运行推理。
        
        参数:
            model: 已加载的模型
            processor: 可选处理器
            image: 输入图像（BGR 格式，numpy 数组）
            **params: 推理参数
            
        返回:
            标准化结果字典
        """
        start = time.perf_counter()
        
        # 提取参数
        conf = params.get("conf", 0.25)
        
        # 预处理
        # 如需处理则将 BGR (OpenCV) 转 PIL
        pil_image = self.bgr_to_pil(image)
        
        if processor:
            inputs = processor(images=pil_image, return_tensors="pt")
        else:
            # 自定义预处理
            inputs = self._preprocess(image)
        
        # 移动到设备
        if isinstance(inputs, dict):
            inputs = {k: self._to_device(v) for k, v in inputs.items()}
        else:
            inputs = self._to_device(inputs)
        
        # 推理
        with torch.no_grad():
            outputs = model(**inputs)
        
        # 后处理
        detections = self._parse_outputs(outputs, image.shape[:2], conf)
        
        inference_time = (time.perf_counter() - start) * 1000
        
        # 返回标准格式
        return self.make_result(
            image=image,
            detections=detections,
            task="detect",  # 或 "classify", "segment" 等
            inference_time=inference_time,
            model=getattr(model, 'name_or_path', str(model))
        )
    
    def _preprocess(self, image: np.ndarray) -> torch.Tensor:
        """如无处理器可用的自定义预处理。"""
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
        将模型输出解析为标准检测格式。
        
        返回包含以下键的字典列表：
        - bbox: [x1, y1, x2, y2]（像素坐标）
        - score: float (0-1)
        - label: str（类别名）
        """
        detections = []
        
        # 示例：解析检测输出
        # 根据模型输出格式调整
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

### 1.3 常见模式

#### YOLO 风格模型

```python
def load(self, model_id: str):
    from ultralytics import YOLO
    model = YOLO(model_id)
    return model, None

def infer(self, model, processor, image, **params):
    results = model(image, conf=params.get('conf', 0.25))
    # 解析 YOLO 结果
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
    # 运行推理
```

#### PyTorch Hub

```python
def load(self, model_id: str):
    model = torch.hub.load('repo', model_id)
    return self._model_to_device(model), None
```

---

## 🔌 步骤 2：注册模型

### 2.1 添加类别（如为新类型）

编辑 `app/handlers/registry.py`：

```python
from enum import Enum

class ModelCategory(Enum):
    # ... 现有类别
    MY_MODEL = "my_model"  # 添加新类别
```

### 2.2 注册处理器映射

```python
from app.handlers.my_model_handler import MyModelHandler

_CATEGORY_HANDLER_MAP = {
    # ... 现有映射
    ModelCategory.MY_MODEL: MyModelHandler,
}
```

### 2.3 添加模型元数据

```python
MODEL_REGISTRY = {
    # ... 现有模型
    "my-model-v1": {
        "category": ModelCategory.MY_MODEL,
        "name": "My Model v1",
        "description": "Custom detection model",
        "task": "detect",  # 或 "classify", "segment"
        "parameters": {
            "conf": {"default": 0.25, "min": 0.0, "max": 1.0}
        }
    },
}
```

### 2.4 完整注册表示例

```python
# app/handlers/registry.py

from enum import Enum
from typing import Dict, Any

from app.handlers.yolo_handler import YOLOHandler
from app.handlers.hf_handler import DETRHandler, OWLViTHandler
from app.handlers.blip_handler import BLIPCaptionHandler, BLIPVQAHandler
from app.handlers.my_model_handler import MyModelHandler  # 导入新处理器


class ModelCategory(Enum):
    """处理器选择的模型类别。"""
    YOLO_DETECT = "yolo_detect"
    YOLO_SEGMENT = "yolo_segment"
    YOLO_POSE = "yolo_pose"
    HF_DETR = "hf_detr"
    HF_OWL_VIT = "hf_owl_vit"
    HF_GROUNDING_DINO = "hf_grounding_dino"
    HF_BLIP_CAPTION = "hf_blip_caption"
    HF_BLIP_VQA = "hf_blip_vqa"
    MY_MODEL = "my_model"  # 新类别


# 处理器工厂映射
_CATEGORY_HANDLER_MAP = {
    ModelCategory.YOLO_DETECT: YOLOHandler,
    ModelCategory.YOLO_SEGMENT: YOLOHandler,
    ModelCategory.YOLO_POSE: YOLOHandler,
    ModelCategory.HF_DETR: DETRHandler,
    ModelCategory.HF_OWL_VIT: OWLViTHandler,
    ModelCategory.HF_GROUNDING_DINO: GroundingDINOHandler,
    ModelCategory.HF_BLIP_CAPTION: BLIPCaptionHandler,
    ModelCategory.HF_BLIP_VQA: BLIPVQAHandler,
    ModelCategory.MY_MODEL: MyModelHandler,  # 注册处理器
}


# 模型元数据注册表
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # YOLO 模型...
    # HuggingFace 模型...
    
    # 你的自定义模型
    "my-model-v1": {
        "category": ModelCategory.MY_MODEL,
        "name": "My Model v1",
        "description": "用于特定用例的自定义检测模型",
        "task": "detect",
    },
}
```

---

## 🧪 步骤 3：添加测试

### 3.1 创建测试文件

```python
# tests/test_my_model.py
import pytest
import numpy as np
from app.handlers.my_model_handler import MyModelHandler


class TestMyModelHandler:
    """MyModelHandler 的测试。"""
    
    @pytest.fixture
    def handler(self):
        return MyModelHandler(device="cpu")
    
    @pytest.fixture
    def test_image(self):
        """创建测试图像。"""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_load(self, handler):
        """测试模型加载。"""
        model, processor = handler.load("my-model-v1")
        assert model is not None
        # 添加模型特定断言
    
    def test_infer(self, handler, test_image):
        """测试推理。"""
        model, processor = handler.load("my-model-v1")
        result = handler.infer(
            model, processor, test_image,
            conf=0.5
        )
        
        # 验证结果结构
        assert "detections" in result
        assert "inference_time" in result
        assert "task" in result
        
        # 验证检测格式
        for det in result["detections"]:
            assert "bbox" in det
            assert "score" in det
            assert "label" in det
            assert len(det["bbox"]) == 4
    
    def test_device_handling(self):
        """测试设备配置。"""
        handler = MyModelHandler(device="cpu")
        assert handler.device == "cpu"
        # 如可用则测试 GPU
        # handler = MyModelHandler(device="cuda:0")
```

### 3.2 运行测试

```bash
# 运行特定测试
pytest tests/test_my_model.py -v

# 运行所有测试
make test
```

---

## 🎨 步骤 4：前端集成（可选）

如果你的模型需要特殊 UI 处理：

### 4.1 添加模型类别显示

编辑 `frontend/index.html` 或 `frontend/app.js`：

```javascript
// 添加新类别到 UI
const MODEL_CATEGORIES = {
    // ... 现有类别
    my_model: {
        name: 'My Models',
        icon: '🎯',
        description: '自定义检测模型'
    }
};
```

### 4.2 特殊参数

如果你的模型需要自定义参数：

```javascript
// 添加自定义参数处理
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

## 📊 性能优化

### 模型缓存

模型由 ModelManager 自动缓存。首次加载可能较慢。

### FP16 推理（GPU）

```python
def load(self, model_id: str):
    model = load_model(model_id)
    model = self._model_to_device(model)
    
    # CUDA 上启用 FP16
    if self.device.startswith("cuda"):
        model = model.half()
    
    return model, processor
```

### 批处理

批处理推理支持：

```python
def infer_batch(self, model, processor, images, **params):
    """多张图像的批处理推理。"""
    # 堆叠图像
    batch = torch.stack([self._preprocess(img) for img in images])
    
    with torch.no_grad():
        outputs = model(batch)
    
    return [self._parse_single(o) for o in outputs]
```

---

## ✅ 检查清单

提交处理器前请确认：

- [ ] 处理器实现了 `load()` 和 `infer()`
- [ ] 模型已注册到 `MODEL_REGISTRY`
- [ ] 类别已添加到 `ModelCategory`
- [ ] 处理器已在 `_CATEGORY_HANDLER_MAP` 中映射
- [ ] 测试已添加并通过
- [ ] 文档已更新
- [ ] 包含类型提示
- [ ] 实现了错误处理

---

## 🔗 相关文档

- 🏗️ **[处理器模式](../architecture/handlers.zh-CN.md)** — 处理器实现详情
- 🏗️ **[架构](../architecture/overview.zh-CN.md)** — 系统架构
- 🤝 **[贡献指南](../../CONTRIBUTING.md)** — 贡献规范

---

<div align="center">

**[⬆ 返回顶部](#添加自定义模型)**

</div>
