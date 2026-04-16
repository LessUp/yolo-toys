# Quick Start Guide

Get YOLO-Toys running and perform your first object detection in under 5 minutes.

<p align="center">
  <a href="quickstart.zh-CN.md">简体中文</a> •
  <a href="./">⬅ Back to Getting Started</a>
</p>

---

## 🚀 Start the Server

### Python Native

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS

# Start the server with auto-reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Docker

```bash
docker-compose up -d
```

---

## 🌐 Access the Web Interface

1. Open your browser and navigate to: `http://localhost:8000`

2. **Grant Camera Permission**: When prompted, allow camera access for live detection.

3. **Select a Model**: Choose from the dropdown:
   - `yolov8n.pt` — Fastest, good for testing
   - `yolov8s.pt` — Balanced speed/accuracy
   - `yolov8m.pt` — Higher accuracy, slower

4. **Adjust Settings** (optional):
   - **Confidence**: 0.25 (default) — lower values detect more objects
   - **IoU**: 0.45 — NMS threshold for overlapping boxes
   - **Max Detections**: 300 — maximum objects per frame

5. **Click "Start Detection"** to begin real-time object detection!

---

## 🔌 Using WebSocket Streaming

For the lowest latency real-time detection, use WebSocket streaming:

### JavaScript Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?model=yolov8n.pt&conf=0.25');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('Detections:', result.detections);
  console.log('Inference time:', result.inference_time, 'ms');
};

// Send image frames (JPEG binary)
function sendFrame(imageBlob) {
  ws.send(imageBlob);
}
```

### Updating Configuration

You can update detection parameters without reconnecting:

```javascript
ws.send(JSON.stringify({
  type: 'config',
  conf: 0.5,      // New confidence threshold
  iou: 0.4,       // New IoU threshold
  max_det: 100    // New max detections
}));
```

---

## 📡 REST API Examples

### Single Image Inference

Using cURL:

```bash
curl -X POST "http://localhost:8000/infer" \
  -F "file=@image.jpg" \
  -F "model=yolov8n.pt" \
  -F "conf=0.25" \
  -F "iou=0.45"
```

Using Python (requests):

```python
import requests

url = "http://localhost:8000/infer"
files = {"file": open("image.jpg", "rb")}
data = {"model": "yolov8n.pt", "conf": 0.25}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Detected {len(result['detections'])} objects")
for det in result['detections']:
    print(f"  - {det['label']}: {det['score']:.2f}")
```

### Response Format

```json
{
  "width": 640,
  "height": 480,
  "task": "detect",
  "detections": [
    {
      "bbox": [100.5, 200.3, 150.8, 350.2],
      "score": 0.89,
      "label": "person"
    }
  ],
  "inference_time": 5.2,
  "model": "yolov8n.pt"
}
```

### List Available Models

```bash
curl http://localhost:8000/models
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## 🖼️ Image Captioning (BLIP)

Generate automatic descriptions of images:

```bash
curl -X POST "http://localhost:8000/caption" \
  -F "file=@image.jpg" \
  -F "model=Salesforce/blip-image-captioning-base"
```

Response:
```json
{
  "caption": "a person riding a skateboard on a street",
  "inference_time": 120.5
}
```

---

## ❓ Visual Question Answering (BLIP VQA)

Ask questions about images:

```bash
curl -X POST "http://localhost:8000/vqa" \
  -F "file=@image.jpg" \
  -F "question=What color is the car?" \
  -F "model=Salesforce/blip-vqa-base"
```

---

## ✅ What's Next?

- 📖 **[API Reference](../api/rest-api.md)** — Complete API documentation
- 🏗️ **[Architecture](../architecture/overview.md)** — Understand the system design
- 🐳 **[Deployment](../deployment/docker.md)** — Production deployment guide
- 📋 **[Supported Models](../reference/models.md)** — Model specifications

---

<div align="center">

**[⬆ Back to Top](#quick-start-guide)**

</div>
