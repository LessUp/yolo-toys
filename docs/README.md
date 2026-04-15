# YOLO-Toys 技术文档

> 深入理解多模型实时视觉识别平台的架构与实现

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术架构](#2-技术架构)
3. [后端实现](#3-后端实现)
4. [前端实现](#4-前端实现)
5. [API 参考](#5-api-参考)
6. [部署指南](#6-部署指南)
7. [扩展开发](#7-扩展开发)
8. [常见问题](#8-常见问题)

---

## 1. 项目概述

### 1.1 简介

YOLO-Toys 是一个基于 FastAPI + YOLOv8 + HuggingFace Transformers 的多模型实时视觉识别平台，支持：

- **目标检测**: YOLOv8 系列 (n/s/m/l/x)
- **实例分割**: YOLOv8-seg 系列
- **姿态估计**: YOLOv8-pose 系列
- **Transformer 检测**: DETR ResNet-50/101
- **开放词汇检测**: OWL-ViT、Grounding DINO
- **多模态**: BLIP 图像描述、视觉问答

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| WebSocket 流式推理 | 低延迟实时视频分析 |
| 策略模式架构 | 新增模型零耦合扩展 |
| 自动设备选择 | CUDA / MPS / CPU 自动检测 |
| FP16 加速 | NVIDIA GPU 半精度推理 |
| 并发控制 | Semaphore 限制同时推理数 |
| 模型缓存 | 首次加载后复用，避免重复初始化 |

### 1.3 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI + Uvicorn | 0.111+ |
| 检测模型 | Ultralytics YOLOv8 | Latest |
| Transformer | HuggingFace Transformers | Latest |
| 深度学习 | PyTorch | 2.0+ |
| 图像处理 | OpenCV (headless) | 4.x |
| 配置管理 | Pydantic Settings | 2.x |
| 前端 | HTML + CSS + ES Modules | - |
| 容器化 | Docker + docker-compose | - |
| 代码质量 | Ruff + pre-commit | - |

---

## 2. 技术架构

### 2.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (ES Modules)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │camera.js │  │ draw.js  │  │  api.js  │  │   app.js    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘  │
│       └─────────────┴────────────┴────────────────┘          │
└──────────────────────────┬───────────────────────────────────┘
                           │ REST / WebSocket
┌──────────────────────────┴───────────────────────────────────┐
│                  FastAPI Backend (routes.py)                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              ModelManager (model_manager.py)             │ │
│  │   load_model() → cache    infer() → route to handler    │ │
│  └────────────────────────────┬────────────────────────────┘ │
│                               │                              │
│  ┌────────────────────────────┴────────────────────────────┐ │
│  │             HandlerRegistry (registry.py)               │ │
│  │   MODEL_REGISTRY → category → handler class mapping     │ │
│  └────┬──────────┬──────────┬──────────┬─────────┬────────┘ │
│       │          │          │          │         │          │
│    ┌──┴───┐  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐       │
│    │ YOLO │  │ DETR │  │OWLViT│  │G-DINO│  │ BLIP │       │
│    └──────┘  └──────┘  └──────┘  └──────┘  └──────┘       │
│         BaseHandler 策略模式 — 统一 load() + infer()        │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 设计模式

#### 策略模式 (Strategy Pattern)

所有模型处理器继承 `BaseHandler` 抽象基类：

```python
# app/handlers/base.py
class BaseHandler(ABC):
    @abstractmethod
    def load(self, model_id: str) -> tuple[Any, Any | None]: ...
    
    @abstractmethod
    def infer(self, model, processor, image, **params) -> dict: ...
```

新增模型只需：
1. 创建 Handler 继承 `BaseHandler`
2. 实现 `load()` 和 `infer()`
3. 在 `registry.py` 注册

#### 注册表模式 (Registry Pattern)

```python
# app/handlers/registry.py
MODEL_REGISTRY = {
    "yolov8n.pt": {"category": ModelCategory.YOLO_DETECT, ...},
    "facebook/detr-resnet-50": {"category": ModelCategory.HF_DETR, ...},
    ...
}

_CATEGORY_HANDLER_MAP = {
    ModelCategory.YOLO_DETECT: YOLOHandler,
    ModelCategory.HF_DETR: DETRHandler,
    ...
}
```

### 2.3 数据流

```
HTTP Request (image file)
    │
    ▼
routes.py: infer()
    │
    ▼
ModelManager.infer(model_id, image, ...)
    │
    ├── load_model(model_id) [cached]
    │       │
    │       ▼
    │   HandlerRegistry.get_handler(model_id)
    │       │
    │       ▼
    │   handler.load(model_id) → (model, processor)
    │
    ▼
handler.infer(model, processor, image, ...)
    │
    ▼
BaseHandler.make_result() → dict
    │
    ▼
JSON Response
```

---

## 3. 后端实现

### 3.1 目录结构

```
app/
├── main.py             # FastAPI 入口 + lifespan 生命周期
├── config.py           # Pydantic Settings 配置
├── routes.py           # REST + WebSocket 路由
├── model_manager.py    # 模型缓存与处理器委托
├── schemas.py          # Pydantic 响应模型
└── handlers/           # 策略模式处理器
    ├── __init__.py
    ├── base.py         # BaseHandler 抽象基类
    ├── registry.py     # 模型注册表 + 工厂
    ├── yolo_handler.py # YOLO 检测/分割/姿态
    ├── hf_handler.py   # DETR / OWL-ViT / Grounding DINO
    └── blip_handler.py # BLIP Caption / VQA
```

### 3.2 配置管理 (config.py)

使用 Pydantic Settings 从环境变量读取配置：

```python
class AppSettings(BaseSettings):
    model_config = {"env_file": ".env"}
    
    port: int = Field(default=8000, alias="PORT")
    model_name: str = Field(default="yolov8s.pt", alias="MODEL_NAME")
    conf_threshold: float = Field(default=0.25, alias="CONF_THRESHOLD")
    device: str = Field(default="", alias="DEVICE")  # auto-detect if empty
    skip_warmup: bool = Field(default=False, alias="SKIP_WARMUP")
    ...
```

### 3.3 模型管理器 (model_manager.py)

```python
class ModelManager:
    def __init__(self):
        self._device = get_device()  # auto: cuda > mps > cpu
        self._registry = HandlerRegistry(self._device)
        self._cache: dict[str, tuple] = {}  # model_id → (model, processor)
    
    def load_model(self, model_id: str) -> Any:
        if model_id in self._cache:
            return self._cache[model_id][0]
        handler = self._registry.get_handler(model_id)
        model, processor = handler.load(model_id)
        self._cache[model_id] = (model, processor)
        return model
    
    def infer(self, model_id, image, **params) -> dict:
        self.load_model(model_id)  # ensure loaded
        handler = self._registry.get_handler(model_id)
        model, processor = self._cache[model_id]
        return handler.infer(model, processor, image, **params)
```

### 3.4 处理器实现示例

#### YOLO Handler

```python
class YOLOHandler(BaseHandler):
    def load(self, model_id: str) -> tuple[Any, None]:
        from ultralytics import YOLO
        return YOLO(model_id), None  # YOLO 不需要单独 processor
    
    def infer(self, model, processor, image, conf, iou, max_det, device, ...):
        results = model(image, conf=conf, iou=iou, max_det=max_det, device=device)
        task = self._resolve_task(model, results[0])
        dets = self._parse_detections(results[0], task)
        return self.make_result(image, detections=dets, task=task, ...)
```

#### HuggingFace Handler (DETR)

```python
class DETRHandler(BaseHandler):
    def load(self, model_id: str):
        processor = DetrImageProcessor.from_pretrained(model_id)
        model = DetrForObjectDetection.from_pretrained(model_id)
        model = self._model_to_device(model)
        return model, processor
    
    def infer(self, model, processor, image, conf, ...):
        pil_image = self.bgr_to_pil(image)
        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = self._to_device(inputs)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        results = processor.post_process_object_detection(outputs, threshold=conf)[0]
        dets = [...]  # parse results
        return self.make_result(image, detections=dets, task="detect", ...)
```

---

## 4. 前端实现

### 4.1 目录结构

```
frontend/
├── index.html      # UI 界面
├── style.css       # 深色/浅色主题
├── app.js          # 主入口 (ES Module)
└── js/
    ├── api.js      # HTTP/WebSocket 通信
    ├── camera.js   # 摄像头控制
    └── draw.js     # Canvas 绘制
```

### 4.2 核心模块

#### api.js — 通信层

```javascript
// HTTP 推理
export async function infer(imageBlob, params) {
    const formData = new FormData();
    formData.append('file', imageBlob);
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`/infer?${query}`, { method: 'POST', body: formData });
    return response.json();
}

// WebSocket 连接
export function createWebSocket(params, onMessage, onError) {
    const query = new URLSearchParams(params).toString();
    const ws = new WebSocket(`ws://${location.host}/ws?${query}`);
    ws.onmessage = (e) => onMessage(JSON.parse(e.data));
    ws.onerror = onError;
    return ws;
}
```

#### draw.js — 绘制层

```javascript
export function drawDetections(ctx, detections, scale, colors) {
    for (const det of detections) {
        const [x, y, w, h] = det.bbox.map(v => v * scale);
        const color = colors[det.label] || defaultColor;
        
        // 绘制边界框
        ctx.strokeStyle = color;
        ctx.strokeRect(x, y, w, h);
        
        // 绘制标签
        ctx.fillStyle = color;
        ctx.fillText(`${det.label} ${det.score.toFixed(2)}`, x, y - 5);
        
        // 绘制掩膜 (如果有)
        if (det.polygons) { ... }
        
        // 绘制关键点 (如果有)
        if (det.keypoints) { ... }
    }
}
```

### 4.3 设置持久化

```javascript
// 保存到 localStorage
function saveSettings() {
    const settings = {
        model: modelSelect.value,
        conf: confInput.value,
        theme: document.documentElement.dataset.theme,
        ...
    };
    localStorage.setItem('yolo-toys-settings', JSON.stringify(settings));
}

// 加载设置
function loadSettings() {
    const saved = localStorage.getItem('yolo-toys-settings');
    if (saved) {
        const settings = JSON.parse(saved);
        modelSelect.value = settings.model;
        confInput.value = settings.conf;
        ...
    }
}
```

---

## 5. API 参考

### 5.1 REST 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `GET` | `/models` | 列出所有模型 |
| `GET` | `/models/{model_id}` | 获取模型详情 |
| `GET` | `/labels` | 获取模型标签 |
| `POST` | `/infer` | 统一推理 |
| `POST` | `/caption` | 图像描述 |
| `POST` | `/vqa` | 视觉问答 |

### 5.2 WebSocket 端点

**URL:** `ws://host/ws?model=...&conf=...&iou=...`

**消息类型:**

| 类型 | 方向 | 说明 |
|------|------|------|
| 二进制帧 | Client → Server | JPEG 图像 |
| `{type: "config", ...}` | Client → Server | 更新参数 |
| `{type: "result", data: {...}}` | Server → Client | 推理结果 |
| `{type: "error", detail: "..."}` | Server → Client | 错误信息 |

### 5.3 响应格式

```json
{
    "width": 640,
    "height": 480,
    "task": "detect",
    "detections": [
        {
            "bbox": [x1, y1, x2, y2],
            "score": 0.89,
            "label": "person",
            "polygons": [[...]],      // 可选，分割任务
            "keypoints": [[x, y], ...] // 可选，姿态任务
        }
    ],
    "inference_time": 5.2,
    "model": "yolov8n.pt"
}
```

---

## 6. 部署指南

### 6.1 本地开发

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 启动服务
python -m uvicorn app.main:app --reload --port 8000
```

### 6.2 Docker 部署

```bash
# 构建镜像
docker build -t yolo-toys .

# 运行容器
docker run -d -p 8000:8000 \
    -e MODEL_NAME=yolov8s.pt \
    -e DEVICE=cpu \
    yolo-toys
```

### 6.3 Docker Compose

```yaml
# docker-compose.yml
services:
  yolo-toys:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_NAME=yolov8s.pt
      - SKIP_WARMUP=0
    volumes:
      - model-cache:/root/.cache  # 模型缓存
```

```bash
docker-compose up -d
```

### 6.4 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | `8000` | 服务端口 |
| `MODEL_NAME` | `yolov8s.pt` | 默认模型 |
| `CONF_THRESHOLD` | `0.25` | 置信度阈值 |
| `IOU_THRESHOLD` | `0.45` | NMS IoU 阈值 |
| `MAX_DET` | `300` | 最大检测数 |
| `DEVICE` | `auto` | 设备 (cpu/cuda:0/mps) |
| `SKIP_WARMUP` | `false` | 跳过预热 |
| `MAX_CONCURRENCY` | `4` | 并发限制 |
| `ALLOW_ORIGINS` | `*` | CORS 来源 |

---

## 7. 扩展开发

### 7.1 添加新模型

**Step 1: 创建 Handler**

```python
# app/handlers/my_handler.py
from app.handlers.base import BaseHandler

class MyModelHandler(BaseHandler):
    def load(self, model_id: str):
        # 加载模型和处理器
        from my_library import MyModel, MyProcessor
        processor = MyProcessor.from_pretrained(model_id)
        model = MyModel.from_pretrained(model_id)
        model = self._model_to_device(model)
        return model, processor
    
    def infer(self, model, processor, image, **params):
        # 执行推理
        result = model(processor(image))
        dets = [...]  # 解析结果
        return self.make_result(image, detections=dets, task="detect", ...)
```

**Step 2: 注册模型**

```python
# app/handlers/registry.py
class ModelCategory:
    MY_MODEL = "my_model"

_CATEGORY_HANDLER_MAP = {
    ModelCategory.MY_MODEL: MyModelHandler,
    ...
}

MODEL_REGISTRY["my-model-id"] = {
    "category": ModelCategory.MY_MODEL,
    "name": "My Model",
    "description": "描述",
}
```

### 7.2 添加新端点

```python
# app/routes.py
@router.post("/my-endpoint")
async def my_endpoint(file: UploadFile = File(...)):
    img = await _read_upload_image(file)
    result = await asyncio.to_thread(
        model_manager.infer,
        model_id="my-model",
        image=img,
    )
    return result
```

### 7.3 自定义前端

前端使用 ES Modules，可以自由扩展 `frontend/js/` 下的模块。

---

## 8. 常见问题

### Q: 模型下载慢？

A: YOLO 权重从 Ultralytics 服务器下载，HuggingFace 模型从 HF Hub 下载。可以：
- 使用镜像站点
- 手动下载后放到缓存目录
- 使用 Docker 挂载模型缓存卷

### Q: GPU 不被识别？

A: 检查：
1. CUDA 是否正确安装：`nvidia-smi`
2. PyTorch CUDA 版本：`python -c "import torch; print(torch.cuda.is_available())"`
3. 设置 `DEVICE=cuda:0`

### Q: WebSocket 断开重连？

A: 前端实现了自动重连机制，检查网络稳定性和服务器日志。

### Q: 内存占用高？

A: 每个模型加载后缓存在内存中，可以通过：
- 使用更小的模型 (yolov8n)
- 限制 `MAX_CONCURRENCY`
- 设置 Docker 内存限制

---

## 相关链接

- [项目 README](../README.md)
- [贡献指南](../CONTRIBUTING.md)
- [更新日志](./)
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [HuggingFace Transformers](https://github.com/huggingface/transformers)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
