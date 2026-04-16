# REST API Reference

Complete reference for YOLO-Toys HTTP API endpoints.

<p align="center">
  <a href="rest-api.zh-CN.md">简体中文</a> •
  <a href="./">⬅ Back to API Reference</a>
</p>

---

## 📋 Overview

Base URL: `http://localhost:8000`

All API responses are in JSON format. Errors follow the standard HTTP status code convention.

### Content Types

| Endpoint | Content-Type |
|----------|--------------|
| `GET` endpoints | `application/json` |
| `POST` endpoints with file upload | `multipart/form-data` |

---

## 🔍 Endpoints

### Health Check

Check server status and system information.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "models_loaded": 2,
  "device": "cuda:0",
  "uptime_seconds": 3600
}
```

---

### List Models

Get all available models grouped by category.

```http
GET /models
```

**Response:**
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

### Get Model Details

Get detailed information about a specific model.

```http
GET /models/{model_id}
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `model_id` | string | Model identifier (e.g., `yolov8n.pt`) |

**Response (200 OK):**
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

**Response (404 Not Found):**
```json
{
  "detail": "Model not found: unknown-model"
}
```

---

### Get Model Labels

Get class labels for a classification model.

```http
GET /labels?model={model_id}
```

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `model` | string | Yes | Model identifier |

**Response:**
```json
{
  "labels": ["person", "car", "dog", ...],
  "count": 80
}
```

---

### Single Image Inference

Perform inference on a single image.

```http
POST /infer
```

**Content-Type:** `multipart/form-data`

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file` | File | Yes | - | Image file (JPEG, PNG, WEBP) |
| `model` | string | No | `yolov8n.pt` | Model identifier |
| `conf` | float | No | 0.25 | Confidence threshold |
| `iou` | float | No | 0.45 | IoU threshold for NMS |
| `max_det` | int | No | 300 | Maximum detections |

**Response (200 OK):**
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

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid image format"
}
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Model inference failed: {error_message}"
}
```

---

### Image Captioning

Generate automatic description for an image.

```http
POST /caption
```

**Content-Type:** `multipart/form-data`

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file` | File | Yes | - | Image file |
| `model` | string | No | `Salesforce/blip-image-captioning-base` | Caption model |
| `max_length` | int | No | 50 | Max caption length |

**Response:**
```json
{
  "caption": "a person riding a skateboard on a street",
  "inference_time": 120.5,
  "model": "Salesforce/blip-image-captioning-base"
}
```

---

### Visual Question Answering

Answer questions about an image.

```http
POST /vqa
```

**Content-Type:** `multipart/form-data`

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file` | File | Yes | - | Image file |
| `question` | string | Yes | - | Question about the image |
| `model` | string | No | `Salesforce/blip-vqa-base` | VQA model |

**Response:**
```json
{
  "answer": "blue",
  "inference_time": 95.2,
  "model": "Salesforce/blip-vqa-base",
  "question": "What color is the car?"
}
```

---

## 🚦 Error Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Model or resource not found |
| 413 | Payload Too Large | File exceeds size limit |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server processing error |
| 503 | Service Unavailable | Model loading or system unavailable |

---

## 📊 Detection Result Format

### Bounding Box Format

Bboxes are returned as `[x1, y1, x2, y2]` in pixel coordinates:
- `x1`: Left coordinate
- `y1`: Top coordinate
- `x2`: Right coordinate
- `y2`: Bottom coordinate

### Detection Types

| Task | Additional Fields |
|------|-------------------|
| `detect` | `bbox`, `score`, `label` |
| `segment` | `bbox`, `score`, `label`, `polygons` |
| `pose` | `bbox`, `score`, `label`, `keypoints` |

### Segmentation Polygons

```json
{
  "polygons": [
    [[x1, y1], [x2, y2], [x3, y3], ...],
    ...
  ]
}
```

### Pose Keypoints

```json
{
  "keypoints": [
    {"x": 100, "y": 200, "confidence": 0.95},  // nose
    {"x": 95, "y": 210, "confidence": 0.92},   // left eye
    ...
  ]
}
```

Keypoint indices (COCO format):
0. Nose
1. Left eye
2. Right eye
3. Left ear
4. Right ear
5. Left shoulder
6. Right shoulder
7. Left elbow
8. Right elbow
9. Left wrist
10. Right wrist
11. Left hip
12. Right hip
13. Left knee
14. Right knee
15. Left ankle
16. Right ankle

---

## 🔗 Next Steps

- 🔌 **[WebSocket Protocol](./websocket.md)** — Real-time streaming API
- 🏗️ **[Architecture](../architecture/overview.md)** — System design overview
- 📋 **[Models](../reference/models.md)** — Supported model reference

---

<div align="center">

**[⬆ Back to Top](#rest-api-reference)**

</div>
