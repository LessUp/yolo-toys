# WebSocket Protocol

Real-time streaming protocol for low-latency object detection.

<p align="center">
  <a href="websocket.zh-CN.md">简体中文</a> •
  <a href="./">⬅ Back to API Reference</a>
</p>

---

## 📋 Overview

WebSocket connections provide the lowest latency for real-time video analysis. Binary image frames are sent to the server, and JSON detection results are returned.

**Endpoint:** `ws://localhost:8000/ws`

---

## 🔌 Connection

### URL Format

```
ws://{host}/ws?model={model_id}&conf={confidence}&iou={iou}&max_det={max_detections}
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | `yolov8n.pt` | Model identifier |
| `conf` | float | 0.25 | Confidence threshold (0.0 - 1.0) |
| `iou` | float | 0.45 | IoU threshold for NMS |
| `max_det` | int | 300 | Maximum detections per frame |
| `device` | string | auto | Inference device (cpu/cuda/mps) |
| `imgsz` | int | 640 | Inference image size |
| `half` | bool | false | Enable FP16 half-precision |
| `text_queries` | string | - | Text queries for open-vocabulary detection (comma-separated) |
| `question` | string | - | Question for VQA models |

### Example Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?model=yolov8n.pt&conf=0.25');
```

---

## 📤 Client → Server Messages

### Binary Image Frame

Send JPEG-encoded image as binary message:

```javascript
// Capture from canvas
canvas.toBlob((blob) => {
  ws.send(blob);
}, 'image/jpeg', 0.85);
```

**Requirements:**
- Format: JPEG
- Resolution: Any (640x480 recommended for balance)
- Quality: 0.85 recommended
- Max size: 10MB

### Configuration Update

Update detection parameters without reconnecting:

```javascript
ws.send(JSON.stringify({
  type: 'config',
  conf: 0.5,
  iou: 0.4,
  max_det: 100,
  model: 'yolov8s.pt'  // Optional: switch model
}));
```

**Config Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Must be `"config"` |
| `conf` | float | New confidence threshold (0.0-1.0) |
| `iou` | float | New IoU threshold (0.0-1.0) |
| `max_det` | int | New max detections limit |
| `model` | string | (Optional) Switch to different model |
| `device` | string | (Optional) Change inference device |
| `imgsz` | int | (Optional) Change inference image size |
| `half` | bool | (Optional) Enable/disable FP16 |
| `text_queries` | string/array | (Optional) Text queries for open-vocabulary detection |
| `question` | string | (Optional) Question for VQA models |

---

## 📥 Server → Client Messages

### Ready Message

Sent immediately after WebSocket connection is established:

```json
{
  "type": "ready",
  "message": "connected",
  "model": "yolov8n.pt",
  "device": "cuda:0"
}
```

### Detection Result

```json
{
  "type": "result",
  "data": {
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
    "inference_time": 12.5,
    "model": "yolov8n.pt",
    "timestamp": "2026-04-16T10:30:00.000Z"
  }
}
```

### Error Message

```json
{
  "type": "error",
  "detail": "Model inference failed"
}
```

**Common Error Messages:**
| Detail | Description |
|--------|-------------|
| `file too large` | Image exceeds MAX_UPLOAD_MB limit |
| `failed to decode image` | Invalid image format or corrupted data |
| `Unknown model category for ...` | Model ID not recognized |

### Config Acknowledgment

```json
{
  "type": "config_updated",
  "model": "yolov8s.pt"
}
```

---

## 💻 Complete Example

### JavaScript Client

```javascript
class DetectionStream {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.setupHandlers();
    this.frameCount = 0;
    this.lastFpsTime = performance.now();
  }

  setupHandlers() {
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.onConnect?.();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.onError?.(error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.onDisconnect?.();
      // Auto-reconnect after 3 seconds
      setTimeout(() => this.reconnect(), 3000);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'ready':
        console.log('Connected, model:', message.model, 'device:', message.device);
        break;
      case 'result':
        this.onDetection?.(message.data);
        this.updateFps();
        break;
      case 'error':
        console.error('Server error:', message.detail);
        break;
      case 'config_updated':
        console.log('Config updated, model:', message.model);
        break;
    }
  }

  sendFrame(imageBlob) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(imageBlob);
    }
  }

  updateConfig(config) {
    this.ws.send(JSON.stringify({
      type: 'config',
      ...config
    }));
  }

  updateFps() {
    this.frameCount++;
    const now = performance.now();
    if (now - this.lastFpsTime >= 1000) {
      const fps = this.frameCount;
      this.frameCount = 0;
      this.lastFpsTime = now;
      this.onFpsUpdate?.(fps);
    }
  }

  reconnect() {
    console.log('Reconnecting...');
    this.ws = new WebSocket(this.ws.url);
    this.setupHandlers();
  }

  close() {
    this.ws.close();
  }
}

// Usage
const stream = new DetectionStream('ws://localhost:8000/ws?model=yolov8n.pt');

stream.onConnect = () => {
  console.log('Connected to detection server');
};

stream.onDetection = (data) => {
  console.log(`Detected ${data.detections.length} objects in ${data.inference_time}ms`);
  // Render detections on canvas...
};

stream.onFpsUpdate = (fps) => {
  document.getElementById('fps').textContent = `${fps} FPS`;
};

// Send frames from video element
function sendVideoFrame() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0);

  canvas.toBlob((blob) => {
    stream.sendFrame(blob);
  }, 'image/jpeg', 0.85);

  requestAnimationFrame(sendVideoFrame);
}
```

---

## ⚡ Performance Tips

### 1. Optimize Image Size

```javascript
// Resize before sending for better performance
const MAX_WIDTH = 640;
const scale = Math.min(1, MAX_WIDTH / video.videoWidth);
const width = video.videoWidth * scale;
const height = video.videoHeight * scale;
```

### 2. Reduce JPEG Quality

```javascript
// Lower quality = smaller payload = faster transfer
canvas.toBlob((blob) => {
  stream.sendFrame(blob);
}, 'image/jpeg', 0.7);  // Try 0.7 for faster streaming
```

### 3. Frame Skipping

```javascript
// Skip frames to maintain target FPS
const TARGET_FPS = 15;
const SKIP_EVERY = Math.round(30 / TARGET_FPS);  // For 30fps camera

let frameCounter = 0;
function onVideoFrame() {
  frameCounter++;
  if (frameCounter % SKIP_EVERY !== 0) return;
  // Send frame...
}
```

### 4. Connection Pooling

For multiple cameras, create separate WebSocket connections:

```javascript
const streams = cameras.map(cam =>
  new DetectionStream(`ws://localhost:8000/ws?model=${cam.model}`)
);
```

---

## 🔒 Security Considerations

### CORS

Configure allowed origins in environment:

```bash
ALLOW_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Rate Limiting

Maximum concurrent connections controlled by `MAX_CONCURRENCY`:

```bash
MAX_CONCURRENCY=4  # Default
```

### Authentication (Future)

Token-based authentication will be supported:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN');
```

---

## 🔗 Related Documentation

- 🔍 **[REST API](./rest-api.md)** — HTTP endpoints reference
- 🏗️ **[Architecture](../architecture/overview.md)** — System design
- 📋 **[Models](../reference/models.md)** — Supported model list

---

<div align="center">

**[⬆ Back to Top](#websocket-protocol)**

</div>
