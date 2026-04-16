# 常见问题 (FAQ)

常见问题解答和故障排除技巧。

---

## 🚀 入门

### Q: 最低硬件要求是什么？

**A:** 基础使用：
- CPU: 任何现代 x86_64 或 ARM64 处理器
- 内存: 4GB 最低，8GB 推荐
- 存储: 2GB 空闲空间
- 系统: Linux、macOS 或 Windows

GPU 加速：
- NVIDIA: GTX 1060 6GB 或更好
- Apple Silicon: M1 或更新

---

## 🐛 安装问题

### Q: 安装失败，提示 "No matching distribution found"

**A:** 检查 Python 版本：
```bash
python --version  # 必须是 3.11+
```

如果使用较旧 Python：
```bash
# 安装 Python 3.11
sudo apt-get install python3.11 python3.11-venv

# 使用正确版本创建 venv
python3.11 -m venv .venv
```

### Q: CUDA 可用但未检测到

**A:** 验证 PyTorch CUDA 安装：

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

如果为 False，重新安装正确 CUDA 版本：
```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Q: 模型下载非常慢

**A:** 如在中国使用镜像：
```bash
# HuggingFace
export HF_ENDPOINT=https://hf-mirror.com

# 使用镜像运行
HF_ENDPOINT=https://hf-mirror.com python -m uvicorn app.main:app
```

---

## ⚡ 性能

### Q: 如何提高推理速度？

**A:** 尝试这些优化：

1. **使用更小模型：**
   ```bash
   MODEL_NAME=yolov8n.pt  # 替代 yolov8x.pt
   ```

2. **降低分辨率：**
   ```javascript
   // 前端：发送更小的帧
   canvas.toBlob(sendFrame, 'image/jpeg', 0.7)
   ```

3. **降低置信度阈值：**
   ```bash
   CONF_THRESHOLD=0.3  # 处理的候选框更少
   ```

4. **减少最大检测数：**
   ```bash
   MAX_DET=100  # 默认是 300
   ```

5. **启用 GPU：**
   ```bash
   DEVICE=cuda:0
   ```

### Q: 内存不足错误

**A:** 减少内存使用：

```bash
# 使用更小模型
MODEL_NAME=yolov8n.pt

# 限制并发请求
MAX_CONCURRENCY=1

# 跳过预热（首次使用时加载模型）
SKIP_WARMUP=true
```

Docker 环境：
```bash
docker run -m 4g --memory-swap 4g yolo-toys
```

### Q: WebSocket 频繁断开

**A:** 检查这些设置：

1. **代理超时** (Nginx)：
   ```nginx
   proxy_read_timeout 86400;
   proxy_send_timeout 86400;
   ```

2. **客户端重连：**
   ```javascript
   ws.onclose = () => {
       setTimeout(reconnect, 3000);
   };
   ```

3. **服务器保活：**
   ```bash
   # 检查服务器负载
   curl http://localhost:8000/health
   ```

---

## 🎯 模型使用

### Q: 如何检测自定义对象？

**A:** 自定义检测的选项：

1. **开放词汇 (OWL-ViT)：**
   ```bash
   curl -X POST "http://localhost:8000/infer" \
     -F "model=google/owlvit-base-patch32" \
     -F "file=@image.jpg" \
     -F "text_queries=你的自定义对象"
   ```

2. **微调 YOLO：**
   使用 Ultralytics 训练自定义模型：
   ```bash
   yolo detect train data=custom.yaml model=yolov8n.pt
   ```

3. **添加自定义处理器：**
   见 [添加自定义模型](../guides/adding-models.zh-CN.md)

### Q: 如何获取分割掩膜？

**A:** 使用 YOLO-seg 模型：

```bash
MODEL_NAME=yolov8n-seg.pt
```

响应包含 `polygons` 字段：
```json
{
  "detections": [{
    "bbox": [x1, y1, x2, y2],
    "polygons": [[[x1, y1], [x2, y2], ...]]
  }]
}
```

### Q: 可以同时使用多个模型吗？

**A:** 可以！每个请求可以指定不同模型：

```javascript
// 请求 1：检测
const ws1 = new WebSocket('ws://localhost:8000/ws?model=yolov8n.pt');

// 请求 2：分割
const ws2 = new WebSocket('ws://localhost:8000/ws?model=yolov8n-seg.pt');

// 请求 3：VQA
fetch('/vqa', {body: formDataWithVQA});
```

模型首次加载后自动缓存。

---

## 🔌 API 问题

### Q: 最大图像大小？

**A:** 默认限制 10MB。在 `.env` 中配置：

```bash
MAX_UPLOAD_MB=50  # 增加到 50MB
```

或不限：
```bash
MAX_UPLOAD_MB=0
```

### Q: 支持的图像格式？

**A:** 支持 JPEG、PNG 和 WEBP。

最佳性能：
- **照片：** 85% 质量的 JPEG
- **截图：** PNG 用于文字/UI
- **Web：** WEBP 用于现代浏览器

### Q: 如何批处理图像？

**A:** 当前 API 每次请求单张图像。批处理：

```python
import requests
import concurrent.futures

def process_image(path):
    with open(path, 'rb') as f:
        return requests.post('http://localhost:8000/infer', 
                           files={'file': f}).json()

# 并发处理 10 张图像
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_image, image_paths))
```

---

## 🐳 Docker

### Q: 如何持久化模型缓存？

**A:** 挂载卷：

```yaml
# docker-compose.yml
volumes:
  - model-cache:/root/.cache

volumes:
  model-cache:
    driver: local
```

或预下载模型：
```bash
mkdir -p cache
docker run -v $(pwd)/cache:/root/.cache yolo-toys python -c \
  "from app.model_manager import ModelManager; \
   ModelManager().load_model('yolov8n.pt')"
```

### Q: 端口已被占用

**A:** 更改端口映射：

```bash
docker run -p 8080:8000 yolo-toys  # 主机 8080 → 容器 8000
```

或在 docker-compose.yml：
```yaml
ports:
  - "8080:8000"
```

---

## 🤝 贡献

### Q: 如何贡献新模型？

**A:** 见详细指南：[添加自定义模型](../guides/adding-models.zh-CN.md)

快速摘要：
1. 在 `app/handlers/` 创建处理器
2. 在 `registry.py` 注册
3. 在 `tests/` 添加测试
4. 提交 PR

### Q: 代码风格要求？

**A:** 我们使用 Ruff 进行代码检查：

```bash
make lint    # 检查代码
make format  # 自动修复问题
```

- 行长度：100 字符
- 需要 Python 3.11+ 类型提示
- 遵循现有模式

---

## 🔗 还需要帮助？

- 📖 [文档](../README.zh-CN.md)
- 🐛 [GitHub Issues](https://github.com/LessUp/yolo-toys/issues)
- 💬 [Discussions](https://github.com/LessUp/yolo-toys/discussions)

---

<div align="center">

**[⬆ 返回顶部](#常见问题-faq)**

</div>
