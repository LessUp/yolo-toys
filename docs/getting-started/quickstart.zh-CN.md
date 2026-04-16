# 快速开始指南

在 5 分钟内让 YOLO-Toys 运行起来，完成第一次目标检测。

<p align="center">
  <a href="quickstart.md">English</a> •
  <a href="./">⬅ 返回入门指南</a>
</p>

---

## 🚀 启动服务器

### Python 原生

```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # Linux/macOS

# 启动服务器并启用自动重载
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

你应该看到类似输出：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Docker

```bash
docker-compose up -d
```

---

## 🌐 访问 Web 界面

1. 打开浏览器并访问：`http://localhost:8000`

2. **授予摄像头权限**：出现提示时，允许摄像头访问以进行实时检测。

3. **选择模型**：从下拉框中选择：
   - `yolov8n.pt` — 最快，适合测试
   - `yolov8s.pt` — 速度/精度平衡
   - `yolov8m.pt` — 更高精度，较慢

4. **调整设置**（可选）：
   - **置信度**：0.25（默认）— 值越低检测越多对象
   - **IoU**：0.45 — 重叠框的 NMS 阈值
   - **最大检测数**：300 — 每帧最大对象数

5. **点击"开始检测"** 开始实时目标检测！

---

## 🔌 使用 WebSocket 流式传输

对于最低延迟的实时检测，使用 WebSocket 流式传输：

### JavaScript 示例

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?model=yolov8n.pt&conf=0.25');

ws.onopen = () => {
  console.log('WebSocket 已连接');
};

ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('检测结果:', result.detections);
  console.log('推理时间:', result.inference_time, 'ms');
};

// 发送图像帧（JPEG 二进制）
function sendFrame(imageBlob) {
  ws.send(imageBlob);
}
```

### 更新配置

你可以在不重新连接的情况下更新检测参数：

```javascript
ws.send(JSON.stringify({
  type: 'config',
  conf: 0.5,      // 新的置信度阈值
  iou: 0.4,       // 新的 IoU 阈值
  max_det: 100    // 新的最大检测数
}));
```

---

## 📡 REST API 示例

### 单图推理

使用 cURL：

```bash
curl -X POST "http://localhost:8000/infer" \
  -F "file=@image.jpg" \
  -F "model=yolov8n.pt" \
  -F "conf=0.25" \
  -F "iou=0.45"
```

使用 Python (requests)：

```python
import requests

url = "http://localhost:8000/infer"
files = {"file": open("image.jpg", "rb")}
data = {"model": "yolov8n.pt", "conf": 0.25}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"检测到 {len(result['detections'])} 个对象")
for det in result['detections']:
    print(f"  - {det['label']}: {det['score']:.2f}")
```

### 响应格式

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

### 列出可用模型

```bash
curl http://localhost:8000/models
```

### 健康检查

```bash
curl http://localhost:8000/health
```

---

## 🖼️ 图像描述（BLIP）

为图像自动生成描述：

```bash
curl -X POST "http://localhost:8000/caption" \
  -F "file=@image.jpg" \
  -F "model=Salesforce/blip-image-captioning-base"
```

响应：
```json
{
  "caption": "a person riding a skateboard on a street",
  "inference_time": 120.5
}
```

---

## ❓ 视觉问答（BLIP VQA）

针对图像提问：

```bash
curl -X POST "http://localhost:8000/vqa" \
  -F "file=@image.jpg" \
  -F "question=What color is the car?" \
  -F "model=Salesforce/blip-vqa-base"
```

---

## ✅ 接下来做什么？

- 📖 **[API 参考](../api/rest-api.zh-CN.md)** — 完整 API 文档
- 🏗️ **[架构设计](../architecture/overview.zh-CN.md)** — 理解系统设计
- 🐳 **[部署指南](../deployment/docker.zh-CN.md)** — 生产环境部署
- 📋 **[支持的模型](../reference/models.md)** — 模型规格说明

---

<div align="center">

**[⬆ 返回顶部](#快速开始指南)**

</div>
