<div align="center">

<!-- PROJECT LOGO/BANNER -->
<h1 align="center">🎯 YOLO-Toys</h1>
<h3 align="center">多模型实时视觉识别平台</h3>

<p align="center">
  <strong>FastAPI + YOLOv8 + Transformers</strong> — 基于 WebSocket 流式传输的实时目标检测、分割、姿态估计与多模态 AI
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
  <a href="README.md">English</a> •
  <a href="https://lessup.github.io/yolo-toys/">🌐 在线演示</a> •
  <a href="docs/README.md">📚 项目文档</a> •
  <a href="CONTRIBUTING.md">🤝 参与贡献</a>
</p>

</div>

---

## 🚀 核心功能

<div align="center">

| 🎯 **目标检测** | 🖼️ **实例分割** | 🏃 **姿态估计** |
|:---:|:---:|:---:|
| 80类 COCO 实时检测 | 像素级掩膜分割 | 17关键点人体姿态 |
| YOLOv8 n/s/m/l/x | YOLOv8 n/s/m-seg | YOLOv8 n/s/m-pose |

| 🔄 **Transformer** | 🔍 **开放词汇** | 📝 **多模态** |
|:---:|:---:|:---:|
| DETR ResNet-50/101 | OWL-ViT base-patch32 | BLIP 图像描述 |
| 端到端检测器 | 零样本检测 | 视觉问答 |

</div>

### 前端能力

- 📷 **摄像头捕获** 与 Canvas 叠加渲染
- 🎛️ **模型分类标签**，支持参数配置
- ⚙️ **动态参数调节**：置信度、IoU、最大检测数、设备选择
- 🎨 **显示控制**：检测框、标签、掩膜、关键点、骨架
- 🌓 **深色/浅色主题** 与设置自动持久化

### 后端亮点

- ⚡ **FastAPI** 提供 REST + WebSocket 端点
- 💾 **模型缓存** 与自动设备选择，支持 FP16 加速
- 🔀 **异步并发控制** 通过 `asyncio.Semaphore`
- 🧩 **策略模式** 处理不同类型的模型
- 🔧 **Pydantic Settings** 统一环境配置管理

---

## ⚡ 性能基准

> 每帧延迟（毫秒），数值越小越好

| 模型 | 任务 | CPU (i7-12700) | RTX 3060 | Apple M1 |
|------|------|----------------|----------|----------|
| YOLOv8n | 检测 | ~25ms | ~5ms | ~8ms |
| YOLOv8s | 检测 | ~35ms | ~6ms | ~12ms |
| YOLOv8n-seg | 分割 | ~45ms | ~10ms | ~15ms |
| DETR-R50 | 检测 | ~120ms | ~25ms | ~40ms |
| OWL-ViT | 零样本 | ~150ms | ~30ms | ~50ms |

*注：性能因输入分辨率和批量大小而异。WebSocket 流针对 640x480 输入优化。*

---

## 📋 系统要求

### 最低配置
- **Python**: 3.11+
- **内存**: 4GB（大型模型建议 8GB+）
- **存储**: 2GB 可用空间

### GPU 支持（可选）
- **NVIDIA**: CUDA 11.8+ 与 cuDNN
- **Apple 芯片**: 支持 MPS 后端
- **CPU**: 始终支持，推理较慢

### 浏览器兼容性
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- 实时演示需要摄像头访问权限

---

## 🚀 快速开始

### 方式一：Python 原生（开发推荐）

```bash
# 克隆仓库
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys

# 创建虚拟环境
python -m venv .venv

# 激活（Linux/macOS）
source .venv/bin/activate
# 激活（Windows PowerShell）
# .venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 `http://localhost:8000` — 授予摄像头权限并开始检测！

### 方式二：Docker

```bash
# 构建并运行
cp .env.example .env
docker build -t yolo-toys .
docker run -p 8000:8000 --env-file .env yolo-toys
```

### 方式三：Docker Compose（生产推荐）

```bash
cp .env.example .env
docker-compose up --build -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 📡 API 参考

<details>
<summary><b>🔍 REST 接口</b></summary>

| 方法 | 端点 | 描述 |
|------|------|------|
| `GET` | `/health` | 健康检查与系统信息 |
| `GET` | `/models` | 列出可用模型 |
| `GET` | `/labels` | 获取模型的类别标签 |
| `POST` | `/infer` | 单张图片推理 |
| `POST` | `/caption` | 图像描述生成 |
| `POST` | `/vqa` | 视觉问答 |

</details>

<details>
<summary><b>🔌 WebSocket 流式传输</b></summary>

```javascript
const ws = new WebSocket(
  'ws://localhost:8000/ws'
  + '?model=yolov8n.pt'
  + '&conf=0.25'
  + '&iou=0.45'
  + '&max_det=300'
);

// 发送二进制 JPEG 帧
ws.send(imageBlob);

// 接收 JSON 结果
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  // result.detections: [...]
  // result.inference_time: number (ms)
};
```

</details>

<details>
<summary><b>📤 示例：单图推理</b></summary>

```bash
curl -X POST "http://localhost:8000/infer" \
  -F "file=@image.jpg" \
  -F "model=yolov8n.pt" \
  -F "conf=0.25" \
  -F "iou=0.45"
```

**响应：**
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

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  摄像头  │  │  Canvas  │  │ WebSocket│  │  HTTP    │    │
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
              │   (缓存 + 路由分发)        │
              └─────────────┬─────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │   YOLO     │   │Transformers│   │    BLIP    │
   │  Handler   │   │  Handler   │   │  Handler   │
   └────────────┘   └────────────┘   └────────────┘
```

**核心设计模式：**
- **策略模式**：YOLO / DETR / OWL-ViT / Grounding DINO / BLIP 分离处理器
- **Pydantic 配置**：从环境变量统一配置管理
- **现代 FastAPI Lifespan**：替代已弃用的 `on_event`
- **路由分离**：职责分离，路由逻辑独立在 `routes.py`
- **结构化日志**：生产级日志替代 print 语句

---

## 📁 项目结构

```
yolo-toys/
├── app/                      # 后端应用
│   ├── handlers/             # 策略模式处理器
│   │   ├── base.py           # BaseHandler 抽象基类
│   │   ├── registry.py       # 模型注册表与工厂
│   │   ├── yolo_handler.py   # YOLO 检测/分割/姿态
│   │   ├── hf_handler.py     # DETR/OWL-ViT/Grounding DINO
│   │   └── blip_handler.py   # BLIP 描述/VQA
│   ├── main.py               # FastAPI 入口与生命周期
│   ├── config.py             # Pydantic 配置
│   ├── routes.py             # API 路由（REST + WebSocket）
│   ├── model_manager.py      # 模型缓存与处理器委托
│   └── schemas.py            # Pydantic 响应模型
├── frontend/                 # 静态前端
│   ├── js/                   # 前端模块
│   ├── index.html            # UI 界面
│   ├── style.css             # 深色/浅色主题
│   └── app.js                # 主应用逻辑
├── tests/                    # API + WebSocket + 单元测试
├── docs/                     # 详细文档
├── changelog/                # 版本历史
├── docker-compose.yml        # Docker 编排
├── Dockerfile                # 多阶段构建
├── pyproject.toml            # 项目元数据与 Ruff 配置
├── Makefile                  # 开发命令
└── requirements.txt          # Python 依赖
```

---

## 🛠️ 开发指南

```bash
# 安装开发依赖
pip install -r requirements-dev.txt
pre-commit install

# 运行代码检查
make lint

# 运行测试
make test

# 启动开发服务器
make run
```

### 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `MODEL_NAME` | `yolov8n.pt` | 默认模型名称 |
| `CONF_THRESHOLD` | `0.25` | 检测置信度阈值 |
| `IOU_THRESHOLD` | `0.45` | NMS IoU 阈值 |
| `MAX_DET` | `300` | 每帧最大检测数 |
| `DEVICE` | `auto` | 推理设备 (cpu/cuda/mps) |
| `SKIP_WARMUP` | `false` | 启动时跳过模型预热 |
| `MAX_CONCURRENCY` | `4` | 最大并发推理请求数 |

---

## 📚 文档资源

- **[📖 详细文档](docs/README.md)** — 架构设计、数据流、实现细节
- **[🌐 项目首页](https://lessup.github.io/yolo-toys/)** — 在线文档与演示
- **[📝 更新日志](changelog/)** — 版本历史与迁移指南
- **[🤝 参与贡献](CONTRIBUTING.md)** — 开发指南与 PR 工作流程

---

## 🤝 参与贡献

欢迎贡献！请阅读我们的 [贡献指南](CONTRIBUTING.md) 了解详情。

**贡献者快速开始：**

```bash
# Fork 并克隆
git clone https://github.com/your-username/yolo-toys.git

# 创建分支
git checkout -b feat/your-feature

# 修改、提交、推送到你的仓库
git commit -m "feat: 添加新功能"
git push origin feat/your-feature

# 创建 Pull Request
```

---

## 📄 开源协议

本项目采用 [MIT 协议](LICENSE) 开源。

---

## 🙏 致谢

- **[Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)** — 先进的目标检测框架
- **[HuggingFace Transformers](https://github.com/huggingface/transformers)** — 开源机器学习模型库
- **[FastAPI](https://fastapi.tiangolo.com/)** — 现代、快速的 Web 框架
- **[OpenCV](https://opencv.org/)** — 计算机视觉库

---

<div align="center">

如果本项目对你有帮助，请给我们一颗 ⭐！

[**🌐 访问在线演示**](https://lessup.github.io/yolo-toys/) • [**🐛 报告问题**](https://github.com/LessUp/yolo-toys/issues) • [**💡 功能建议**](https://github.com/LessUp/yolo-toys/issues)

</div>
