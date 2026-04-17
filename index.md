---
layout: default
title: "YOLO-Toys — 多模型实时视觉识别系统"
description: "基于 FastAPI + WebSocket 的实时视频物体识别平台，支持 YOLO、HuggingFace Transformers 和多模态模型"
nav_order: 1
nav_exclude: true
---

<div class="hero-section" markdown="1">

# 🎯 YOLO-Toys

<p class="tagline">
  <strong>多模型实时视觉识别系统</strong><br>
  <span style="font-size: 1rem; color: #6b7280;">Multi-Model Real-Time Vision Recognition System</span>
</p>

<div class="badges">

[![CI](https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml/badge.svg)](https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml){:target="_blank"}
[![Pages](https://github.com/LessUp/yolo-toys/actions/workflows/pages.yml/badge.svg)](https://lessup.github.io/yolo-toys/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/LessUp/yolo-toys/blob/main/LICENSE)
![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI 0.115+](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

</div>

<div class="hero-buttons">
  <a href="{{ site.baseurl }}/docs/getting-started/quickstart.html" class="btn-primary">🚀 快速开始 / Quick Start</a>
  <a href="{{ site.baseurl }}/docs/" class="btn-secondary">📖 查看文档 / Documentation</a>
</div>

</div>

---

## ✨ 亮点 / Highlights

<div class="features-grid" markdown="1">

| 🎯 | **多模型动态切换** | 支持 YOLO 检测/分割/姿态、DETR、OWL-ViT、Grounding DINO、BLIP |
| 🔌 | **WebSocket 实时推理** | 低延迟视频流处理，支持自动重连和心跳机制 |
| 🤖 | **HuggingFace 集成** | 开放词汇检测、图像描述生成、视觉问答 |
| 🏗️ | **策略模式架构** | 每种模型类型独立 Handler，零耦合扩展 |
| 🐳 | **Docker 一键部署** | 多阶段构建，非 root 运行，模型缓存卷 |
| 🧪 | **现代化测试** | pytest + httpx，API/WebSocket/单元测试覆盖率 70%+ |

</div>

---

## 📊 支持的模型 / Supported Models

### 目标检测 / Object Detection

| 模型 | 类型 | 推荐场景 |
|------|------|----------|
| YOLOv8 n/s/m/l/x | 检测 | ⚡ 实时目标检测，速度优先 |
| YOLOv8 n/s/m-seg | 分割 | 🎨 实例分割，像素级掩膜 |
| YOLOv8 n/s/m-pose | 姿态 | 🏃 人体 17 关键点检测 |
| DETR ResNet-50/101 | Transformer | 🔬 端到端 Transformer 检测 |

### 开放词汇检测 / Open Vocabulary Detection

| 模型 | 输入 | 说明 |
|------|------|------|
| OWL-ViT | 文本 + 图像 | Google 零样本检测，检测任意文本描述的物体 |
| Grounding DINO | 文本 + 图像 | IDEA-Research 开放集检测 |

### 多模态 / Multimodal

| 模型 | 任务 | 说明 |
|------|------|------|
| BLIP Caption | 图像描述 | Salesforce 图像描述生成 |
| BLIP VQA | 视觉问答 | 根据图片内容回答自然语言问题 |

---

## 🏗️ 架构设计 / Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend (ES Modules)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ camera.js│  │  draw.js │  │  api.js  │  │   app.js    │  │
│  └─────┬────┘  └─────┬────┘  └────┬─────┘  └──────┬──────┘  │
│        └─────────────┴────────────┴───────────────┘          │
└──────────────────────────┬───────────────────────────────────┘
                  REST / WebSocket
┌──────────────────────────┴───────────────────────────────────┐
│                   FastAPI Backend (app/api/)                  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              ModelManager (model_manager.py)             │ │
│  │        TTL+LRU 缓存 · 内存压力监控 · 自动驱逐           │ │
│  └────────────────────────────┬────────────────────────────┘ │
│                               │                               │
│  ┌────────────────────────────┴────────────────────────────┐ │
│  │             HandlerRegistry (strategy pattern)          │ │
│  │    MODEL_REGISTRY → category → handler factory          │ │
│  └──┬──────────┬──────────┬──────────┬──────────┬──────────┘ │
│     │          │          │          │          │            │
│  ┌──┴──┐  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐         │
│  │ YOLO │  │ DETR │  │OWLViT│  │G-DINO│  │ BLIP │         │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘         │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始 / Quick Start

### Python 本地运行 / Local Python

```bash
# 克隆仓库
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 访问 http://localhost:8000
```

### Docker Compose / Docker 部署

```bash
# 复制配置
cp config/.env.example config/.env

# 启动服务
docker compose up --build -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down --remove-orphans
```

---

## 📚 技术栈 / Tech Stack

| 层级 | 技术 | 用途 |
|------|------|------|
| **后端框架** | Python 3.11+, FastAPI | REST API + WebSocket |
| **检测模型** | Ultralytics YOLOv8 | 检测/分割/姿态估计 |
| **Transformer** | HuggingFace Transformers | DETR / OWL-ViT / BLIP |
| **配置管理** | Pydantic Settings | 环境变量统一管理 |
| **前端** | HTML + CSS + JS (ES Modules) | Canvas 绘制 + WebSocket |
| **容器化** | Docker 多阶段构建 | 一键部署，模型缓存 |
| **代码质量** | Ruff + pre-commit | 统一风格，CI 检查 |
| **监控** | Prometheus + Grafana | 指标收集与可视化 |

---

## 📖 文档导航 / Documentation

### 🚀 开始 / Getting Started
- [安装指南](/docs/getting-started/installation.html)
- [快速开始](/docs/getting-started/quickstart.html)

### 🔌 API 文档 / API
- [REST API](/docs/api/rest-api.html)
- [WebSocket 协议](/docs/api/websocket.html)

### 🏗️ 架构 / Architecture
- [系统概述](/docs/architecture/overview.html)
- [处理器模式](/docs/architecture/handlers.html)

### 🐳 部署 / Deployment
- [Docker 部署](/docs/deployment/docker.html)
- [环境变量](/docs/deployment/environments.html)

---

## 🤝 贡献 / Contributing

欢迎贡献代码！请查看：
- [贡献指南](/CONTRIBUTING.html)
- [代码规范](/AGENTS.html)

---

## 📜 许可证 / License

[MIT License](https://github.com/LessUp/yolo-toys/blob/main/LICENSE) — 自由使用、修改和分发
