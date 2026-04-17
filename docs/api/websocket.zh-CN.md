# WebSocket 协议

用于低延迟实时目标检测的流式传输协议。

<p align="center">
  <a href="websocket.md">English</a> •
  <a href="./">⬅ 返回 API 参考</a>
</p>

---

## 📋 概述

WebSocket 连接为实时视频分析提供最低延迟。二进制图像帧发送到服务器，JSON 检测结果返回。

**端点：** `ws://localhost:8000/ws`

---

## 🔌 连接

### URL 格式

```
ws://{host}/ws?model={model_id}&conf={confidence}&iou={iou}&max_det={max_detections}
```

### 查询参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `model` | string | `yolov8n.pt` | 模型标识符 |
| `conf` | float | 0.25 | 置信度阈值 (0.0 - 1.0) |
| `iou` | float | 0.45 | NMS 的 IoU 阈值 |
| `max_det` | int | 300 | 每帧最大检测数 |
| `device` | string | auto | 推理设备 (cpu/cuda/mps) |
| `imgsz` | int | 640 | 推理图像尺寸 |
| `half` | bool | false | 启用 FP16 半精度 |
| `text_queries` | string | - | 开放词汇检测的文本查询（逗号分隔）|
| `question` | string | - | VQA 模型的问题 |

### 连接示例

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?model=yolov8n.pt&conf=0.25');
```

---

## 📤 客户端 → 服务器消息

### 二进制图像帧

发送 JPEG 编码图像作为二进制消息：

```javascript
// 从 canvas 捕获
canvas.toBlob((blob) => {
  ws.send(blob);
}, 'image/jpeg', 0.85);
```

**要求：**
- 格式：JPEG
- 分辨率：任意（640x480 推荐作为平衡）
- 质量：0.85 推荐
- 最大大小：10MB

### 配置更新

无需重新连接即可更新检测参数：

```javascript
ws.send(JSON.stringify({
  type: 'config',
  conf: 0.5,
  iou: 0.4,
  max_det: 100,
  model: 'yolov8s.pt'  // 可选：切换模型
}));
```

**配置字段：**

| 字段 | 类型 | 描述 |
|------|------|------|
| `type` | string | 必须是 `"config"` |
| `conf` | float | 新置信度阈值 (0.0-1.0) |
| `iou` | float | 新 IoU 阈值 (0.0-1.0) |
| `max_det` | int | 新最大检测数限制 |
| `model` | string |（可选）切换到不同模型 |
| `device` | string |（可选）更改推理设备 |
| `imgsz` | int |（可选）更改推理图像尺寸 |
| `half` | bool |（可选）启用/禁用 FP16 |
| `text_queries` | string/array |（可选）开放词汇检测的文本查询 |
| `question` | string |（可选）VQA 模型的问题 |

---

## 📥 服务器 → 客户端消息

### 就绪消息

WebSocket 连接建立后立即发送：

```json
{
  "type": "ready",
  "message": "connected",
  "model": "yolov8n.pt",
  "device": "cuda:0"
}
```

### 检测结果

```json
{
  "type": "result",
  "data": {
    "width": 640,
    "height": 480,
    "task": "detect",
    "detections": [
      {
        "bbox": [100.5, 200.3, 250.8, 450.2],
        "score": 0.89,
        "label": "person"
      }
    ],
    "inference_time": 12.5,
    "model": "yolov8n.pt",
    "timestamp": "2026-04-16T10:30:00.000Z"
  }
}
```

### 错误消息

```json
{
  "type": "error",
  "detail": "Model inference failed"
}
```

**常见错误消息：**
| 详情 | 描述 |
|------|------|
| `file too large` | 图像超出 MAX_UPLOAD_MB 限制 |
| `failed to decode image` | 无效图像格式或损坏数据 |
| `Unknown model category for ...` | 模型 ID 无法识别 |

### 配置确认

```json
{
  "type": "config_updated",
  "model": "yolov8s.pt"
}
```

---

## 💻 完整示例

### JavaScript 客户端

```javascript
class DetectionStream {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.setupHandlers();
    this.frameCount = 0;
    this.lastFpsTime = performance.now();
  }

  setupHandlers() {
    this.ws.onopen = () => {
      console.log('WebSocket 已连接');
      this.onConnect?.();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket 错误:', error);
      this.onError?.(error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket 已关闭');
      this.onDisconnect?.();
      // 3 秒后自动重连
      setTimeout(() => this.reconnect(), 3000);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'ready':
        console.log('已连接, 模型:', message.model, '设备:', message.device);
        break;
      case 'result':
        this.onDetection?.(message.data);
        this.updateFps();
        break;
      case 'error':
        console.error('服务器错误:', message.detail);
        break;
      case 'config_updated':
        console.log('配置已更新, 模型:', message.model);
        break;
    }
  }

  sendFrame(imageBlob) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(imageBlob);
    }
  }

  updateConfig(config) {
    this.ws.send(JSON.stringify({
      type: 'config',
      ...config
    }));
  }

  updateFps() {
    this.frameCount++;
    const now = performance.now();
    if (now - this.lastFpsTime >= 1000) {
      const fps = this.frameCount;
      this.frameCount = 0;
      this.lastFpsTime = now;
      this.onFpsUpdate?.(fps);
    }
  }

  reconnect() {
    console.log('重新连接中...');
    this.ws = new WebSocket(this.ws.url);
    this.setupHandlers();
  }

  close() {
    this.ws.close();
  }
}

// 使用
const stream = new DetectionStream('ws://localhost:8000/ws?model=yolov8n.pt');

stream.onConnect = () => {
  console.log('已连接到检测服务器');
};

stream.onDetection = (data) => {
  console.log(`检测到 ${data.detections.length} 个对象，耗时 ${data.inference_time}ms`);
  // 在 canvas 上渲染检测...
};

stream.onFpsUpdate = (fps) => {
  document.getElementById('fps').textContent = `${fps} FPS`;
};

// 从视频元素发送帧
function sendVideoFrame() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0);

  canvas.toBlob((blob) => {
    stream.sendFrame(blob);
  }, 'image/jpeg', 0.85);

  requestAnimationFrame(sendVideoFrame);
}
```

---

## ⚡ 性能优化建议

### 1. 优化图像大小

```javascript
// 发送前调整大小以获得更好性能
const MAX_WIDTH = 640;
const scale = Math.min(1, MAX_WIDTH / video.videoWidth);
const width = video.videoWidth * scale;
const height = video.videoHeight * scale;
```

### 2. 降低 JPEG 质量

```javascript
// 较低质量 = 较小负载 = 更快传输
canvas.toBlob((blob) => {
  stream.sendFrame(blob);
}, 'image/jpeg', 0.7);  // 尝试 0.7 以获得更快流式传输
```

### 3. 帧跳过

```javascript
// 跳过帧以保持目标 FPS
const TARGET_FPS = 15;
const SKIP_EVERY = Math.round(30 / TARGET_FPS);  // 对于 30fps 摄像头

let frameCounter = 0;
function onVideoFrame() {
  frameCounter++;
  if (frameCounter % SKIP_EVERY !== 0) return;
  // 发送帧...
}
```

### 4. 连接池

对于多个摄像头，创建单独的 WebSocket 连接：

```javascript
const streams = cameras.map(cam =>
  new DetectionStream(`ws://localhost:8000/ws?model=${cam.model}`)
);
```

---

## 🔒 安全注意事项

### CORS

在环境中配置允许的源：

```bash
ALLOW_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 速率限制

`MAX_CONCURRENCY` 控制最大并发连接数：

```bash
MAX_CONCURRENCY=4  # 默认值
```

### 认证（未来）

将支持基于令牌的认证：

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN');
```

---

## 🔗 相关文档

- 🔍 **[REST API](./rest-api.zh-CN.md)** — HTTP 接口参考
- 🏗️ **[架构设计](../architecture/overview.zh-CN.md)** — 系统设计
- 📋 **[模型列表](../reference/models.md)** — 支持的模型列表

---

<div align="center">

**[⬆ 返回顶部](#websocket-协议)**

</div>
