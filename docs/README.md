# YOLO-Toys 教学文档

> 面向个人学习与实战演练的实时目标检测小项目说明

---

## 1. 项目简介

YOLO-Toys 是一个基于 **FastAPI + Ultralytics YOLOv8 + HuggingFace Transformers + 原生前端** 的多模型实时视觉识别 Demo：

- 后端使用 FastAPI 提供 `/infer`、`/caption`、`/vqa`、`/health`、`/models`、`/labels`、`/ws` 等接口。
- 模型侧同时支持 YOLO 检测 / 分割 / 姿态估计，以及 Transformers 系列的 DETR、开放词汇检测（OWL-ViT / Grounding DINO）与多模态（BLIP Caption / VQA）。
- 前端用浏览器摄像头 / 本地图片，实时把图像发给后端，并在 Canvas 上绘制检测框、掩膜、关键点与骨架；对于 Caption / VQA 任务会展示文本输出。
- 工程层面提供 Docker、docker-compose、Makefile、pre-commit、pytest 等，方便你把它当成一个“小而全”的学习项目。

本教学文档的目标：

- 让你能从 0 理解这个项目的架构与代码；
- 帮你梳理“浏览器 → 后端 API → 模型推理 → 前端可视化”的完整数据流；
- 给出一套循序渐进的扩展练习建议，方便你继续改造和玩这个项目。

---

## 2. 技术栈与关键依赖

- **后端**：
  - Python 3.11
  - FastAPI / Uvicorn
  - Ultralytics YOLOv8
  - PyTorch (torch)
  - HuggingFace Transformers (+ accelerate)
  - OpenCV (opencv-python-headless)
  - NumPy, Pillow

- **前端**：
  - 原生 HTML + CSS + JavaScript
  - 浏览器媒体 API（`getUserMedia`、`<video>`、`<canvas>`）
  - Fetch / WebSocket

- **工程化**：
  - Docker / docker-compose
  - Makefile
  - pytest
  - pre-commit（Ruff lint + format）

建议在阅读本项目代码之前，先对以下概念有大致了解：

- HTTP API 与 JSON 返回体；
- WebSocket 的基本使用方式；
- Python 虚拟环境 / 依赖管理；
- 基本的前端 DOM 操作与 Canvas 绘图。

---

## 3. 快速开始

### 3.1 本地运行（推荐）

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -U pip
pip install -r requirements.txt

# （可选）安装开发依赖（用于运行测试/代码规范检查）
pip install -r requirements-dev.txt

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

浏览器访问：

```text
http://localhost:8000/
```

- 首次运行时可能需要下载 YOLOv8 权重，确保可以访问外网。
- 页面加载后，点击“开始”按钮授予摄像头权限，即可看到实时识别结果。

### 3.2 使用 Docker 运行

```bash
# 构建镜像
docker build -t vision-det .

# 运行容器
docker run --rm -it -p 8000:8000 \
  -e MODEL_NAME=yolov8n.pt \
  -e CONF_THRESHOLD=0.3 \
  -e IOU_THRESHOLD=0.45 \
  -e DEVICE=cpu \
  vision-det
```

同样访问 `http://localhost:8000/` 即可。

### 3.3 使用 Docker Compose

```bash
docker compose up --build -d
# 关闭
docker compose down --remove-orphans
```

---

## 4. 目录结构与文件说明

项目根目录主要结构如下（简化）：

```text
YOLO-Toys/
├─ app/
│  ├─ main.py             # FastAPI 入口 + lifespan 生命周期
│  ├─ config.py           # Pydantic Settings 统一配置
│  ├─ routes.py           # API 路由（REST + WebSocket）
│  ├─ model_manager.py    # 模型管理器（缓存 + Handler 委托）
│  ├─ schemas.py          # Pydantic 响应模型
│  └─ handlers/           # 策略模式处理器
│     ├─ base.py          # BaseHandler 抽象基类
│     ├─ registry.py      # 模型注册表 + 处理器工厂
│     ├─ yolo_handler.py  # YOLO 检测/分割/姿态
│     ├─ hf_handler.py    # DETR / OWL-ViT / Grounding DINO
│     └─ blip_handler.py  # BLIP Caption / VQA
├─ frontend/
│  ├─ index.html          # UI 界面
│  ├─ style.css           # 深色/浅色主题样式
│  ├─ app.js              # 前端入口（ES Module）
│  └─ js/                 # 前端模块 (api, camera, draw)
├─ tests/                 # API + WebSocket + 单元测试
├─ docs/
│  └─ README.md           # 本教学文档
├─ Dockerfile
├─ docker-compose.yml
├─ Makefile
├─ requirements.txt
├─ requirements-dev.txt
├─ pyproject.toml         # Ruff lint + format + pytest 配置
└─ README.md              # 项目简要说明与运行指南
```

你可以对照源码一起看本教学文档，效果会更好。

---

## 5. 后端架构与数据流

### 5.1 FastAPI 入口：`app/main.py`

`app/main.py` 是后端服务的入口，主要职责：

- 创建 FastAPI 应用实例；
- 配置 CORS、中间件（GZip、安全响应头）；
- 在启动时预热默认模型（可通过 `SKIP_WARMUP` 关闭）；
- 暴露多个 HTTP / WebSocket 接口；
- 挂载 `frontend/` 作为静态前端目录。

关键端点概览：

- `GET /health`：健康检查，返回运行状态、默认模型、设备等信息。 
- `POST /infer`：单张图片推理（表单 `file`，返回检测结果 JSON）。
- `POST /caption`：图像描述生成（表单 `file`，返回 caption）。
- `POST /vqa`：视觉问答（表单 `file` + 查询参数 `question`，返回 answer）。
- `GET /models`：返回推荐模型列表及默认模型名。
- `GET /labels`：根据模型返回所有类别标签列表。
- `WEBSOCKET /ws`：二进制 JPEG 帧实时推理，返回推理结果 JSON。

这些路由内部统一调用 `app.model_manager.model_manager.infer` 来执行对应模型的推理逻辑，并返回统一结构的结果。

### 5.2 推理逻辑：`app/model_manager.py`

`model_manager.py` 负责：

- 维护 `MODEL_REGISTRY`：定义各模型的类别、名称与说明，用于 `/models` 按类别输出。
- 提供 `ModelManager`：
  - `load_model(model_id)`：按需加载并缓存 YOLO / Transformers 模型与 Processor。
  - `infer(model_id, image, ...)`：统一推理入口，根据模型类别分发到：
    - YOLO 检测 / 分割 / 姿态（`infer_yolo`）
    - DETR 检测（`infer_detr`）
    - 开放词汇检测：OWL-ViT / Grounding DINO（`infer_owlvit` / `infer_grounding_dino`，需要 `text_queries`）
    - 多模态：Caption / VQA（`infer_caption` / `infer_vqa`）
- 统一返回结构：
  - 检测类任务返回 `detections`（bbox/score/label，可选 polygons/keypoints）
  - Caption 返回 `caption`
  - VQA 返回 `question` 与 `answer`
  - 开放词汇检测会回显 `text_queries`

你可以在这里尝试：

- 切换 `MODEL_NAME` 或在前端选择不同类别模型，观察 `task` 与返回字段的变化。
- 对开放词汇检测模型设置 `text_queries`（逗号分隔），观察检测结果与类别标签变化。

### 5.3 后端配置与环境变量

常用环境变量（可通过 `.env`、docker-compose 或 shell 设置）：

- `MODEL_NAME`: 默认模型名或权重路径，例如 `yolov8n.pt`。
- `CONF_THRESHOLD`: 置信度阈值，默认约 0.25–0.3。
- `IOU_THRESHOLD`: NMS IoU 阈值，默认约 0.45。
- `MAX_DET`: 单帧最大检测目标数，默认 300。
- `DEVICE`: 推理设备，如 `cpu`、`mps`、`cuda:0`；留空则自动选择。
- `SKIP_WARMUP`: 任意非空值则跳过启动预热流程。
- `ALLOW_ORIGINS`: CORS 允许的来源，默认 `*`。
- `MAX_UPLOAD_MB`: 单张图片上传大小上限（MB）。
- `MAX_CONCURRENCY`: 后端推理并发限制。

建议你自己动手：

1. 修改 `.env.example` 中的值，复制为 `.env`。
2. 使用 `make docker-run` 读取 `.env` 并观察行为差异。

---

## 6. 前端架构与关键逻辑

前端入口文件为 `frontend/index.html`、`frontend/style.css`、`frontend/app.js`。

### 6.1 布局与控件：`index.html`

核心结构：

- 顶部控制区 `.controls`：
  - `开始 / 停止` 按钮（摄像头采集）。
  - 本地图片上传：`#imageFile` + `#inferImage` 按钮。
  - 服务地址输入框（可用于跨设备访问）。
  - 是否使用 WebSocket 的开关。
  - 模型下拉选择 + 自定义模型输入框。
  - 推理参数：发送帧率、发送宽度、置信度、IoU、最大检测数、设备、JPEG 质量、推理尺寸、FP16 等。
  - 显示开关：框、标签、掩膜、关键点、骨架；掩膜透明度滑条。

- 中间主区域：
  - `.layout` 左列：`<canvas id="canvas">`，用来渲染视频帧与检测结果。
  - `.layout` 右列：`<aside class="sidebar" id="detectionsSidebar">` 检测概览侧边栏（总数、模型、设备、耗时、类别计数）。

- 页面底部：
  - `#stats` 文本状态栏，用于显示一行调试信息（尺寸、设备、耗时、检测数量等）。
  - 隐藏的 `<video id="video">` 元素作为摄像头原始画面来源。

### 6.2 样式：`style.css`

- 整体采用暗色主题，使用系统字体。 
- `.controls` 使用 flex 布局，支持自动换行。 
- `.stage` 则是一个带圆角和边框的容器，居中展示 Canvas。
- `.layout` 在大屏时左右两列，在小屏（宽度 ≤ 768px）时自动变为上下结构。
- `.sidebar` 以卡片形式展示检测汇总信息与类别计数列表。

可以尝试自行调整：

- `.container` 的最大宽度，让布局更宽或更窄；
- `.sidebar` 的高度与字体大小；
- 不同颜色方案，以熟悉 CSS 基础布局技巧。

### 6.3 核心逻辑：`app.js`

`app.js` 是前端的“控制中心”，可以 roughly 按模块理解：

1. **状态与设置管理**：
   - 一系列 `const xxx = document.getElementById(...)` 获取 DOM 节点。
   - `loadSettings` / `saveSettings`：把用户在页面上的选择保存在 `localStorage` 中，实现简单的“记忆上次设置”。
   - `applySettings`：页面加载时应用上次保存的设置。

2. **界面交互与主题**：
   - 设置面板：通过 `settingsOverlay` 的打开/关闭状态展示详细设置。
   - 侧边栏：支持折叠/展开，在小屏幕下以抽屉方式显示。
   - 主题切换：`setTheme` 切换 `data-theme` 并持久化到 `localStorage`。

3. **摄像头采集与绘制**：
   - `setupCamera`：
     - 通过 `navigator.mediaDevices.getUserMedia` 打开摄像头；
     - 把媒体流绑定到隐藏的 `<video>` 元素；
     - 将 Canvas 的宽高设置为视频宽高。
   - `draw`：
     - 使用 `requestAnimationFrame` 循环，把视频帧绘制到 Canvas；
     - 在其上叠加当前 `detections` 的可视化（调用 `drawDetections`）。

4. **推理结果渲染**：`drawDetections`
   - 对每个检测对象：
     - 根据后端返回的坐标和当前 Canvas 尺寸计算缩放比例；
     - 根据标签哈希映射到固定调色板颜色；
     - 绘制：
       - 掩膜填充（可选）
       - 边框与标签背景矩形
       - 关键点与骨架（在姿态估计任务中）

5. **通过 HTTP / WebSocket 调用后端**：
   - `sendFrame`：
     - 按设定的发送宽度（如 320/480/640）把视频帧等比例缩放；
     - 转成 JPEG Blob；
     - 若勾选 WebSocket 且连接可用，则直接 `ws.send(blob)`；
     - 否则使用 HTTP：
       - 构造 `FormData` 并调用 `POST /infer`；
       - 解包 JSON 并调用 `handleResult`。
   - `handleResult`：
     - 更新 `detections` / `lastInferSize` / `lastTask` 等前端状态；
     - 计算后端耗时与往返时间；
     - 更新 `#stats` 文本状态栏；
     - 调用 `updateSidebar` 更新右侧概览。
   - `initWS` / `closeWS`：
     - 负责建立 WebSocket 连接，将查询参数（conf、iou、max_det、device、model、imgsz、half、text_queries、question）一并附在 URL 上。

6. **本地图片上传推理：`runImageInference`**

这是在原项目基础上新增的一个扩展功能，方便你从静态图片入手理解整个数据流：

- 由 `#imageFile` 与 `#inferImage` 控件触发：
  - 点击“上传并推理”时，如果摄像头模式在运行，会先自动点击“停止”，防止相互抢占画布。
- `runImageInference(file)` 的流程：
  - 根据当前页面设置构造请求参数和 `FormData`；
  - 调用 `POST /infer`，拿到 JSON 结果；
  - 使用 `Image` 对象在 Canvas 上绘制本地图片；
  - 更新 `detections` 与 `lastInferSize` 并调用 `drawDetections` 进行可视化；
  - 统计耗时并更新 `#stats` 与右侧的 `updateSidebar`。

你可以把这个函数当作一个“最小闭环”：

1. 从本地文件读取 → 2. 发给后端 → 3. YOLO 推理 → 4. 返回 JSON → 5. 在前端画出来。

7. **检测概览与类别计数：`updateSidebar`**

- 每当推理结果更新（不论是摄像头还是本地图片），都会调用该函数。 
- 它会：
  - 统计当前 `detections` 数量；
  - 读取 `data.model`、后端耗时与往返耗时；
  - 聚合 `label -> count`，按数量从大到小排序；
  - 把信息填充到右侧侧边栏的 `summary*` 与 `classCounts` 元素中。

这是一个典型的“前端侧数据聚合 + 展示”例子，也非常适合你继续做更多可视化练习。

---

## 7. API 返回结构与数据模型

后端使用 Pydantic 模型 `InferenceResponse` 约束 `/infer` 等接口的返回结构：

- `width: int` / `height: int`：后端实际解析的图像尺寸；
- `task: "detect" | "segment" | "pose" | "caption" | "vqa"`：当前推理任务类型；
- `detections: List[Detection]`：每个检测目标（在 `caption`/`vqa` 任务中通常为空数组）；
  - `bbox: List[float]`：边界框 `[x1, y1, x2, y2]`；
  - `score: float`：置信度；
  - `label: str`：类别名；
  - `polygons?: List[List[float]]`：分割掩膜多边形坐标；
  - `keypoints?: List[List[float]]`：姿态关键点坐标；
- `caption?: str`：在 `caption` 任务中返回的图像描述文本；
- `question?: str` / `answer?: str`：在 `vqa` 任务中返回的问题与答案；
- `text_queries?: List[str]`：开放词汇检测模型的文本查询列表（用于 OWL-ViT / Grounding DINO 等）。
- `inference_time: float`：后端推理时间（毫秒）；
- `model: Optional[str]`：使用的模型名；

在前端的 `handleResult` / `runImageInference` 中，你可以找到如何消费这些字段的示例。

---

## 8. 学习路线与扩展练习建议

如果你是以本项目作为“个人学习 + 功能扩展”的练习场，下面是一个推荐路线：

### 8.1 已完成的两个基础 Step

1. **本地图片上传推理**（Step 1）
   - 目标：从单张图片贯通前后端推理流程。
   - 对应代码：前端 `runImageInference` 及相关控件。

2. **检测侧边栏 + 各类别计数**（Step 2）
   - 目标：在前端基于返回 JSON 做数据聚合与结构化展示。
   - 对应代码：`updateSidebar` 与侧边栏 DOM 结构/CSS。

### 8.2 推荐的后续扩展 Step

你可以继续按难度递增做下面几件事：

1. **本地视频文件推理**
   - 从 `<input type="file" accept="video/*">` 选择本地视频；
   - 使用 `URL.createObjectURL` 在新的 `<video>` 上播放；
   - 按设定 FPS 从视频中截帧，复用现有 `sendFrame` 流程推理与绘制。

2. **折线图 / 柱状图可视化**
   - 维护一个最近 N 帧的历史数组（检测数量、耗时等）；
   - 使用 Canvas 或简单图表库画：
     - FPS/延迟随时间变化的曲线；
     - 各类别出现频次的柱状统计图。

3. **目标轨迹与热力图**
   - 用最近几帧的 bbox 中心做最近邻匹配，给目标一个“临时 ID”；
   - 在画面上绘制轨迹线；
   - 累积中心点位置，渲染成热力图效果。

4. **RTSP / 网络视频流支持（进阶）**
   - 在后端使用 `cv2.VideoCapture(rtsp_url)` 打开远程摄像头；
   - 在后台任务中持续读取帧并推理；
   - 通过 WebSocket/MJPEG 把结果推给前端。

每个 Step 完成后，都建议你：

- 在 `docs/README.md` 中补充一小节，记录你是怎么实现的；
- 在 README 或界面中提一句这是你自己扩展的功能。

---

## 9. 如何配合本仓库的工程工具

项目已经内置了一些工程化工具，建议你在改动后经常跑：

在首次运行 `make lint` / `make test` 之前，建议先执行一次 `make dev`（安装 `requirements-dev.txt`，包含 `pytest` / `pre-commit` 等）。

- `make lint`：运行 pre-commit，执行 Ruff lint + format 检查和自动修复；
- `make test`：执行 `python -m pytest`，验证基础接口仍然正常；
- `make run`：本地开发启动 Uvicorn，调试前后端联动。

如果你增加了新的 Python 模块或测试：

- 尝试保持与现有代码风格一致（行宽、导入排序等）；
- 将对应的文件纳入测试范围；
- 根据需要在本教学文档中增加“实现记录”或“踩坑记录”。

---

## 10. 总结

YOLO-Toys 适合作为你学习以下内容的练习项目：

- 如何用 FastAPI 封装一个推理 API 与 WebSocket 服务；
- 如何集成 Ultralytics YOLOv8 并做结果后处理；
- 如何在浏览器端使用摄像头 / 本地文件与后端交互；
- 如何在 Canvas 上进行实时绘制与可视化；
- 如何通过 Docker / Makefile / pre-commit 初步工程化一个小项目。

建议你一边阅读源码，一边在 `docs/` 下不断添加属于你自己的学习笔记与扩展说明，让这个项目真正成为你的“YOLO 玩具实验场”。
