## Purpose

Define the WebSocket protocol for real-time streaming inference.

---

### Requirement: WebSocket Connection

The system MUST accept WebSocket connections at `/ws` with optional query parameters.

#### Scenario: Connect with default parameters
Given: The server is running
When: A WebSocket connection is opened to `/ws`
Then: Server sends `{ "type": "connected", "model": "...", "device": "...", "config": {...} }`

#### Scenario: Connect with model parameter
Given: The server is running
When: A WebSocket connection is opened to `/ws?model=yolov8s.pt`
Then: Server acknowledges with the specified model loaded

---

### Requirement: Query Parameters

The system MUST support the following query parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | yolov8n.pt | Model identifier |
| `conf` | float | 0.25 | Confidence threshold |
| `iou` | float | 0.45 | IoU threshold for NMS |
| `max_det` | int | 300 | Maximum detections |
| `device` | string | auto | Inference device |
| `imgsz` | int | 640 | Inference image size |
| `half` | bool | false | Enable FP16 |
| `text_queries` | string | - | Text queries for open-vocabulary models |

#### Scenario: Custom connection parameters
Given: The server is running
When: A WebSocket connection is opened to `/ws?model=yolov8s.pt&conf=0.5&iou=0.3`
Then: Server acknowledges with the specified configuration

---

### Requirement: Binary Frame Processing

The system MUST process binary frames as JPEG/PNG/WEBP images.

#### Scenario: Send JPEG for inference
Given: A WebSocket connection is established
When: A binary frame containing a JPEG image is sent
Then: Server processes the image and sends `{ "width", "height", "task", "detections", "inference_time", "model" }`

#### Scenario: Image size limit
Given: A binary frame exceeds MAX_UPLOAD_MB
When: The frame is received
Then: Server sends `{ "type": "error", "message": "...", "code": "DECODE_ERROR" }`

---

### Requirement: Config Update Messages

The system MUST support runtime configuration updates via JSON messages.

#### Scenario: Update model at runtime
Given: A WebSocket connection is established
When: A JSON message `{ "type": "config", "model": "yolov8s.pt" }` is sent
Then: Server sends `{ "type": "config_updated", "config": {...} }`

#### Scenario: Update confidence threshold
Given: A WebSocket connection is established
When: A JSON message `{ "type": "config", "conf": 0.5 }` is sent
Then: Subsequent inferences use the new confidence threshold

---

### Requirement: Server Message Types

The system MUST send the following message types:

| Type | Direction | Description |
|------|-----------|-------------|
| `connected` | Server → Client | Connection acknowledgment |
| `result` | Server → Client | Inference result |
| `config_updated` | Server → Client | Config update acknowledgment |
| `error` | Server → Client | Error notification |

#### Scenario: Connection acknowledgment
Given: WebSocket connects successfully
When: The connection is established
Then: Server sends `{ "type": "connected", "model": "...", "device": "...", "config": {...} }`

#### Scenario: Error on invalid model
Given: A WebSocket connection with invalid model
When: The server fails to load the model
Then: Server sends `{ "type": "error", "message": "...", "code": "MODEL_NOT_FOUND" }`

---

### Requirement: Error Codes

The system MUST use the following error codes:

| Code | Description |
|------|-------------|
| `DECODE_ERROR` | Failed to decode image data |
| `MODEL_NOT_FOUND` | Requested model not available |
| `INFERENCE_ERROR` | Model inference failed |
| `INVALID_CONFIG` | Invalid configuration parameters |
| `OVERLOAD` | Server overloaded |

#### Scenario: Inference failure
Given: A model fails during inference
When: An error occurs
Then: Server sends `{ "type": "error", "message": "...", "code": "INFERENCE_ERROR" }`

---

### Requirement: Streaming Performance

The system SHOULD support real-time streaming at various frame rates.

#### Scenario: Real-time detection with YOLOv8n
Given: GPU device and yolov8n.pt model
When: 640x480 frames are streamed
Then: System achieves 30-60 FPS

#### Scenario: Segmentation streaming
Given: GPU device and yolov8n-seg.pt model
When: 640x480 frames are streamed
Then: System achieves 15-25 FPS

#### Scenario: FP16 optimization
Given: CUDA device with half=true
When: Streaming inference
Then: Performance improves by 20-50% compared to FP32
