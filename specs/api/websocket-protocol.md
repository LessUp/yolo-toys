# WebSocket Protocol Specification

| Version | Author | Updated |
|---------|--------|---------|
| 1.0 | YOLO-Toys Team | 2026-04-17 |

---

## Overview

YOLO-Toys provides a WebSocket endpoint for real-time streaming inference, optimized for video frame processing with minimal latency.

---

## Connection

### Endpoint

```
ws://localhost:8000/ws
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `yolov8n.pt` | Model identifier |
| `conf` | float | `0.25` | Confidence threshold (0.0-1.0) |
| `iou` | float | `0.45` | IoU threshold for NMS (0.0-1.0) |
| `max_det` | int | `300` | Maximum detections (1-1000) |
| `device` | string | `auto` | Inference device (cpu/cuda/mps) |
| `imgsz` | int | `640` | Inference image size (32-4096) |
| `half` | bool | `false` | Enable FP16 half-precision |
| `text_queries` | string | - | Text queries for open-vocabulary models (comma-separated) |

### Connection URL Examples

```
# Basic detection
ws://localhost:8000/ws?model=yolov8n.pt

# Custom parameters
ws://localhost:8000/ws?model=yolov8s.pt&conf=0.5&iou=0.3&max_det=100

# Open-vocabulary detection
ws://localhost:8000/ws?model=google/owlvit-base-patch32&text_queries=cat,dog,person

# Segmentation with FP16
ws://localhost:8000/ws?model=yolov8n-seg.pt&half=true
```

---

## Message Flow

```
┌─────────────┐                           ┌─────────────┐
│   Client    │                           │   Server    │
└──────┬──────┘                           └──────┬──────┘
       │                                         │
       │  ─ ─ ─ ─ WebSocket Connect ─ ─ ─ ─ ─ ▶ │
       │                                         │
       │  ◀ ─ ─ ─ Connection Ack ─ ─ ─ ─ ─ ─ ─ │
       │  {"type": "connected", ...}            │
       │                                         │
       │  ─ ─ ─ ─ Binary JPEG Frame ─ ─ ─ ─ ─ ▶ │
       │                                         │
       │  ◀ ─ ─ ─ JSON Inference Result ─ ─ ─ ─ │
       │  {"detections": [...], ...}            │
       │                                         │
       │  ─ ─ ─ ─ Binary JPEG Frame ─ ─ ─ ─ ─ ▶ │
       │                                         │
       │  ◀ ─ ─ ─ JSON Inference Result ─ ─ ─ ─ │
       │                                         │
       │  ─ ─ ─ ─ Config Update ─ ─ ─ ─ ─ ─ ─ ▶ │
       │  {"type": "config", ...}               │
       │                                         │
       │  ◀ ─ ─ ─ Config Ack ─ ─ ─ ─ ─ ─ ─ ─ ─ │
       │  {"type": "config_updated", ...}       │
       │                                         │
       │  ◀ ─ ─ ─ Binary JPEG Frame ─ ─ ─ ─ ─ ─ │
       │  (continues...)                         │
       ▼                                         ▼
```

---

## Message Types

### Client → Server

#### Binary Frame (Image Data)

- **Format**: Binary JPEG image data
- **Encoding**: JPEG (recommended), PNG, or WEBP
- **Size Limit**: Configured by `MAX_UPLOAD_MB` (default 10MB)

#### Config Update (JSON)

Update inference parameters at runtime.

```json
{
  "type": "config",
  "model": "yolov8s.pt",
  "conf": 0.5,
  "iou": 0.3,
  "max_det": 100,
  "device": "cuda:0",
  "imgsz": 640,
  "half": true,
  "text_queries": ["cat", "dog", "person"]
}
```

### Server → Client

#### Connection Ack

Sent upon successful WebSocket connection.

```json
{
  "type": "connected",
  "model": "yolov8n.pt",
  "device": "cuda:0",
  "config": {
    "conf": 0.25,
    "iou": 0.45,
    "max_det": 300,
    "imgsz": 640,
    "half": false
  }
}
```

#### Inference Result (Detection)

```json
{
  "width": 640,
  "height": 480,
  "task": "detect",
  "detections": [
    {
      "bbox": [100.5, 200.3, 250.8, 450.2],
      "score": 0.89,
      "label": "person"
    }
  ],
  "inference_time": 5.2,
  "model": "yolov8n.pt"
}
```

#### Inference Result (Segmentation)

```json
{
  "width": 640,
  "height": 480,
  "task": "segment",
  "detections": [
    {
      "bbox": [100.5, 200.3, 250.8, 450.2],
      "score": 0.89,
      "label": "person",
      "polygons": [
        [[110, 210], [115, 215], [120, 210], ...]
      ]
    }
  ],
  "inference_time": 10.5,
  "model": "yolov8n-seg.pt"
}
```

#### Inference Result (Pose)

```json
{
  "width": 640,
  "height": 480,
  "task": "pose",
  "detections": [
    {
      "bbox": [100.5, 200.3, 250.8, 450.2],
      "score": 0.89,
      "label": "person",
      "keypoints": [
        {"x": 150, "y": 220, "confidence": 0.95},
        {"x": 145, "y": 215, "confidence": 0.92},
        ...
      ]
    }
  ],
  "inference_time": 8.3,
  "model": "yolov8n-pose.pt"
}
```

#### Config Update Ack

```json
{
  "type": "config_updated",
  "config": {
    "model": "yolov8s.pt",
    "conf": 0.5,
    "iou": 0.3,
    "max_det": 100
  }
}
```

#### Error

```json
{
  "type": "error",
  "message": "Failed to decode image",
  "code": "DECODE_ERROR"
}
```

**Error Codes:**

| Code | Description |
|------|-------------|
| `DECODE_ERROR` | Failed to decode image data |
| `MODEL_NOT_FOUND` | Requested model not available |
| `INFERENCE_ERROR` | Model inference failed |
| `INVALID_CONFIG` | Invalid configuration parameters |
| `OVERLOAD` | Server overloaded, try again later |

---

## Client Implementation Example

### JavaScript

```javascript
class YOLOToysWebSocket {
  constructor(url, options = {}) {
    this.url = url;
    this.options = options;
    this.ws = null;
    this.onResult = options.onResult || (() => {});
    this.onError = options.onError || (() => {});
    this.onConnected = options.onConnected || (() => {});
  }

  connect() {
    const params = new URLSearchParams({
      model: this.options.model || 'yolov8n.pt',
      conf: this.options.conf || 0.25,
      iou: this.options.iou || 0.45,
      max_det: this.options.max_det || 300,
    });

    this.ws = new WebSocket(`${this.url}?${params}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        const data = JSON.parse(event.data);
        if (data.type === 'connected') {
          this.onConnected(data);
        } else if (data.type === 'error') {
          this.onError(data);
        } else if (data.type === 'config_updated') {
          console.log('Config updated:', data.config);
        } else {
          this.onResult(data);
        }
      }
    };

    this.ws.onerror = (error) => {
      this.onError({ type: 'error', message: 'WebSocket error' });
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
    };
  }

  sendFrame(imageBlob) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(imageBlob);
    }
  }

  updateConfig(config) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'config',
        ...config
      }));
    }
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const client = new YOLOToysWebSocket('ws://localhost:8000/ws', {
  model: 'yolov8n.pt',
  conf: 0.5,
  onResult: (result) => {
    console.log('Detections:', result.detections);
  },
  onError: (error) => {
    console.error('Error:', error);
  },
  onConnected: (data) => {
    console.log('Connected with config:', data.config);
  }
});

client.connect();

// Send frames from camera
async function sendCameraFrames() {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  const video = document.createElement('video');
  video.srcObject = stream;
  await video.play();

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  function sendFrame() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      client.sendFrame(blob);
    }, 'image/jpeg', 0.8);
    requestAnimationFrame(sendFrame);
  }

  sendFrame();
}
```

### Python

```python
import asyncio
import websockets
import cv2
import json

async def websocket_client():
    uri = "ws://localhost:8000/ws?model=yolov8n.pt&conf=0.25"

    async with websockets.connect(uri) as ws:
        # Receive connection ack
        ack = await ws.recv()
        print(f"Connected: {ack}")

        # Open camera
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            jpeg_data = buffer.tobytes()

            # Send binary frame
            await ws.send(jpeg_data)

            # Receive result
            result = await ws.recv()
            data = json.loads(result)
            print(f"Inference time: {data['inference_time']:.1f}ms, Detections: {len(data['detections'])}")

asyncio.run(websocket_client())
```

---

## Performance Considerations

### Frame Rate

- Maximum sustainable frame rate depends on:
  - Model size (YOLOv8n > YOLOv8s > YOLOv8m)
  - Device (GPU > CPU)
  - Image resolution
  - Network latency

### Recommended Settings

| Use Case | Model | Resolution | Expected FPS (GPU) |
|----------|-------|------------|-------------------|
| Real-time (fast) | yolov8n.pt | 640x480 | 30-60 |
| Real-time (balanced) | yolov8s.pt | 640x480 | 15-30 |
| High accuracy | yolov8m.pt | 640x480 | 10-15 |
| Segmentation | yolov8n-seg.pt | 640x480 | 15-25 |
| Pose estimation | yolov8n-pose.pt | 640x480 | 20-30 |

### Optimization Tips

1. **Use smaller models** for higher FPS
2. **Enable FP16** (`half=true`) on CUDA devices
3. **Reduce image size** for faster processing
4. **Adjust confidence threshold** to filter detections early
5. **Use dedicated GPU** instead of CPU

---

## Changelog

| Date | Change |
|------|--------|
| 2025-02-13 | Initial WebSocket implementation |
| 2025-11-25 | Added runtime config update |
| 2026-02-13 | Added FP16 support |
| 2026-04-17 | Formalized specification |
