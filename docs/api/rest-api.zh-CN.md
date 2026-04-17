# REST API 参考

YOLO-Toys HTTP API 完整参考文档。

<p align="center">
  <a href="rest-api.md">English</a> •
  <a href="./">⬅ 返回 API 参考</a>
</p>

---

## 📋 概述

基础 URL: `http://localhost:8000`

所有 API 响应均为 JSON 格式。错误遵循标准 HTTP 状态码约定。

### 内容类型

| 端点 | 内容类型 |
|------|----------|
| `GET` 端点 | `application/json` |
| 文件上传 `POST` 端点 | `multipart/form-data` |

---

## 🔍 接口列表

### 健康检查

检查服务器状态和系统信息。

```http
GET /health
```

**响应：**
```json
{
  "status": "ok",
  "version": "3.1.0",
  "device": "cuda:0",
  "default_model": "yolov8n.pt",
  "defaults": {
    "conf": 0.25,
    "iou": 0.45,
    "max_det": 300
  }
}
```

---

### 列出模型

获取所有可用模型，按类别分组。

```http
GET /models
```

**响应：**
```json
{
  "categories": {
    "yolo_detect": {
      "name": "YOLO Detection",
      "models": [
        {
          "id": "yolov8n.pt",
          "name": "YOLOv8 Nano",
          "description": "Fastest detection model"
        }
      ]
    }
  }
}
```

---

### 获取模型详情

获取特定模型的详细信息。

```http
GET /models/{model_id}
```

**参数：**
| 名称 | 类型 | 描述 |
|------|------|------|
| `model_id` | string | 模型标识符（如 `yolov8n.pt`）|

**响应 (200 OK)：**
```json
{
  "id": "yolov8n.pt",
  "category": "yolo_detect",
  "name": "YOLOv8 Nano",
  "description": "Fastest detection model",
  "task": "detect",
  "parameters": {
    "conf": {"default": 0.25, "min": 0.0, "max": 1.0},
    "iou": {"default": 0.45, "min": 0.0, "max": 1.0}
  }
}
```

**响应 (404 Not Found)：**
```json
{
  "detail": "Model not found: unknown-model"
}
```

---

### 获取模型标签

获取分类模型的类别标签。

```http
GET /labels?model={model_id}
```

**查询参数：**
| 名称 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `model` | string | 否 | 模型标识符（默认为配置的模型）|

**响应：**
```json
{
  "model": "yolov8n.pt",
  "labels": ["person", "car", "dog", ...]
}
```

---

### 单图推理

对单张图像进行推理。

```http
POST /infer
```

**内容类型：** `multipart/form-data`

**参数：**
| 名称 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `file` | File | 是 | - | 图像文件（JPEG、PNG、WEBP）|
| `model` | string | 否 | `yolov8n.pt` | 模型标识符 |
| `conf` | float | 否 | 0.25 | 置信度阈值 (0.0-1.0) |
| `iou` | float | 否 | 0.45 | NMS 的 IoU 阈值 (0.0-1.0) |
| `max_det` | int | 否 | 300 | 最大检测数 (1-1000) |
| `device` | string | 否 | auto | 推理设备 (cpu/cuda/mps) |
| `imgsz` | int | 否 | 640 | 推理图像尺寸 (32-4096) |
| `half` | bool | 否 | false | 启用 FP16 半精度 |
| `text_queries` | string | 否 | - | 开放词汇检测的文本查询（逗号分隔）|
| `question` | string | 否 | - | VQA 模型的问题（最多 500 字符）|

**响应 (200 OK)：**
```json
{
  "width": 640,
  "height": 480,
  "task": "detect",
  "detections": [
    {
      "bbox": [100.5, 200.3, 250.8, 450.2],
      "score": 0.89,
      "label": "person",
      "track_id": null
    }
  ],
  "inference_time": 12.5,
  "model": "yolov8n.pt"
}
```

**响应 (400 Bad Request)：**
```json
{
  "detail": "Invalid image format"
}
```

**响应 (500 Internal Server Error)：**
```json
{
  "detail": "Model inference failed: {error_message}"
}
```

---

### 图像描述

为图像自动生成描述。

```http
POST /caption
```

**内容类型：** `multipart/form-data`

**参数：**
| 名称 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `file` | File | 是 | - | 图像文件 |
| `model` | string | 否 | `Salesforce/blip-image-captioning-base` | 描述模型 |

**响应：**
```json
{
  "caption": "a person riding a skateboard on a street",
  "inference_time": 120.5,
  "model": "Salesforce/blip-image-captioning-base"
}
```

---

### 视觉问答

回答关于图像的问题。

```http
POST /vqa
```

**内容类型：** `multipart/form-data`

**参数：**
| 名称 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `file` | File | 是 | - | 图像文件 |
| `question` | string | 是 | - | 关于图像的问题 |
| `model` | string | 否 | `Salesforce/blip-vqa-base` | VQA 模型 |

**响应：**
```json
{
  "answer": "blue",
  "inference_time": 95.2,
  "model": "Salesforce/blip-vqa-base",
  "question": "What color is the car?"
}
```

---

## 🚦 错误码

| 状态码 | 含义 | 描述 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 输入参数无效 |
| 404 | Not Found | 模型或资源未找到 |
| 413 | Payload Too Large | 文件超出大小限制 |
| 422 | Unprocessable Entity | 验证错误 |
| 500 | Internal Server Error | 服务器处理错误 |
| 503 | Service Unavailable | 模型加载中或系统不可用 |

---

## 📊 检测结果格式

### 边界框格式

边界框以像素坐标 `[x1, y1, x2, y2]` 返回：
- `x1`：左边坐标
- `y1`：顶边坐标
- `x2`：右边坐标
- `y2`：底边坐标

### 检测类型

| 任务 | 附加字段 |
|------|----------|
| `detect` | `bbox`、`score`、`label` |
| `segment` | `bbox`、`score`、`label`、`polygons` |
| `pose` | `bbox`、`score`、`label`、`keypoints` |

### 分割多边形

```json
{
  "polygons": [
    [[x1, y1], [x2, y2], [x3, y3], ...],
    ...
  ]
}
```

### 姿态关键点

```json
{
  "keypoints": [
    {"x": 100, "y": 200, "confidence": 0.95},  // 鼻子
    {"x": 95, "y": 210, "confidence": 0.92},   // 左眼
    ...
  ]
}
```

关键点索引（COCO 格式）：
0. 鼻子
1. 左眼
2. 右眼
3. 左耳
4. 右耳
5. 左肩
6. 右肩
7. 左肘
8. 右肘
9. 左手腕
10. 右手腕
11. 左髋
12. 右髋
13. 左膝
14. 右膝
15. 左脚踝
16. 右脚踝

---

## 🔗 下一步

- 🔌 **[WebSocket 协议](./websocket.zh-CN.md)** — 实时流传输 API
- 🏗️ **[架构设计](../architecture/overview.zh-CN.md)** — 系统架构概述
- 📋 **[模型列表](../reference/models.md)** — 支持的模型参考

---

<div align="center">

**[⬆ 返回顶部](#rest-api-参考)**

</div>
