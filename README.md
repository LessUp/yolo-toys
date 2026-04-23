# YOLO-Toys

> Multi-model vision inference platform for **YOLOv8, DETR, OWL-ViT, Grounding DINO, and BLIP** behind one FastAPI + WebSocket interface.

[简体中文](README.zh-CN.md) · [GitHub Pages](https://lessup.github.io/yolo-toys/) · [Docs](https://lessup.github.io/yolo-toys/docs/) · [Issues](https://github.com/LessUp/yolo-toys/issues)

## Why this project exists

YOLO-Toys packages several practical vision tasks behind one consistent API:

- object detection, segmentation, and pose estimation
- open-vocabulary detection
- image captioning and visual question answering
- REST inference and low-latency WebSocket streaming

The project is optimized for people who want to **compare model families quickly**, build a lightweight demo/backend, or study how to unify mixed vision stacks under one handler architecture.

## Quick start

### Docker

```bash
docker run -p 8000:8000 ghcr.io/lessup/yolo-toys:latest
```

Open <http://localhost:8000>.

### Local development

```bash
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys
bash scripts/dev.sh setup
. .venv/bin/activate
make run
```

## What you get

| Surface | What it is for |
| --- | --- |
| `/infer` | Detection / segmentation / pose / open-vocabulary inference |
| `/caption` | BLIP image captioning |
| `/vqa` | BLIP visual QA |
| `/models`, `/labels` | Model discovery |
| `/ws` | Real-time streaming inference |
| `/metrics`, `/health`, `/system/*` | Operations and observability |

## Model families

| Family | Examples | Tasks |
| --- | --- | --- |
| YOLOv8 | `yolov8n.pt`, `yolov8n-seg.pt`, `yolov8n-pose.pt` | detect / segment / pose |
| DETR | `facebook/detr-resnet-50` | detect |
| OWL-ViT / Grounding DINO | `google/owlvit-base-patch32` | zero-shot detect |
| BLIP | `Salesforce/blip-image-captioning-base`, `Salesforce/blip-vqa-base` | caption / vqa |

## Repository guide

| Path | Role |
| --- | --- |
| `app/` | backend runtime |
| `tests/` | pytest suite |
| `openspec/` | current specs and change workflow |
| `docs/` | long-form docs |
| root Jekyll files | GitHub Pages landing + navigation |
| `.github/` | workflows, templates, Copilot instructions |

## Development workflow

Non-trivial work is **OpenSpec-first**:

1. explore or clarify
2. propose a change
3. implement from tasks
4. review at phase boundaries
5. archive the completed change

Canonical local commands:

```bash
make lint
make format
make hooks
make typecheck
make test
```

## Next step

- Want a guided overview? Start at the [GitHub Pages landing site](https://lessup.github.io/yolo-toys/).
- Want setup and API details? Go to [docs](https://lessup.github.io/yolo-toys/docs/).
- Want to contribute or finish repository cleanup? Read [CONTRIBUTING.md](CONTRIBUTING.md).
