# Supported Models Reference

Complete list of all supported models with specifications and benchmarks.

---

## 📊 Model Comparison

### Detection Models

| Model | Size | Speed (CPU) | Speed (GPU) | mAP | Best For |
|-------|------|-------------|-------------|-----|----------|
| YOLOv8n | 6.2M | ~25ms | ~5ms | 37.3 | Real-time, edge devices |
| YOLOv8s | 11.2M | ~35ms | ~6ms | 44.9 | Balanced speed/accuracy |
| YOLOv8m | 25.9M | ~50ms | ~8ms | 50.2 | Higher accuracy |
| YOLOv8l | 43.7M | ~80ms | ~12ms | 52.9 | Maximum accuracy |
| YOLOv8x | 68.2M | ~120ms | ~18ms | 53.9 | Research, high-end GPU |

### Segmentation Models

| Model | Size | Speed (CPU) | Speed (GPU) | mAP | mask mAP |
|-------|------|-------------|-------------|-----|----------|
| YOLOv8n-seg | 6.4M | ~45ms | ~10ms | 36.7 | 30.5 |
| YOLOv8s-seg | 11.8M | ~60ms | ~12ms | 44.6 | 36.8 |
| YOLOv8m-seg | 27.3M | ~85ms | ~15ms | 49.9 | 40.8 |

### Pose Estimation Models

| Model | Size | Speed (CPU) | Speed (GPU) | AP@50 |
|-------|------|-------------|-------------|-------|
| YOLOv8n-pose | 6.5M | ~40ms | ~8ms | 67.4 |
| YOLOv8s-pose | 11.6M | ~55ms | ~10ms | 77.9 |
| YOLOv8m-pose | 26.4M | ~75ms | ~14ms | 84.4 |

### Transformer Models

| Model | Parameters | Speed (GPU) | mAP | Source |
|-------|------------|-------------|-----|--------|
| DETR-R50 | 41M | ~25ms | 42.0 | Facebook |
| DETR-R101 | 60M | ~35ms | 43.5 | Facebook |
| OWL-ViT-B/32 | 150M | ~30ms | - | Google |

### Multimodal Models

| Model | Task | Parameters | Speed (GPU) |
|-------|------|------------|-------------|
| BLIP-Caption-Base | Image Captioning | 400M | ~120ms |
| BLIP-VQA-Base | Visual QA | 400M | ~95ms |

---

## 🏷️ YOLO Models

### YOLOv8 Detection

```python
MODEL_NAME=yolov8n.pt  # Nano - fastest
MODEL_NAME=yolov8s.pt  # Small - balanced
MODEL_NAME=yolov8m.pt  # Medium - accurate
MODEL_NAME=yolov8l.pt  # Large - very accurate
MODEL_NAME=yolov8x.pt  # XLarge - max accuracy
```

**COCO Classes (80):**

```
person, bicycle, car, motorcycle, airplane, bus, train, truck, boat,
traffic light, fire hydrant, stop sign, parking meter, bench, bird,
cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack,
umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball,
kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket,
bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich,
orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted
plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard,
cell phone, microwave, oven, toaster, sink, refrigerator, book, clock,
vase, scissors, teddy bear, hair drier, toothbrush
```

### YOLOv8 Segmentation

```python
MODEL_NAME=yolov8n-seg.pt
MODEL_NAME=yolov8s-seg.pt
MODEL_NAME=yolov8m-seg.pt
```

**Segmentation Features:**
- Pixel-level masks for each detected object
- Same 80 COCO classes as detection
- Slightly slower than detection (~20% overhead)

### YOLOv8 Pose

```python
MODEL_NAME=yolov8n-pose.pt
MODEL_NAME=yolov8s-pose.pt
MODEL_NAME=yolov8m-pose.pt
```

**Keypoint Format:** 17 keypoints per person following COCO format

```python
keypoints = [
    {"x": x, "y": y, "confidence": conf},  # 0: nose
    {"x": x, "y": y, "confidence": conf},  # 1: left eye
    {"x": x, "y": y, "confidence": conf},  # 2: right eye
    # ... (17 total)
]
```

---

## 🤗 HuggingFace Models

### DETR (Detection Transformer)

```python
MODEL_NAME=facebook/detr-resnet-50
MODEL_NAME=facebook/detr-resnet-101
```

**Features:**
- End-to-end object detection
- Parallel decoding (faster than autoregressive)
- Global attention mechanism
- Better on large objects

### OWL-ViT (Open Vocabulary)

```python
MODEL_NAME=google/owlvit-base-patch32
MODEL_NAME=google/owlvit-base-patch16
```

**Features:**
- Text-guided object detection
- Zero-shot detection capability
- Supports arbitrary object descriptions
- Use with `text_queries` parameter

**Example:**
```bash
curl -X POST "http://localhost:8000/infer" \
  -F "file=@image.jpg" \
  -F "model=google/owlvit-base-patch32" \
  -F "text_queries=person, red car, dog"
```

### Grounding DINO

```python
MODEL_NAME=IDEA-Research/grounding-dino-base
MODEL_NAME=IDEA-Research/grounding-dino-tiny
```

**Features:**
- Language-guided detection
- Strong zero-shot performance
- Box threshold tuning

### BLIP (Image Captioning)

```python
MODEL_NAME=Salesforce/blip-image-captioning-base
MODEL_NAME=Salesforce/blip-image-captioning-large
```

**Features:**
- Automatic image description generation
- Configurable max length
- Vision-language pre-training

**Parameters:**
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `max_length` | 50 | 10-100 | Maximum caption length |

### BLIP VQA

```python
MODEL_NAME=Salesforce/blip-vqa-base
MODEL_NAME=Salesforce/blip-vqa-capfilt-large
```

**Features:**
- Answer questions about images
- Natural language understanding
- Visual reasoning

**Required Parameter:** `question`

---

## ⚙️ Model Configuration

### Default Parameters

| Model Type | conf | iou | max_det |
|------------|------|-----|---------|
| YOLO Detection | 0.25 | 0.45 | 300 |
| YOLO Segmentation | 0.25 | 0.45 | 300 |
| YOLO Pose | 0.25 | 0.45 | 300 |
| DETR | 0.50 | - | 100 |
| OWL-ViT | 0.10 | - | - |

### Recommended Settings

**High Precision:**
```bash
CONF_THRESHOLD=0.5
IOU_THRESHOLD=0.3
```

**High Recall:**
```bash
CONF_THRESHOLD=0.1
IOU_THRESHOLD=0.5
MAX_DET=500
```

**Speed Optimized:**
```bash
MODEL_NAME=yolov8n.pt
CONF_THRESHOLD=0.3
MAX_DET=100
```

---

## 🌐 Mirror Configuration

### China Mirrors

For users in China, configure mirrors for faster downloads:

```bash
# HuggingFace
export HF_ENDPOINT=https://hf-mirror.com

# PyTorch (in requirements.txt)
--index-url https://download.pytorch.org/whl/cu118
--extra-index-url https://mirrors.aliyun.com/pypi/simple/
```

### Model Cache

Models are cached at:

| Framework | Cache Location |
|-----------|----------------|
| Ultralytics | `~/.ultralytics/` |
| HuggingFace | `~/.cache/huggingface/` |
| PyTorch | `~/.cache/torch/` |

Change cache location:

```bash
export ULTRALYTICS_CONFIG_DIR=/data/cache/ultralytics
export HF_HOME=/data/cache/huggingface
export TORCH_HOME=/data/cache/torch
```

---

## 📥 Model Formats

### Supported Input Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| JPEG | .jpg, .jpeg | Recommended for photos |
| PNG | .png | Good for diagrams/screenshots |
| WEBP | .webp | Modern format, smaller size |

### Input Requirements

- **Min Resolution:** 32x32
- **Max Resolution:** 4096x4096
- **Max File Size:** 10MB (configurable)
- **Color Space:** RGB (auto-converted from BGR)

---

## 🔗 Related Documentation

- 🏗️ **[Handler Pattern](../architecture/handlers.md)** — How models are implemented
- 🔍 **[REST API](../api/rest-api.md)** — API usage
- 🚀 **[Installation](../getting-started/installation.md)** — Setup guide

---

<div align="center">

**[⬆ Back to Top](#supported-models-reference)**

</div>
