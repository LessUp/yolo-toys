# 系统架构概述

理解 YOLO-Toys 的设计原则和数据流。

<p align="center">
  <a href="overview.md">English</a> •
  <a href="./">⬅ 返回架构文档</a>
</p>

---

## 📐 高层次架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端层                                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │   摄像头    │ │   Canvas   │ │ API 客户端  │ │ WebSocket  │   │
│  │   模块     │ │   渲染器    │ │   (HTTP)   │ │   客户端    │   │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘   │
│         └──────────────┴──────────────┴────────────────┘        │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ REST / WebSocket
┌─────────────────────────────────┴───────────────────────────────┐
│                     FastAPI 后端层                               │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ModelManager (路由/缓存)                     │   │
│  │       load_model() → 缓存    infer() → 委托              │   │
│  └────────────────────────┬────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────┴────────────────────────────────┐   │
│  │              HandlerRegistry (工厂)                       │   │
│  │    MODEL_REGISTRY → 解析处理器 → 实例化                    │   │
│  └────┬──────────┬──────────┬──────────┬──────────┬────────┘   │
│       │          │          │          │          │             │
│  ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐       │
│  │  YOLO  │ │  DETR  │ │OWLViT  │ │Ground. │ │  BLIP  │       │
│  │处理器  │ │处理器  │ │处理器  │ │ DINO   │ │处理器  │       │
│  └──┬─────┘ └──┬─────┘ └──┬─────┘ └──┬─────┘ └──┬─────┘       │
│     │          │          │          │          │              │
│     └──────────┴──────────┴──────────┴──────────┘              │
│                    BaseHandler (抽象类)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 数据流

### REST API 请求流

```
1. HTTP 请求（图像文件）
        │
        ▼
2. FastAPI 路由 (routes.py)
   - 解析 multipart 表单数据
   - 验证参数
   - 读取图像字节
        │
        ▼
3. ModelManager.infer()
   - 检查模型缓存
   - 如未缓存则加载
        │
        ▼
4. HandlerRegistry.get_handler()
   - 查询模型类别
   - 返回处理器实例
        │
        ▼
5. Handler.load()（如需要）
   - 加载模型权重
   - 初始化处理器
   - 移动到设备
        │
        ▼
6. Handler.infer()
   - 预处理图像
   - 运行推理
   - 后处理结果
        │
        ▼
7. BaseHandler.make_result()
   - 格式化检测
   - 添加元数据
        │
        ▼
8. JSON 响应
```

### WebSocket 流式传输流

```
1. WebSocket 连接
   - 查询参数解析
   - 模型预加载
        │
        ▼
2. 二进制帧接收
   - JPEG 解码
   - 验证
        │
        ▼
3. 推理流水线
   - 同 REST（步骤 3-6）
        │
        ▼
4. JSON 结果推送
   - 实时传递
   - 并发处理
```

---

## 🧩 设计模式

### 1. 策略模式 (Handler 系统)

所有模型类型实现通用接口：

```python
class BaseHandler(ABC):
    @abstractmethod
    def load(self, model_id: str) -> tuple[Any, Any | None]:
        """加载模型和处理器"""
        pass
    
    @abstractmethod
    def infer(self, model, processor, image, **params) -> dict:
        """运行推理并返回格式化结果"""
        pass
```

**优点：**
- 无需修改现有代码即可添加新模型类型
- 所有模型实现一致的接口
- 便于使用模拟处理器测试

### 2. 注册表模式

集中式模型注册和查询：

```python
MODEL_REGISTRY = {
    "yolov8n.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Nano",
        "task": "detect"
    },
    # ... 更多模型
}

_CATEGORY_HANDLER_MAP = {
    ModelCategory.YOLO_DETECT: YOLOHandler,
    ModelCategory.HF_DETR: DETRHandler,
    # ... 更多映射
}
```

**优点：**
- 模型元数据的单一事实来源
- 动态处理器解析
- 运行时模型发现

### 3. 模板方法模式

BaseHandler 提供通用工具方法：

```python
class BaseHandler(ABC):
    def make_result(self, image, detections, task, **kwargs) -> dict:
        """标准化结果格式"""
        return {
            "width": image.shape[1],
            "height": image.shape[0],
            "task": task,
            "detections": detections,
            "inference_time": kwargs.get("inference_time"),
            "model": kwargs.get("model")
        }
    
    def _to_device(self, tensor):
        """将张量移动到配置的设备"""
        return tensor.to(self.device)
```

**优点：**
- 处理器间结果格式一致
- 共享工具方法
- 减少代码重复

### 4. 工厂模式

HandlerRegistry 充当工厂：

```python
class HandlerRegistry:
    def get_handler(self, model_id: str) -> BaseHandler:
        category = MODEL_REGISTRY[model_id]["category"]
        handler_class = _CATEGORY_HANDLER_MAP[category]
        return handler_class(self.device)
```

**优点：**
- 封装对象创建
- 易于扩展新处理器类型
- 集中配置注入

---

## 📦 组件详情

### ModelManager

**职责：**
- 模型生命周期管理（加载/卸载）
- 缓存管理
- 并发控制

```python
class ModelManager:
    def __init__(self):
        self._device = get_device()
        self._registry = HandlerRegistry(self._device)
        self._cache: dict[str, tuple] = {}
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
```

### HandlerRegistry

**职责：**
- 模型类别解析
- 处理器实例化
- 设备配置注入

### 处理器

| 处理器 | 模型 | 任务 |
|--------|------|------|
| YOLOHandler | YOLOv8 (n/s/m/l/x) | 检测、分割、姿态 |
| DETRHandler | facebook/detr-* | 目标检测 |
| OWLViTHandler | google/owlvit-* | 开放词汇检测 |
| GroundingDINOHandler | grounding-dino-* | 文本提示检测 |
| BLIPCaptionHandler | Salesforce/blip-* | 图像描述 |
| BLIPVQAHandler | Salesforce/blip-vqa-* | 视觉问答 |

---

## 🔄 请求生命周期

### 启动序列

```
1. FastAPI lifespan 启动
        │
        ▼
2. 创建 ModelManager 实例
        │
        ▼
3.（可选）预热默认模型
        │
        ▼
4. 接受连接
```

### 每请求序列

```
1. 接收请求 (HTTP/WebSocket)
        │
        ▼
2. 获取信号量槽
   （限制并发推理）
        │
        ▼
3. 加载模型（如未缓存）
   - Handler.load()
   - 缓存结果
        │
        ▼
4. 运行推理
   - Handler.infer()
        │
        ▼
5. 格式化响应
        │
        ▼
6. 释放信号量
```

---

## 🔧 配置

### 环境驱动配置

```python
class AppSettings(BaseSettings):
    model_config = {"env_file": ".env"}
    
    # 服务器设置
    port: int = Field(default=8000, alias="PORT")
    
    # 模型设置
    model_name: str = Field(default="yolov8n.pt", alias="MODEL_NAME")
    device: str = Field(default="auto", alias="DEVICE")
    
    # 性能设置
    max_concurrency: int = Field(default=4, alias="MAX_CONCURRENCY")
```

### 设备自动检测

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

## 📊 性能特性

### 缓存策略

- 模型首次使用时加载并缓存到内存
- 缓存键：model_id 字符串
- 缓存值：(model, processor) 元组
- 模型在服务器重启前保持缓存

### 并发控制

- `asyncio.Semaphore` 限制并发推理
- 默认限制：4 个并发请求
- 额外请求进入队列等待

### 内存管理

- 每个缓存模型占用 GPU/CPU 内存
- 模型越大 = 内存使用越多
- 如遇 OOM，使用较小模型或降低 `MAX_CONCURRENCY`

---

## 🔗 相关文档

- 🔌 **[处理器模式](./handlers.zh-CN.md)** — 处理器实现详情
- 🔍 **[REST API](../api/rest-api.zh-CN.md)** — API 端点参考
- 🔌 **[WebSocket](../api/websocket.zh-CN.md)** — 流式传输协议
- 📋 **[模型列表](../reference/models.md)** — 支持的模型列表

---

<div align="center">

**[⬆ 返回顶部](#系统架构概述)**

</div>
