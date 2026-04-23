## Purpose

Define data structures for model cache, registry, and inference results.

---

### Requirement: Model Cache Structure

The system MUST cache loaded models with optional TTL-based expiration.

```python
ModelCache = dict[str, tuple[Model, Processor | None]]

# Example
{
    "yolov8n.pt": (YOLO_model, None),
    "facebook/detr-resnet-50": (DETR_model, DETR_processor),
}
```

#### Scenario: Cache hit
Given: A model was previously loaded
When: The same model_id is requested within TTL
Then: The cached model is returned without reloading

#### Scenario: Cache miss
Given: A model_id not in cache
When: The model is requested
Then: Model is loaded and added to cache

#### Scenario: Cache expiration
Given: A model cached with TTL of 3600 seconds
When: More than 3600 seconds have passed
Then: Cache entry is invalidated, model reloaded on next request

---

### Requirement: Handler Cache Structure

The system MUST cache handler instances per handler class.

```python
HandlerCache = dict[str, BaseHandler]

# Example
{
    "YOLOHandler": YOLOHandler("cuda:0"),
    "DETRHandler": DETRHandler("cuda:0"),
}
```

#### Scenario: Handler instance reuse
Given: Multiple model requests for the same handler type
When: Handler is needed
Then: Same handler instance is reused

---

### Requirement: Model Registry Schema

The system MUST maintain a single source of truth for model metadata.

```python
ModelMetadata = {
    "category": str,           # Model category identifier
    "name": str,               # Human-readable name
    "description": str,        # Model description
    "speed": str,              # Speed rating
    "accuracy": str,           # Accuracy rating
    "task": str,               # Task type
    "parameters": dict | None  # Optional parameter definitions
}
```

#### Scenario: Look up model metadata
Given: A model_id in MODEL_REGISTRY
When: Metadata is requested
Then: Returns category, name, description, speed, accuracy, task, parameters

#### Scenario: Model parameters
Given: A model with parameters defined
When: Parameters are queried
Then: Returns `{ "conf": {"default": 0.25, "min": 0.0, "max": 1.0}, ... }`

---

### Requirement: Model Category Constants

The system MUST define the following model categories:

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

#### Scenario: Resolve category from model ID
Given: Model ID `yolov8n.pt`
When: Category is looked up in registry
Then: Category is `ModelCategory.YOLO_DETECT`

---

### Requirement: Detection Result Format

The system MUST return detection results in the following format:

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

#### Scenario: Detection result with multiple objects
Given: An image with 3 detected objects
When: Detection result is returned
Then: `detections` array contains 3 items, each with bbox, score, label

---

### Requirement: Segmentation Result Format

The system MUST return segmentation results with polygon data.

```python
SegmentationDetection = {
    "bbox": [float, float, float, float],
    "score": float,
    "label": str,
    "polygons": list[list[list[float]]]  # List of polygon points
}
```

#### Scenario: Segmentation with polygons
Given: A segmentation inference result
When: Result is returned
Then: Each detection includes `polygons` field with point arrays

---

### Requirement: Pose Result Format

The system MUST return pose results with keypoint data.

```python
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

#### Scenario: Pose with 17 keypoints
Given: A pose estimation result
When: Result is returned
Then: Each detection has `keypoints` array with 17 COCO keypoints

---

### Requirement: Caption Result Format

The system MUST return caption results in the following format:

```python
CaptionResult = {
    "caption": str,          # Generated caption
    "inference_time": float, # Inference time in ms
    "model": str             # Model identifier
}
```

#### Scenario: Caption result
Given: A caption inference result
When: Result is returned
Then: Contains `caption` string, `inference_time`, and `model`

---

### Requirement: VQA Result Format

The system MUST return VQA results in the following format:

```python
VQAResult = {
    "answer": str,           # Generated answer
    "question": str,         # Original question
    "inference_time": float, # Inference time in ms
    "model": str             # Model identifier
}
```

#### Scenario: VQA result
Given: A VQA inference result
When: Result is returned
Then: Contains `answer`, `question`, `inference_time`, and `model`

---

### Requirement: COCO Keypoint Indices

For pose estimation, the system MUST use COCO 17-keypoint format:

| Index | Keypoint |
|-------|----------|
| 0 | nose |
| 1 | left_eye |
| 2 | right_eye |
| 3 | left_ear |
| 4 | right_ear |
| 5 | left_shoulder |
| 6 | right_shoulder |
| 7 | left_elbow |
| 8 | right_elbow |
| 9 | left_wrist |
| 10 | right_wrist |
| 11 | left_hip |
| 12 | right_hip |
| 13 | left_knee |
| 14 | right_knee |
| 15 | left_ankle |
| 16 | right_ankle |

#### Scenario: Keypoint ordering
Given: A pose detection result
When: Keypoints array is indexed
Then: Index 0 is nose, index 5 is left_shoulder, index 16 is right_ankle

---

### Requirement: COCO Class Labels (80 Classes)

For YOLO detection models, the system MUST support standard COCO classes:

```
0: person, 1: bicycle, 2: car, 3: motorcycle, ...
```

#### Scenario: Get COCO labels
Given: A YOLO model
When: `/labels` endpoint is called
Then: Returns 80 COCO class labels in order
