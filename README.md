# YOLO-Toys — Multi-Model Real-Time Vision Recognition

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

English | [简体中文](README.zh-CN.md)

Real-time video object recognition platform supporting YOLO, HuggingFace Transformers, and multimodal models via WebSocket streaming.

## Features

### Supported Models

| Category | Model | Description |
|----------|-------|-------------|
| **YOLO Detection** | YOLOv8 n/s/m/l/x | Real-time object detection |
| **YOLO Segmentation** | YOLOv8 n/s/m-seg | Instance segmentation |
| **YOLO Pose** | YOLOv8 n/s/m-pose | Human keypoint detection |
| **DETR** | facebook/detr-resnet-50/101 | Transformer detector |
| **OWL-ViT** | google/owlvit-base-patch32 | Open-vocabulary detection |
| **BLIP Caption** | Salesforce/blip-image-captioning | Image captioning |
| **BLIP VQA** | Salesforce/blip-vqa | Visual question answering |

### Frontend
- Camera capture, canvas overlay rendering
- Model category tabs, configurable server/framerate/quality
- Dynamic parameters: confidence, IoU, max detections, device
- Display toggles: bounding boxes, labels, masks, keypoints, skeleton
- Dark/light theme, settings auto-persistence

### Backend
- FastAPI REST + WebSocket endpoints
- `/infer` — Unified inference, `/models` — Available models, `/health` — Health check
- `/caption` — Image captioning, `/vqa` — Visual QA
- Model caching, auto device selection, FP16 acceleration

## Quick Start

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Visit http://localhost:8000
```

### Docker

```bash
cp .env.example .env
docker compose up --build -d
```

### Makefile

```bash
make install    # Install dependencies
make dev        # Install dev deps + pre-commit
make lint       # Code check (ruff)
make test       # Run tests
make run        # Start uvicorn --reload
```

## Architecture (v3.0)

- **Strategy Pattern** — Separate handlers (YOLO / DETR / OWL-ViT / BLIP)
- **Pydantic Settings** — Unified config management
- **Modern FastAPI Lifespan** — Replaces deprecated `on_event`
- **Route Extraction** — `main.py` split into `routes.py`
- **Structured Logging** — `logging` replaces `print`

## Project Structure

```
YOLO-Toys/
├─ app/
│  ├─ main.py             # FastAPI entry + lifespan
│  ├─ config.py           # Pydantic Settings
│  ├─ routes.py           # API routes (REST + WebSocket)
│  ├─ model_manager.py    # Model manager (delegates to handlers)
│  └─ handlers/           # Strategy pattern handlers
├─ frontend/
│  ├─ index.html          # UI
│  ├─ app.js              # Frontend entry (ES Module)
│  └─ js/                 # Frontend modules (api, camera, draw)
├─ tests/                 # API + WebSocket + unit tests
└─ docs/                  # Detailed teaching docs
```

## License

MIT License
