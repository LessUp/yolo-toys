---
layout: default
title: "YOLO-Toys — 多模型实时视觉识别系统"
description: "支持 YOLO 检测/分割/姿态 · DETR · OWL-ViT · Grounding DINO · BLIP Caption/VQA · WebSocket 流式推理"
---

<div align="center">

# YOLO-Toys

**多模型实时视觉识别系统**

[![CI](https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml/badge.svg)](https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/LessUp/yolo-toys/blob/main/LICENSE)
![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

*基于 FastAPI + WebSocket 的实时视频物体识别平台，*
*支持 YOLO、HuggingFace Transformers 和多模态模型*

[快速开始](#快速开始) · [支持的模型](#支持的模型) · [架构设计](#架构设计) · [详细文档](docs/README.md) · [GitHub 仓库](https://github.com/LessUp/yolo-toys)

</div>

---

## 亮点

|  | 特性 | 说明 |
|:---:|------|------|
| 🎯 | **多模型动态切换** | YOLO 检测/分割/姿态、DETR、OWL-ViT、Grounding DINO、BLIP |
| 🔌 | **WebSocket 实时推理** | 低延迟视频流处理，支持自动重连和心跳 |
| 🤖 | **HuggingFace 集成** | 开放词汇检测、图像描述生成、视觉问答 |
| 🏗️ | **策略模式架构** | 每种模型类型独立 Handler，扩展零耦合 |
| 🐳 | **Docker 一键部署** | 多阶段构建，非 root 运行，模型缓存卷 |
| 🌓 | **现代化 UI** | 深色/浅色主题、Toast 通知、设置自动持久化 |

---

## 支持的模型

### 目标检测

| 模型 | 类型 | 速度 | 精度 | 说明 |
|------|------|:----:|:----:|------|
| YOLOv8 n/s/m/l/x | YOLO 检测 | ⚡⚡⚡ ~ ⚡ | ★★ ~ ★★★★★ | Ultralytics 实时目标检测 |
| YOLOv8 n/s/m-seg | YOLO 分割 | ⚡⚡⚡ ~ ⚡⚡ | ★★ ~ ★★★★ | 实例分割，像素级掩膜 |
| YOLOv8 n/s/m-pose | YOLO 姿态 | ⚡⚡⚡ ~ ⚡⚡ | ★★ ~ ★★★★ | 人体 17 关键点检测 |
| DETR ResNet-50/101 | Transformer | ⚡⚡ ~ ⚡ | ★★★★ ~ ★★★★★ | Facebook 端到端 Transformer 检测 |

### 开放词汇检测

| 模型 | 输入 | 说明 |
|------|------|------|
| OWL-ViT | 文本 + 图像 | Google 零样本检测，检测任意文本描述的物体 |
| Grounding DINO | 文本 + 图像 | IDEA-Research 开放集检测，文本提示定位 |

### 多模态

| 模型 | 任务 | 说明 |
|------|------|------|
| BLIP Caption (base/large) | 图像描述 | Salesforce 图像描述生成 |
| BLIP VQA | 视觉问答 | 根据图片内容回答自然语言问题 |

---

## 架构设计

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
│                   FastAPI Backend (routes.py)                 │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              ModelManager (model_manager.py)             │ │
│  │   load_model() → cache    infer() → route to handler    │ │
│  └────────────────────────────┬────────────────────────────┘ │
│                               │                              │
│  ┌────────────────────────────┴────────────────────────────┐ │
│  │             HandlerRegistry (registry.py)               │ │
│  │   MODEL_REGISTRY → category → handler class mapping     │ │
│  └──┬──────────┬──────────┬──────────┬──────────┬──────────┘ │
│     │          │          │          │          │            │
│  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐  ┌──┴───┐        │
│  │ YOLO │  │ DETR │  │OWLViT│  │G-DINO│  │ BLIP │        │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘        │
│  (BaseHandler 策略模式 — 统一 load() + infer() 接口)       │
└──────────────────────────────────────────────────────────────┘
```

**核心设计决策：**

- **策略模式** — 每种模型类型实现 `BaseHandler`，新增模型只需添加 Handler + 注册
- **Pydantic Settings** — 环境变量统一管理，告别散乱的 `os.getenv`
- **异步并发控制** — `asyncio.Semaphore` 限制同时推理数
- **模型缓存** — 首次加载后缓存，避免重复初始化
- **安全头** — 自动注入 `X-Content-Type-Options`、`X-Frame-Options`、`Referrer-Policy`

---

## 快速开始

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys

# 创建虚拟环境
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

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
# 停止: docker compose down --remove-orphans
```

### Makefile

```bash
make install       # 安装运行依赖
make dev           # 安装开发依赖 + pre-commit
make lint          # 代码规范检查 (Ruff)
make test          # 运行测试 (pytest)
make run           # 本地开发启动
make compose-up    # Docker Compose 启动
```

---

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **后端框架** | Python 3.11+, FastAPI | REST API + WebSocket 端点 |
| **检测模型** | Ultralytics YOLOv8 | 检测 / 分割 / 姿态估计 |
| **Transformer** | HuggingFace Transformers | DETR / OWL-ViT / Grounding DINO / BLIP |
| **配置管理** | Pydantic Settings | 环境变量统一读取 |
| **前端** | HTML + CSS + JavaScript (ES Modules) | Canvas 绘制 + WebSocket 通信 |
| **容器化** | Docker 多阶段构建 + docker-compose | 一键部署，模型缓存卷 |
| **代码质量** | Ruff (lint + format) + pre-commit | 统一风格，CI 检查 |
| **测试** | pytest + httpx | API / WebSocket / 注册表单元测试 |

---

## 项目结构

```
yolo-toys/
├── app/
│   ├── main.py             # FastAPI 入口 + lifespan 生命周期
│   ├── config.py           # Pydantic Settings 统一配置
│   ├── routes.py           # API 路由 (REST + WebSocket)
│   ├── model_manager.py    # 模型管理器 (缓存 + 路由)
│   ├── schemas.py          # Pydantic 响应模型
│   └── handlers/           # 策略模式处理器
│       ├── base.py         # BaseHandler 抽象基类
│       ├── registry.py     # 模型注册表 + 处理器工厂
│       ├── yolo_handler.py # YOLO 检测/分割/姿态
│       ├── hf_handler.py   # DETR / OWL-ViT / Grounding DINO
│       └── blip_handler.py # BLIP Caption / VQA
├── frontend/
│   ├── index.html          # UI 界面
│   ├── style.css           # 深色/浅色主题样式
│   ├── app.js              # 前端入口 (ES Module)
│   └── js/                 # 前端模块 (api, camera, draw)
├── tests/                  # API + WebSocket + 单元测试
├── docs/                   # 详细教学文档
├── Dockerfile              # 多阶段 Docker 构建
├── docker-compose.yml      # Compose 编排
└── pyproject.toml          # 项目元数据 + Ruff 配置
```

---

## API 概览

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 (版本、设备、默认配置) |
| `GET` | `/models` | 获取所有可用模型 (按类别分组) |
| `GET` | `/models/{id}` | 获取指定模型详情 |
| `GET` | `/labels` | 获取模型标签列表 |
| `POST` | `/infer` | 统一推理端点 (图像 + 参数) |
| `POST` | `/caption` | 图像描述生成 |
| `POST` | `/vqa` | 视觉问答 |
| `WS` | `/ws` | WebSocket 实时推理 |

---

## 文档

- [**项目 README**](README.md) — 快速上手指南
- [**详细教学文档**](docs/README.md) — 架构原理、数据流、前后端实现详解、扩展练习建议
- [**更新日志**](changelog/) — 版本历史
- [**贡献指南**](CONTRIBUTING.md) — 如何参与开发

---

## 许可证

[MIT License](https://github.com/LessUp/yolo-toys/blob/main/LICENSE) — 自由使用、修改和分发
