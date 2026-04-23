---
layout: default
title: YOLO-Toys — Multi-Model Vision Inference
nav_exclude: true
seo:
  type: SoftwareApplication
  name: YOLO-Toys
  applicationCategory: DeveloperApplication
  operatingSystem: Linux, macOS, Windows
---

<div class="hero-section">
  <div class="hero-badge">Vision inference, one API surface</div>
  <h1 class="hero-title">YOLO-Toys</h1>
  <p class="hero-subtitle">
    Run YOLOv8, DETR, OWL-ViT, Grounding DINO, and BLIP behind one FastAPI + WebSocket interface.
    <br>
    <span class="hero-subtitle-cn">把多种视觉模型统一到一个后端与流式接口之下。</span>
  </p>

  <div class="hero-actions">
    <a href="{{ '/docs/getting-started/quickstart.html' | relative_url }}" class="btn btn-primary">
      <span class="btn-icon">🚀</span>
      <span class="btn-text">Quick Start<br><small>快速上手</small></span>
    </a>
    <a href="{{ '/docs/' | relative_url }}" class="btn btn-secondary">
      <span class="btn-icon">📖</span>
      <span class="btn-text">Documentation<br><small>查看文档</small></span>
    </a>
    <a href="https://github.com/LessUp/yolo-toys" class="btn btn-secondary" target="_blank" rel="noopener">
      <span class="btn-icon">🐙</span>
      <span class="btn-text">Repository<br><small>GitHub</small></span>
    </a>
  </div>
</div>

## Why people use it

<div class="features-grid">
  <div class="feature-card">
    <div class="feature-icon">🎯</div>
    <h3>Multiple model families</h3>
    <p>Compare classic YOLO, transformer detectors, open-vocabulary models, and multimodal BLIP flows in one service.</p>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🔌</div>
    <h3>REST + WebSocket</h3>
    <p>Use standard HTTP for requests or switch to streaming inference when you need low-latency frame-by-frame results.</p>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🏗️</div>
    <h3>Handler-based architecture</h3>
    <p>The runtime is organized around reusable handlers and a registry so model families stay isolated and easier to extend.</p>
  </div>
</div>

## Supported tasks

| Task | Representative models |
| --- | --- |
| Detection / segmentation / pose | YOLOv8 |
| Transformer detection | DETR |
| Zero-shot detection | OWL-ViT, Grounding DINO |
| Caption / VQA | BLIP |

## Start paths

### Docker

```bash
docker run -p 8000:8000 ghcr.io/lessup/yolo-toys:latest
```

### Local dev

```bash
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys
bash scripts/dev.sh setup
. .venv/bin/activate
make run
```

## Choose your next page

| If you want... | Go to |
| --- | --- |
| the fastest runnable path | [Quick Start]({{ '/docs/getting-started/quickstart.html' | relative_url }}) |
| API contracts and examples | [API docs]({{ '/docs/api/' | relative_url }}) |
| architecture and handlers | [Architecture]({{ '/docs/architecture/' | relative_url }}) |
| deployment and env guidance | [Deployment]({{ '/docs/deployment/' | relative_url }}) |
| release history | [Changelog]({{ '/changelog/' | relative_url }}) |
