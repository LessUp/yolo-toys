# Frequently Asked Questions (FAQ)

Common questions and troubleshooting tips.

---

## 🚀 Getting Started

### Q: What's the minimum hardware requirement?

**A:** For basic usage:
- CPU: Any modern x86_64 or ARM64 processor
- RAM: 4GB minimum, 8GB recommended
- Storage: 2GB free space
- OS: Linux, macOS, or Windows

For GPU acceleration:
- NVIDIA: GTX 1060 6GB or better
- Apple Silicon: M1 or newer

---

## 🐛 Installation Issues

### Q: Installation fails with "No matching distribution found"

**A:** Check your Python version:
```bash
python --version  # Must be 3.11+
```

If using older Python:
```bash
# Install Python 3.11
sudo apt-get install python3.11 python3.11-venv

# Create venv with correct version
python3.11 -m venv .venv
```

### Q: CUDA is available but not detected

**A:** Verify PyTorch CUDA installation:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If False, reinstall with correct CUDA version:
```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Q: Model downloads are very slow

**A:** Use mirrors if in China:
```bash
# HuggingFace
export HF_ENDPOINT=https://hf-mirror.com

# Run with mirror
HF_ENDPOINT=https://hf-mirror.com python -m uvicorn app.main:app
```

---

## ⚡ Performance

### Q: How to improve inference speed?

**A:** Try these optimizations:

1. **Use smaller model:**
   ```bash
   MODEL_NAME=yolov8n.pt  # instead of yolov8x.pt
   ```

2. **Reduce resolution:**
   ```javascript
   // Frontend: send smaller frames
   canvas.toBlob(sendFrame, 'image/jpeg', 0.7)
   ```

3. **Lower confidence threshold:**
   ```bash
   CONF_THRESHOLD=0.3  # Fewer candidates to process
   ```

4. **Reduce max detections:**
   ```bash
   MAX_DET=100  # Default is 300
   ```

5. **Enable GPU:**
   ```bash
   DEVICE=cuda:0
   ```

### Q: Out of memory errors

**A:** Reduce memory usage:

```bash
# Use smaller model
MODEL_NAME=yolov8n.pt

# Limit concurrent requests
MAX_CONCURRENCY=1

# Skip warmup (load models on first use)
SKIP_WARMUP=true
```

For Docker:
```bash
docker run -m 4g --memory-swap 4g yolo-toys
```

### Q: WebSocket disconnects frequently

**A:** Check these settings:

1. **Proxy timeout** (Nginx):
   ```nginx
   proxy_read_timeout 86400;
   proxy_send_timeout 86400;
   ```

2. **Client reconnection:**
   ```javascript
   ws.onclose = () => {
       setTimeout(reconnect, 3000);
   };
   ```

3. **Server keepalive:**
   ```bash
   # Check server load
   curl http://localhost:8000/health
   ```

---

## 🎯 Model Usage

### Q: How to detect custom objects?

**A:** Options for custom detection:

1. **Open vocabulary (OWL-ViT):**
   ```bash
   curl -X POST "http://localhost:8000/infer" \
     -F "model=google/owlvit-base-patch32" \
     -F "file=@image.jpg" \
     -F "text_queries=your custom object"
   ```

2. **Fine-tune YOLO:**
   Train custom model with Ultralytics:
   ```bash
   yolo detect train data=custom.yaml model=yolov8n.pt
   ```

3. **Add custom handler:**
   See [Adding Custom Models](../guides/adding-models.md)

### Q: How to get segmentation masks?

**A:** Use YOLO-seg models:

```bash
MODEL_NAME=yolov8n-seg.pt
```

Response includes `polygons` field:
```json
{
  "detections": [{
    "bbox": [x1, y1, x2, y2],
    "polygons": [[[x1, y1], [x2, y2], ...]]
  }]
}
```

### Q: Can I use multiple models simultaneously?

**A:** Yes! Each request can specify a different model:

```javascript
// Request 1: Detection
const ws1 = new WebSocket('ws://localhost:8000/ws?model=yolov8n.pt');

// Request 2: Segmentation
const ws2 = new WebSocket('ws://localhost:8000/ws?model=yolov8n-seg.pt');

// Request 3: VQA
fetch('/vqa', {body: formDataWithVQA});
```

Models are cached automatically after first load.

---

## 🔌 API Questions

### Q: Maximum image size?

**A:** Default limit is 10MB. Configure in `.env`:

```bash
MAX_UPLOAD_MB=50  # Increase to 50MB
```

Or set unlimited:
```bash
MAX_UPLOAD_MB=0
```

### Q: Supported image formats?

**A:** JPEG, PNG, and WEBP are supported.

For best performance:
- **Photos:** JPEG with 85% quality
- **Screenshots:** PNG for text/UI
- **Web:** WEBP for modern browsers

### Q: How to batch process images?

**A:** Current API is single-image per request. For batch processing:

```python
import requests
import concurrent.futures

def process_image(path):
    with open(path, 'rb') as f:
        return requests.post('http://localhost:8000/infer',
                           files={'file': f}).json()

# Process 10 images concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_image, image_paths))
```

---

## 🐳 Docker

### Q: How to persist model cache?

**A:** Mount a volume:

```yaml
# docker-compose.yml
volumes:
  - model-cache:/root/.cache

volumes:
  model-cache:
    driver: local
```

Or pre-download models:
```bash
mkdir -p cache
docker run -v $(pwd)/cache:/root/.cache yolo-toys python -c \
  "from app.model_manager import ModelManager; \
   ModelManager().load_model('yolov8n.pt')"
```

### Q: Port already in use

**A:** Change the port mapping:

```bash
docker run -p 8080:8000 yolo-toys  # Host 8080 → Container 8000
```

Or in docker-compose.yml:
```yaml
ports:
  - "8080:8000"
```

---

## 🤝 Contributing

### Q: How to contribute a new model?

**A:** See detailed guide: [Adding Custom Models](../guides/adding-models.md)

Quick summary:
1. Create handler in `app/handlers/`
2. Register in `registry.py`
3. Add tests in `tests/`
4. Submit PR

### Q: Code style requirements?

**A:** We use Ruff for linting:

```bash
make lint    # Check code
make format  # Auto-fix issues
```

- Line length: 100 characters
- Python 3.11+ type hints required
- Follow existing patterns

---

## 🔗 Still Need Help?

- 📖 [Documentation](../README.md)
- 🐛 [GitHub Issues](https://github.com/LessUp/yolo-toys/issues)
- 💬 [Discussions](https://github.com/LessUp/yolo-toys/discussions)

---

<div align="center">

**[⬆ Back to Top](#frequently-asked-questions-faq)**

</div>
