# YOLO-Toys — Multi-Model Real-Time Vision Recognition

[![CI](https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml/badge.svg)](https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml)
[![Pages](https://github.com/LessUp/yolo-toys/actions/workflows/pages.yml/badge.svg)](https://lessup.github.io/yolo-toys/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

English | [简体中文](README.zh-CN.md) | [Project Page](https://lessup.github.io/yolo-toys/)

Real-time video object recognition platform supporting YOLO, HuggingFace Transformers, and multimodal models via WebSocket streaming.

## Features

### Supported Models

| Category | Model | Description |
|----------|-------|-------------|
| **YOLO Detection** | YOLOv8 n/s/m/l/x | Real-time object detection (80 COCO classes) |
| **YOLO Segmentation** | YOLOv8 n/s/m-seg | Instance segmentation with pixel masks |
| **YOLO Pose** | YOLOv8 n/s/m-pose | Human 17-keypoint detection |
| **DETR** | facebook/detr-resnet-50/101 | End-to-end Transformer detector |
| **OWL-ViT** | google/owlvit-base-patch32 | Zero-shot open-vocabulary detection |
| **Grounding DINO** | IDEA-Research/grounding-dino-tiny | Open-set detection with text prompts |
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
- Async concurrency control via `asyncio.Semaphore`

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

Note: the current Docker build copies the bundled `yolov8*.pt` weights from the repository into the image. Keep those files present when building locally.

### Makefile

```bash
make install    # Install dependencies
make dev        # Install dev deps + pre-commit
make lint       # Code check (Ruff lint + format)
make test       # Run tests (pytest)
make run        # Start uvicorn --reload
```

## Architecture (v3.0)

```
Frontend (ES Modules) ──REST / WebSocket──▶ FastAPI Backend
                                              │
                                         ModelManager (cache + routing)
                                              │
                                        HandlerRegistry
                                     ┌────┬────┬────┬────┐
                                    YOLO DETR OWL  DINO BLIP
                                    (BaseHandler strategy pattern)
```

- **Strategy Pattern** — Separate handlers (YOLO / DETR / OWL-ViT / Grounding DINO / BLIP)
- **Pydantic Settings** — Unified config management from environment variables
- **Modern FastAPI Lifespan** — Replaces deprecated `on_event`
- **Route Extraction** — `main.py` split into `routes.py` for single responsibility
- **Structured Logging** — `logging` replaces `print`

## Project Structure

```
yolo-toys/
├── app/
│   ├── main.py             # FastAPI entry + lifespan lifecycle
│   ├── config.py           # Pydantic Settings
│   ├── routes.py           # API routes (REST + WebSocket)
│   ├── model_manager.py    # Model manager (cache + handler delegation)
│   ├── schemas.py          # Pydantic response models
│   └── handlers/           # Strategy pattern handlers
│       ├── base.py         # BaseHandler abstract class
│       ├── registry.py     # Model registry + handler factory
│       ├── yolo_handler.py # YOLO detect/segment/pose
│       ├── hf_handler.py   # DETR / OWL-ViT / Grounding DINO
│       └── blip_handler.py # BLIP Caption / VQA
├── frontend/
│   ├── index.html          # UI
│   ├── style.css           # Dark/light theme styles
│   ├── app.js              # Frontend entry (ES Module)
│   └── js/                 # Frontend modules (api, camera, draw)
├── tests/                  # API + WebSocket + unit tests
├── docs/                   # Detailed teaching docs
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Compose orchestration
└── pyproject.toml          # Project metadata + Ruff config
```

## Documentation

- [Detailed Docs](docs/README.md) — Architecture, data flow, implementation details
- [Project Page](https://lessup.github.io/yolo-toys/) — Online documentation
- [Changelog](changelog/) — Version history

## License

MIT License
