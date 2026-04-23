## Purpose

Define the REST API contract for the YOLO-Toys inference platform.

---

### Requirement: Health Check Endpoint

The system MUST provide a `/health` endpoint that returns service status and system information.

#### Scenario: Service is healthy
Given: The FastAPI application is running
When: A GET request is made to `/health`
Then: Response status is 200 with `{ "status": "ok", "version": "...", "device": "...", "default_model": "...", "defaults": {...} }`

---

### Requirement: Model Discovery Endpoints

The system MUST provide endpoints to list and query available models.

#### Scenario: List all models
Given: The ModelManager is initialized
When: A GET request is made to `/models`
Then: Response contains `categories` object with model groups, each containing `name` and `models` array

#### Scenario: Get specific model details
Given: A valid model_id exists in MODEL_REGISTRY
When: A GET request is made to `/models/{model_id}`
Then: Response contains `id`, `category`, `name`, `description`, `task`, and `parameters`

#### Scenario: Model not found
Given: An invalid model_id
When: A GET request is made to `/models/{model_id}`
Then: Response status is 404 with error detail

---

### Requirement: Labels Endpoint

The system MUST provide class labels for models.

#### Scenario: Get labels for default model
Given: The server is running
When: A GET request is made to `/labels`
Then: Response contains `model` identifier and `labels` array

#### Scenario: Get labels for specific model
Given: A valid model_id
When: A GET request is made to `/labels?model={model_id}`
Then: Response contains the specified model's class labels

---

### Requirement: Inference Endpoint

The system MUST provide a `/infer` endpoint for detection, segmentation, and pose tasks.

#### Scenario: Successful object detection
Given: A valid image file and model_id for detection
When: A POST request is made to `/infer` with the image
Then: Response contains `width`, `height`, `task: "detect"`, `detections` array with `bbox`, `score`, `label`, `inference_time`, and `model`

#### Scenario: Successful segmentation
Given: A valid image file and a segmentation model (e.g., yolov8n-seg.pt)
When: A POST request is made to `/infer`
Then: Response contains `task: "segment"` and detections include `polygons` field

#### Scenario: Successful pose estimation
Given: A valid image file and a pose model (e.g., yolov8n-pose.pt)
When: A POST request is made to `/infer`
Then: Response contains `task: "pose"` and detections include `keypoints` with `x`, `y`, `confidence`

#### Scenario: Open-vocabulary detection
Given: A valid image and text_queries parameter
When: A POST request is made to `/infer` with model like `google/owlvit-base-patch32`
Then: Response contains detections matching the text queries

#### Scenario: Invalid image format
Given: An invalid file (not an image)
When: A POST request is made to `/infer`
Then: Response status is 400 with error detail

#### Scenario: Model not found
Given: A valid image but unknown model_id
When: A POST request is made to `/infer`
Then: Response status is 404 with error detail

#### Scenario: File too large
Given: An image exceeding MAX_UPLOAD_MB
When: A POST request is made to `/infer`
Then: Response status is 413 with error detail

---

### Requirement: Caption Endpoint

The system MUST provide a `/caption` endpoint for image captioning.

#### Scenario: Successful caption generation
Given: A valid image file
When: A POST request is made to `/caption`
Then: Response contains `caption` string, `inference_time`, and `model`

#### Scenario: Caption with custom model
Given: A valid image file and model_id
When: A POST request is made to `/caption?model=Salesforce/blip-image-captioning-large`
Then: Response contains caption from the specified model

---

### Requirement: VQA Endpoint

The system MUST provide a `/vqa` endpoint for visual question answering.

#### Scenario: Successful VQA inference
Given: A valid image file and a question
When: A POST request is made to `/vqa` with `question` parameter
Then: Response contains `answer` string, `question`, `inference_time`, and `model`

#### Scenario: VQA without question returns error
Given: A valid image file without a question
When: A POST request is made to `/vqa`
Then: Response status is 422 (validation error)

---

### Requirement: Inference Parameters

The system MUST support the following inference parameters:

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `conf` | float | 0.25 | 0.0-1.0 | Confidence threshold |
| `iou` | float | 0.45 | 0.0-1.0 | IoU threshold for NMS |
| `max_det` | int | 300 | 1-1000 | Maximum detections |
| `device` | string | auto | cpu/cuda/mps | Inference device |
| `imgsz` | int | 640 | 32-4096 | Inference image size |
| `half` | bool | false | - | Enable FP16 half-precision |

#### Scenario: Detection with custom confidence
Given: A valid image and conf=0.8
When: A POST request is made to `/infer`
Then: All detection scores are >= 0.8

---

### Requirement: Detection Result Format

The system MUST return detection results in the following format:

```json
{
  "width": 640,
  "height": 480,
  "task": "detect",
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "score": 0.89,
      "label": "person"
    }
  ],
  "inference_time": 12.5,
  "model": "yolov8n.pt"
}
```

#### Scenario: Bounding box coordinates
Given: A detection is returned
When: The bbox field is examined
Then: Coordinates are `[x1, y1, x2, y2]` in pixel space (top-left origin)
