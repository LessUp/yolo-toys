---
layout: default
title: YOLO-Toys
---

# YOLO-Toys — 多模型实时视觉识别系统

支持 YOLO、HuggingFace Transformers、多模态模型的实时视频物体识别平台。

## 核心特性

- **多模型动态切换** — YOLO 检测/分割/姿态、DETR、OWL-ViT、BLIP
- **HuggingFace 集成** — 支持开放词汇检测和多模态模型
- **多模态功能** — 图像描述生成、视觉问答 (VQA)
- **WebSocket 实时推理** — 低延迟视频流处理
- **策略模式架构** — 独立 Handler（YOLO / DETR / OWL-ViT / BLIP）
- **现代化 UI** — 深色/浅色主题，Toast 通知

## 文档

- [README](README.md) — 项目概述
- [详细教学文档](docs/README.md) — 架构与实现详解

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 访问 http://localhost:8000
```

### Docker Compose

```bash
cp .env.example .env
docker compose up --build -d
```

## 支持的模型

| 模型 | 类型 | 功能 |
|------|------|------|
| YOLOv8 | 检测/分割/姿态 | 80 类物体检测 |
| DETR | 检测 | Transformer 目标检测 |
| OWL-ViT | 开放词汇 | 任意文本描述检测 |
| BLIP | 多模态 | 图像描述 + VQA |

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3.11+, FastAPI |
| 模型 | Ultralytics, HuggingFace Transformers |
| 前端 | HTML + CSS + JS (ES Modules) |
| 实时 | WebSocket |
| 容器 | Docker, docker-compose |
| 质量 | Ruff (lint + format), pytest |

## 链接

- [GitHub 仓库](https://github.com/LessUp/YOLO-Toys)
- [README](README.md)
