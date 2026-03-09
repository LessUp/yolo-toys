# YOLO-Toys — 多模型实时视觉识别系统

[![CI](https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml/badge.svg)](https://github.com/LessUp/yolo-toys/actions/workflows/ci.yml)
[![Pages](https://github.com/LessUp/yolo-toys/actions/workflows/pages.yml/badge.svg)](https://lessup.github.io/yolo-toys/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

[English](README.md) | 简体中文 | [项目主页](https://lessup.github.io/yolo-toys/)

> 基于 FastAPI + WebSocket 的实时视频物体识别平台，支持 YOLO、HuggingFace Transformers 和多模态模型

## 功能

### 支持的模型

| 类别 | 模型 | 说明 |
|------|------|------|
| **YOLO 检测** | YOLOv8 n/s/m/l/x | 实时目标检测（80 类 COCO） |
| **YOLO 分割** | YOLOv8 n/s/m-seg | 实例分割，像素级掩膜 |
| **YOLO 姿态** | YOLOv8 n/s/m-pose | 人体 17 关键点检测 |
| **DETR** | facebook/detr-resnet-50/101 | 端到端 Transformer 检测器 |
| **OWL-ViT** | google/owlvit-base-patch32 | 零样本开放词汇检测 |
| **Grounding DINO** | IDEA-Research/grounding-dino-tiny | 开放集检测，文本提示定位 |
| **BLIP Caption** | Salesforce/blip-image-captioning | 图像描述生成 |
| **BLIP VQA** | Salesforce/blip-vqa | 视觉问答 |

### 前端
- 摄像头实时采集、Canvas 叠加渲染
- 模型类别标签页切换、快速模型选择
- 动态调参：置信度、IoU、最大检测数、设备选择
- 显示开关：边框、标签、掩膜、关键点、骨架
- 深色/浅色主题切换，设置自动持久化

### 后端
- FastAPI REST + WebSocket 端点
- `/infer` — 统一推理、`/models` — 可用模型、`/health` — 健康检查
- `/caption` — 图像描述、`/vqa` — 视觉问答
- 模型缓存、自动设备选择、FP16 加速
- `asyncio.Semaphore` 异步并发控制

## 快速开始

```bash
pip install -r requirements.txt
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
make lint          # 代码规范检查 (Ruff lint + format)
make test          # 运行测试 (pytest)
make run           # 本地开发启动 uvicorn --reload
make compose-up    # Docker Compose 启动
make compose-down  # Docker Compose 停止
```

## 架构 (v3.0)

```
Frontend (ES Modules) ──REST / WebSocket──▶ FastAPI Backend
                                              │
                                         ModelManager (缓存 + 路由)
                                              │
                                        HandlerRegistry
                                     ┌────┬────┬────┬────┐
                                    YOLO DETR OWL  DINO BLIP
                                    (BaseHandler 策略模式)
```

- **策略模式** — 每种模型类型独立 Handler（YOLO / DETR / OWL-ViT / Grounding DINO / BLIP）
- **Pydantic Settings** — 环境变量统一管理
- **Lifespan** — 现代 FastAPI lifespan 替代已弃用的 `on_event`
- **路由分离** — `main.py` 拆分为 `routes.py`，职责单一
- **结构化日志** — `logging` 替代 `print`

## 目录结构

```
yolo-toys/
├── app/
│   ├── main.py             # FastAPI 入口 + lifespan 生命周期
│   ├── config.py           # Pydantic Settings 统一配置
│   ├── routes.py           # API 路由（REST + WebSocket）
│   ├── model_manager.py    # 模型管理器（缓存 + Handler 委托）
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
│   ├── app.js              # 前端入口（ES Module）
│   └── js/                 # 前端模块 (api, camera, draw)
├── tests/                  # API + WebSocket + 单元测试
├── docs/                   # 详细教学文档
├── Dockerfile              # 多阶段 Docker 构建
├── docker-compose.yml      # Compose 编排
└── pyproject.toml          # 项目元数据 + Ruff 配置
```

## API 参考

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查（版本、设备、默认配置） |
| `GET` | `/models` | 获取所有可用模型（按类别分组） |
| `GET` | `/models/{id}` | 获取指定模型详情 |
| `GET` | `/labels` | 获取模型标签列表 |
| `POST` | `/infer` | 统一推理端点（图像 + 参数） |
| `POST` | `/caption` | 图像描述生成 |
| `POST` | `/vqa` | 视觉问答 |
| `WS` | `/ws` | WebSocket 实时推理 |

### `/infer` 参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `conf` | float | 0.25 | 置信度阈值 |
| `iou` | float | 0.45 | NMS IoU 阈值 |
| `max_det` | int | 300 | 最大检测数 |
| `device` | string | auto | `cpu` / `mps` / `cuda:0` |
| `model` | string | yolov8s.pt | 模型 ID |
| `imgsz` | int | - | 推理尺寸 |
| `half` | bool | false | FP16 半精度（仅 CUDA） |
| `text_queries` | string | - | 逗号分隔文本查询（OWL-ViT / Grounding DINO） |
| `question` | string | - | VQA 问题 |

## 配置

环境变量（通过 `.env` 文件或 Docker `-e` 设置）：

| 变量 | 默认 | 说明 |
|------|------|------|
| `PORT` | 8000 | 服务端口 |
| `MODEL_NAME` | yolov8s.pt | 默认模型 |
| `CONF_THRESHOLD` | 0.25 | 默认置信度 |
| `IOU_THRESHOLD` | 0.45 | 默认 IoU |
| `MAX_DET` | 300 | 默认最大检测数 |
| `DEVICE` | (auto) | 计算设备 |
| `SKIP_WARMUP` | (空) | 非空值跳过启动预热 |
| `ALLOW_ORIGINS` | * | CORS 允许来源 |
| `MAX_UPLOAD_MB` | 10 | 上传大小上限 (MB) |
| `MAX_CONCURRENCY` | 4 | 并发推理限制 |

## 常见问题

- **首次推理较慢** — 模型权重下载 + 首次加载编译，后续会缓存
- **浏览器权限** — 请允许访问摄像头；如被拦截，检查浏览器地址栏权限设置
- **跨设备访问** — 确保同一局域网，使用 `http://<LAN_IP>:8000/`
- **Apple Silicon** — 安装的 `torch` 会自动使用 MPS 后端（若可用）

## 开发与贡献

```bash
# 安装开发依赖
pip install -r requirements-dev.txt
pre-commit install

# 代码检查
ruff check .
ruff format --check .

# 运行测试
python -m pytest
```

- 代码风格：Ruff lint + format（配置见 `pyproject.toml`）
- 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)
- 行为准则：[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## 文档

- [详细教学文档](docs/README.md) — 架构原理、数据流、前后端实现详解
- [项目主页](https://lessup.github.io/yolo-toys/) — 在线文档
- [更新日志](changelog/) — 版本历史

## 许可证

MIT License

