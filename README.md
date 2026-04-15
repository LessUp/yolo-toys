<div align="center">

<!-- PROJECT LOGO/BANNER -->
<h1 align="center">🎯 YOLO-Toys</h1>
<h3 align="center">Multi-Model Real-Time Vision Recognition Platform</h3>

<p align="center">
  <strong>FastAPI + YOLOv8 + Transformers</strong> — Real-time object detection, segmentation, pose estimation & multimodal AI via WebSocket streaming
</p>

<p align="center">
  <a href="https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml">
    <img src="https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/LessUp/yolo-toys/actions/workflows/pages.yml">
    <img src="https://github.com/LessUp/yolo-toys/actions/workflows/pages.yml/badge.svg" alt="Pages">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  </a>
  <br>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.111%2B-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PyTorch-%23EE4C2C?logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> •
  <a href="https://lessup.github.io/yolo-toys/">🌐 Live Demo</a> •
  <a href="docs/README.md">📚 Documentation</a> •
  <a href="CONTRIBUTING.md">🤝 Contributing</a>
</p>

</div>

---

## 🚀 Features

<div align="center">

| 🎯 **Detection** | 🖼️ **Segmentation** | 🏃 **Pose Estimation** |
|:---:|:---:|:---:|
| Real-time object detection (80 COCO classes) | Instance segmentation with pixel masks | Human 17-keypoint detection |
| YOLOv8 n/s/m/l/x | YOLOv8 n/s/m-seg | YOLOv8 n/s/m-pose |

| 🔄 **Transformers** | 🔍 **Open Vocabulary** | 📝 **Multimodal** |
|:---:|:---:|:---:|
| DETR ResNet-50/101 | OWL-ViT base-patch32 | BLIP Image Captioning |
| End-to-end detection | Zero-shot detection | Visual Question Answering |

</div>

### Frontend Capabilities

- 📷 **Camera capture** with canvas overlay rendering
- 🎛️ **Model category tabs** with configurable parameters
- ⚙️ **Dynamic settings**: confidence, IoU, max detections, device selection
- 🎨 **Display toggles**: bounding boxes, labels, masks, keypoints, skeleton
- 🌓 **Dark/light theme** with auto settings persistence

### Backend Highlights

- ⚡ **FastAPI** with REST + WebSocket endpoints
- 💾 **Model caching** with auto device selection & FP16 acceleration
- 🔀 **Async concurrency control** via `asyncio.Semaphore`
- 🧩 **Strategy pattern** handlers for different model types
- 🔧 **Pydantic Settings** for unified environment configuration

---

## ⚡ Performance Benchmarks

> Latency measured in milliseconds per frame (lower is better)

| Model | Task | CPU (i7-12700) | RTX 3060 | Apple M1 |
|-------|------|----------------|----------|----------|
| YOLOv8n | Detection | ~25ms | ~5ms | ~8ms |
| YOLOv8s | Detection | ~35ms | ~6ms | ~12ms |
| YOLOv8n-seg | Segmentation | ~45ms | ~10ms | ~15ms |
| DETR-R50 | Detection | ~120ms | ~25ms | ~40ms |
| OWL-ViT | Zero-shot | ~150ms | ~30ms | ~50ms |

*Note: Performance varies based on input resolution and batch size. WebSocket streaming optimized for 640x480 input.*

---

## 📋 Requirements

### Minimum Requirements
- **Python**: 3.11+
- **RAM**: 4GB (8GB+ recommended for large models)
- **Storage**: 2GB free space

### GPU Support (Optional)
- **NVIDIA**: CUDA 11.8+ with cuDNN
- **Apple Silicon**: MPS backend supported
- **CPU**: Always supported, slower inference

### Browser Compatibility
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Camera access permission required for live demo

---

## 🚀 Quick Start

### Option 1: Python Native (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys

# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate
# Activate (Windows PowerShell)
# .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000` — grant camera permission and start detecting!

### Option 2: Docker

```bash
# Build and run
cp .env.example .env
docker build -t yolo-toys .
docker run -p 8000:8000 --env-file .env yolo-toys
```

### Option 3: Docker Compose (Recommended for Production)

```bash
cp .env.example .env
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📡 API Reference

<details>
<summary><b>🔍 REST Endpoints</b></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check & system info |
| `GET` | `/models` | List available models |
| `GET` | `/labels` | Get class labels for model |
| `POST` | `/infer` | Single image inference |
| `POST` | `/caption` | Image captioning |
| `POST` | `/vqa` | Visual question answering |

</details>

<details>
<summary><b>🔌 WebSocket Streaming</b></summary>

```javascript
const ws = new WebSocket(
  'ws://localhost:8000/ws'
  + '?model=yolov8n.pt'
  + '&conf=0.25'
  + '&iou=0.45'
  + '&max_det=300'
);

// Send binary JPEG frames
ws.send(imageBlob);

// Receive JSON results
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  // result.detections: [...]
  // result.inference_time: number
};
```

</details>

<details>
<summary><b>📤 Example: Single Image Inference</b></summary>

```bash
curl -X POST "http://localhost:8000/infer" \
  -F "file=@image.jpg" \
  -F "model=yolov8n.pt" \
  -F "conf=0.25" \
  -F "iou=0.45"
```

**Response:**
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

</details>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Camera  │  │  Canvas  │  │  WebSocket│  │  HTTP    │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
        ┌────────────┐              ┌────────────┐
        │   REST     │              │ WebSocket  │
        └─────┬──────┘              └─────┬──────┘
              │                           │
              └─────────────┬─────────────┘
                            ▼
              ┌───────────────────────────┐
              │      ModelManager         │
              │   (Cache + Routing)       │
              └─────────────┬─────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │   YOLO     │   │Transformers│   │    BLIP    │
   │  Handler   │   │  Handler   │   │  Handler   │
   └────────────┘   └────────────┘   └────────────┘
```

**Key Design Patterns:**
- **Strategy Pattern**: Separate handlers for YOLO / DETR / OWL-ViT / Grounding DINO / BLIP
- **Pydantic Settings**: Unified configuration from environment variables
- **Modern FastAPI Lifespan**: Lifecycle management replacing deprecated `on_event`
- **Route Extraction**: Separation of concerns with dedicated `routes.py`
- **Structured Logging**: Production-ready logging instead of print statements

---

## 📁 Project Structure

```
yolo-toys/
├── app/                      # Backend application
│   ├── handlers/             # Strategy pattern handlers
│   │   ├── base.py           # BaseHandler abstract class
│   │   ├── registry.py       # Model registry & factory
│   │   ├── yolo_handler.py   # YOLO detection/segment/pose
│   │   ├── hf_handler.py     # DETR/OWL-ViT/Grounding DINO
│   │   └── blip_handler.py   # BLIP Caption/VQA
│   ├── main.py               # FastAPI entry with lifespan
│   ├── config.py             # Pydantic Settings
│   ├── routes.py             # API routes (REST + WebSocket)
│   ├── model_manager.py      # Model cache + handler delegation
│   └── schemas.py            # Pydantic response models
├── frontend/                 # Static frontend
│   ├── js/                   # Frontend modules
│   ├── index.html            # UI interface
│   ├── style.css             # Dark/light themes
│   └── app.js                # Main application logic
├── tests/                    # API + WebSocket + unit tests
├── docs/                     # Detailed documentation
├── changelog/                # Version history
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Multi-stage build
├── pyproject.toml            # Project metadata + Ruff config
├── Makefile                  # Development commands
└── requirements.txt          # Python dependencies
```

---

## 🛠️ Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt
pre-commit install

# Run linting
make lint

# Run tests
make test

# Start development server
make run
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `yolov8n.pt` | Default model name |
| `CONF_THRESHOLD` | `0.25` | Detection confidence threshold |
| `IOU_THRESHOLD` | `0.45` | NMS IoU threshold |
| `MAX_DET` | `300` | Maximum detections per frame |
| `DEVICE` | `auto` | Inference device (cpu/cuda/mps) |
| `SKIP_WARMUP` | `false` | Skip model warmup on startup |
| `MAX_CONCURRENCY` | `4` | Max concurrent inference requests |

---

## 📚 Documentation

- **[📖 Detailed Docs](docs/README.md)** — Architecture, data flow, implementation details
- **[🌐 Project Page](https://lessup.github.io/yolo-toys/)** — Online documentation & demo
- **[📝 Changelog](changelog/)** — Version history & migration guides
- **[🤝 Contributing](CONTRIBUTING.md)** — Development guidelines & PR workflow

---

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

**Quick start for contributors:**

```bash
# Fork and clone
git clone https://github.com/your-username/yolo-toys.git

# Create branch
git checkout -b feat/your-feature

# Make changes, commit, push
git commit -m "feat: add new feature"
git push origin feat/your-feature

# Open Pull Request
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **[Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)** — State-of-the-art object detection
- **[HuggingFace Transformers](https://github.com/huggingface/transformers)** — Open-source ML models
- **[FastAPI](https://fastapi.tiangolo.com/)** — Modern, fast web framework
- **[OpenCV](https://opencv.org/)** — Computer vision library

---

<div align="center">

If you find this project helpful, please give us a ⭐!

[**🌐 Visit Live Demo**](https://lessup.github.io/yolo-toys/) • [**🐛 Report Bug**](https://github.com/LessUp/yolo-toys/issues) • [**💡 Request Feature**](https://github.com/LessUp/yolo-toys/issues)

</div>
