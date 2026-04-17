# Database Schema Specification

| Version | Author | Updated |
|---------|--------|---------|
| 1.0 | YOLO-Toys Team | 2026-04-17 |

---

## Overview

YOLO-Toys is primarily an inference service and does not require a persistent database for core functionality. However, this document defines the data models used for in-memory caching and potential future persistence requirements.

---

## Current Architecture

### In-Memory Model Cache

Models are cached in memory using Python dictionaries:

```python
# Model cache structure
ModelCache = dict[str, tuple[Model, Processor | None]]

# Example
{
    "yolov8n.pt": (YOLO_model, None),
    "facebook/detr-resnet-50": (DETR_model, DETR_processor),
    "Salesforce/blip-image-captioning-base": (BLIP_model, BLIP_processor)
}
```

### Handler Cache

Handler instances are cached per handler class:

```python
# Handler cache structure
HandlerCache = dict[str, BaseHandler]

# Example
{
    "YOLOHandler": YOLOHandler("cuda:0"),
    "DETRHandler": DETRHandler("cuda:0"),
    "BLIPCaptionHandler": BLIPCaptionHandler("cuda:0")
}
```

---

## Model Registry Schema

The `MODEL_REGISTRY` is the single source of truth for model metadata.

### Schema Definition

```python
ModelMetadata = {
    "category": str,           # Model category identifier
    "name": str,               # Human-readable name
    "description": str,        # Model description
    "speed": str,              # Speed rating: "极快", "快", "中等", "较慢", "慢"
    "accuracy": str,           # Accuracy rating: "中等", "较好", "高", "很高", "最高"
    "task": str,               # Task type: "detect", "segment", "pose", "caption", "vqa"
    "parameters": dict | None  # Optional parameter definitions
}
```

### Model Category Constants

```python
class ModelCategory:
    YOLO_DETECT = "yolo_detect"
    YOLO_SEGMENT = "yolo_segment"
    YOLO_POSE = "yolo_pose"
    HF_DETR = "hf_detr"
    HF_OWLVIT = "hf_owlvit"
    HF_GROUNDING_DINO = "hf_grounding_dino"
    MULTIMODAL_CAPTION = "multimodal_caption"
    MULTIMODAL_VQA = "multimodal_vqa"
```

### Example Registry Entry

```python
MODEL_REGISTRY = {
    "yolov8n.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Nano",
        "description": "超轻量检测模型，适合实时场景，速度最快",
        "speed": "极快",
        "accuracy": "中等",
        "task": "detect",
        "parameters": {
            "conf": {"default": 0.25, "min": 0.0, "max": 1.0},
            "iou": {"default": 0.45, "min": 0.0, "max": 1.0},
            "max_det": {"default": 300, "min": 1, "max": 1000}
        }
    }
}
```

---

## Inference Result Schema

### Detection Result

```python
DetectionResult = {
    "width": int,              # Image width in pixels
    "height": int,             # Image height in pixels
    "task": "detect",          # Task type
    "detections": [Detection], # List of detections
    "inference_time": float,   # Inference time in ms
    "model": str               # Model identifier
}

Detection = {
    "bbox": [float, float, float, float],  # [x1, y1, x2, y2]
    "score": float,            # Confidence score 0.0-1.0
    "label": str               # Class label
}
```

### Segmentation Result

```python
SegmentationResult = {
    "width": int,
    "height": int,
    "task": "segment",
    "detections": [SegmentationDetection],
    "inference_time": float,
    "model": str
}

SegmentationDetection = {
    "bbox": [float, float, float, float],
    "score": float,
    "label": str,
    "polygons": list[list[list[float]]]  # List of polygon points
}
```

### Pose Result

```python
PoseResult = {
    "width": int,
    "height": int,
    "task": "pose",
    "detections": [PoseDetection],
    "inference_time": float,
    "model": str
}

PoseDetection = {
    "bbox": [float, float, float, float],
    "score": float,
    "label": str,
    "keypoints": [Keypoint]
}

Keypoint = {
    "x": float,           # X coordinate
    "y": float,           # Y coordinate
    "confidence": float   # Keypoint confidence 0.0-1.0
}
```

### Caption Result

```python
CaptionResult = {
    "caption": str,          # Generated caption
    "inference_time": float, # Inference time in ms
    "model": str             # Model identifier
}
```

### VQA Result

```python
VQAResult = {
    "answer": str,           # Generated answer
    "question": str,         # Original question
    "inference_time": float, # Inference time in ms
    "model": str             # Model identifier
}
```

---

## COCO Keypoint Indices

For pose estimation models, keypoints follow the COCO format:

| Index | Keypoint | Description |
|-------|----------|-------------|
| 0 | nose | Nose tip |
| 1 | left_eye | Left eye center |
| 2 | right_eye | Right eye center |
| 3 | left_ear | Left ear |
| 4 | right_ear | Right ear |
| 5 | left_shoulder | Left shoulder |
| 6 | right_shoulder | Right shoulder |
| 7 | left_elbow | Left elbow |
| 8 | right_elbow | Right elbow |
| 9 | left_wrist | Left wrist |
| 10 | right_wrist | Right wrist |
| 11 | left_hip | Left hip |
| 12 | right_hip | Right hip |
| 13 | left_knee | Left knee |
| 14 | right_knee | Right knee |
| 15 | left_ankle | Left ankle |
| 16 | right_ankle | Right ankle |

### Skeleton Connections

```
(0, 1), (0, 2),      # Nose to eyes
(1, 3), (2, 4),      # Eyes to ears
(5, 7), (7, 9),      # Left arm
(6, 8), (8, 10),     # Right arm
(5, 6),              # Shoulders
(5, 11), (6, 12),    # Shoulders to hips
(11, 13), (13, 15),  # Left leg
(12, 14), (14, 16)   # Right leg
```

---

## COCO Class Labels (80 Classes)

For YOLO detection models:

```
0: person
1: bicycle
2: car
3: motorcycle
4: airplane
5: bus
6: train
7: truck
8: boat
9: traffic light
10: fire hydrant
11: stop sign
12: parking meter
13: bench
14: bird
15: cat
16: dog
17: horse
18: sheep
19: cow
20: elephant
21: bear
22: zebra
23: giraffe
24: backpack
25: umbrella
26: handbag
27: tie
28: suitcase
29: frisbee
30: skis
31: snowboard
32: sports ball
33: kite
34: baseball bat
35: baseball glove
36: skateboard
37: surfboard
38: tennis racket
39: bottle
40: wine glass
41: cup
42: fork
43: knife
44: spoon
45: bowl
46: banana
47: apple
48: sandwich
49: orange
50: broccoli
51: carrot
52: hot dog
53: pizza
54: donut
55: cake
56: chair
57: couch
58: potted plant
59: bed
60: dining table
61: toilet
62: tv
63: laptop
64: mouse
65: remote
66: keyboard
67: cell phone
68: microwave
69: oven
70: toaster
71: sink
72: refrigerator
73: book
74: clock
75: vase
76: scissors
77: teddy bear
78: hair drier
79: toothbrush
```

---

## Future Persistence Considerations

### Potential Use Cases

1. **Inference History** — Store historical inference results for analytics
2. **User Sessions** — Track user sessions and preferences
3. **Model Analytics** — Track model usage and performance metrics
4. **Custom Models** — Store user-uploaded custom model metadata

### Proposed Schema (Future)

```yaml
# For future database implementation

tables:
  inference_history:
    columns:
      id: UUID PRIMARY KEY
      model_id: VARCHAR(255) NOT NULL
      task: VARCHAR(50) NOT NULL
      image_hash: VARCHAR(64)
      detections_count: INTEGER
      inference_time_ms: FLOAT
      created_at: TIMESTAMP

  model_usage_stats:
    columns:
      model_id: VARCHAR(255) PRIMARY KEY
      request_count: BIGINT
      avg_inference_time: FLOAT
      last_used: TIMESTAMP

  user_sessions:
    columns:
      session_id: UUID PRIMARY KEY
      created_at: TIMESTAMP
      last_activity: TIMESTAMP
      settings: JSONB
```

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-17 | Initial schema specification |
