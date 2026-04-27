---
layout: default
title: 支持的模型
parent: 文档
nav_order: 20
lang: zh-CN
---

# 支持的模型参考

所有支持模型的完整列表、规格和基准测试。

---

## 📊 模型对比

### 检测模型

| 模型 | 大小 | CPU 速度 | GPU 速度 | mAP | 适用场景 |
|------|------|----------|----------|-----|----------|
| YOLOv8n | 6.2M | ~25ms | ~5ms | 37.3 | 实时、边缘设备 |
| YOLOv8s | 11.2M | ~35ms | ~6ms | 44.9 | 速度/精度平衡 |
| YOLOv8m | 25.9M | ~50ms | ~8ms | 50.2 | 更高精度 |
| YOLOv8l | 43.7M | ~80ms | ~12ms | 52.9 | 最高精度 |
| YOLOv8x | 68.2M | ~120ms | ~18ms | 53.9 | 研究、高端 GPU |

### 分割模型

| 模型 | 大小 | CPU 速度 | GPU 速度 | mAP | mask mAP |
|------|------|----------|----------|-----|----------|
| YOLOv8n-seg | 6.4M | ~45ms | ~10ms | 36.7 | 30.5 |
| YOLOv8s-seg | 11.8M | ~60ms | ~12ms | 44.6 | 36.8 |
| YOLOv8m-seg | 27.3M | ~85ms | ~15ms | 49.9 | 40.8 |

### 姿态估计模型

| 模型 | 大小 | CPU 速度 | GPU 速度 | AP@50 |
|------|------|----------|----------|-------|
| YOLOv8n-pose | 6.5M | ~40ms | ~8ms | 67.4 |
| YOLOv8s-pose | 11.6M | ~55ms | ~10ms | 77.9 |
| YOLOv8m-pose | 26.4M | ~75ms | ~14ms | 84.4 |

### Transformer 模型

| 模型 | 参数量 | GPU 速度 | mAP | 来源 |
|------|--------|----------|-----|------|
| DETR-R50 | 41M | ~25ms | 42.0 | Facebook |
| DETR-R101 | 60M | ~35ms | 43.5 | Facebook |
| OWL-ViT-B/32 | 150M | ~30ms | - | Google |

### 多模态模型

| 模型 | 任务 | 参数量 | GPU 速度 |
|------|------|--------|----------|
| BLIP-Caption-Base | 图像描述 | 400M | ~120ms |
| BLIP-VQA-Base | 视觉问答 | 400M | ~95ms |

---

## 🏷️ YOLO 模型

### YOLOv8 检测

```python
MODEL_NAME=yolov8n.pt  # Nano - 最快
MODEL_NAME=yolov8s.pt  # Small - 平衡
MODEL_NAME=yolov8m.pt  # Medium - 准确
MODEL_NAME=yolov8l.pt  # Large - 很准确
MODEL_NAME=yolov8x.pt  # XLarge - 最高精度
```

**COCO 类别 (80):**

```
人、自行车、汽车、摩托车、飞机、公交车、火车、卡车、船、
红绿灯、消防栓、停车标志、停车计时器、长椅、鸟、猫、狗、
马、羊、牛、大象、熊、斑马、长颈鹿、背包、雨伞、手提包、
领带、行李箱、飞盘、滑雪板、滑雪板、运动球、风筝、棒球棒、
棒球手套、滑板、冲浪板、网球拍、瓶子、酒杯、杯子、叉子、
刀、勺子、碗、香蕉、苹果、三明治、橙子、西兰花、胡萝卜、
热狗、披萨、甜甜圈、蛋糕、椅子、沙发、盆栽、床、餐桌、
马桶、电视、笔记本电脑、鼠标、遥控器、键盘、手机、微波炉、
烤箱、烤面包机、水槽、冰箱、书、钟、花瓶、剪刀、泰迪熊、
吹风机、牙刷
```

### YOLOv8 分割

```python
MODEL_NAME=yolov8n-seg.pt
MODEL_NAME=yolov8s-seg.pt
MODEL_NAME=yolov8m-seg.pt
```

**分割特性:**
- 每个检测对象的像素级掩码
- 与检测相同的 80 个 COCO 类别
- 比检测稍慢（约 20% 开销）

### YOLOv8 姿态

```python
MODEL_NAME=yolov8n-pose.pt
MODEL_NAME=yolov8s-pose.pt
MODEL_NAME=yolov8m-pose.pt
```

**关键点格式:** 每人 17 个关键点，遵循 COCO 格式

```python
keypoints = [
    {"x": x, "y": y, "confidence": conf},  # 0: 鼻子
    {"x": x, "y": y, "confidence": conf},  # 1: 左眼
    {"x": x, "y": y, "confidence": conf},  # 2: 右眼
    # ... (共 17 个)
]
```

---

## 🤗 HuggingFace 模型

### DETR (检测 Transformer)

```python
MODEL_NAME=facebook/detr-resnet-50
MODEL_NAME=facebook/detr-resnet-101
```

**特性:**
- 端到端目标检测
- 并行解码（比自回归更快）
- 全局注意力机制
- 对大物体效果更好

### OWL-ViT (开放词汇)

```python
MODEL_NAME=google/owlvit-base-patch32
MODEL_NAME=google/owlvit-base-patch16
```

**特性:**
- 文本引导目标检测
- 零样本检测能力
- 支持任意对象描述
- 使用 `text_queries` 参数

**示例:**
```bash
curl -X POST "http://localhost:8000/infer" \
  -F "file=@image.jpg" \
  -F "model=google/owlvit-base-patch32" \
  -F "text_queries=人, 红色汽车, 狗"
```

### Grounding DINO

```python
MODEL_NAME=IDEA-Research/grounding-dino-base
MODEL_NAME=IDEA-Research/grounding-dino-tiny
```

**特性:**
- 语言引导检测
- 强大的零样本性能
- 框阈值调节

### BLIP (图像描述)

```python
MODEL_NAME=Salesforce/blip-image-captioning-base
MODEL_NAME=Salesforce/blip-image-captioning-large
```

**特性:**
- 自动图像描述生成
- 可配置最大长度
- 视觉语言预训练

**参数:**
| 参数 | 默认值 | 范围 | 描述 |
|------|--------|------|------|
| `max_length` | 50 | 10-100 | 最大描述长度 |

### BLIP VQA

```python
MODEL_NAME=Salesforce/blip-vqa-base
MODEL_NAME=Salesforce/blip-vqa-capfilt-large
```

**特性:**
- 图像问答
- 自然语言理解
- 视觉推理

**必需参数:** `question`

---

## ⚙️ 模型配置

### 默认参数

| 模型类型 | conf | iou | max_det |
|----------|------|-----|---------|
| YOLO 检测 | 0.25 | 0.45 | 300 |
| YOLO 分割 | 0.25 | 0.45 | 300 |
| YOLO 姿态 | 0.25 | 0.45 | 300 |
| DETR | 0.50 | - | 100 |
| OWL-ViT | 0.10 | - | - |

### 推荐设置

**高精度:**
```bash
CONF_THRESHOLD=0.5
IOU_THRESHOLD=0.3
```

**高召回率:**
```bash
CONF_THRESHOLD=0.1
IOU_THRESHOLD=0.5
MAX_DET=500
```

**速度优化:**
```bash
MODEL_NAME=yolov8n.pt
CONF_THRESHOLD=0.3
MAX_DET=100
```

---

## 🌐 镜像配置

### 中国镜像

对于中国用户，配置镜像以加快下载速度:

```bash
# HuggingFace
export HF_ENDPOINT=https://hf-mirror.com

# PyTorch (在 requirements.txt 中)
--index-url https://download.pytorch.org/whl/cu118
--extra-index-url https://mirrors.aliyun.com/pypi/simple/
```

### 模型缓存

模型缓存位置:

| 框架 | 缓存位置 |
|------|----------|
| Ultralytics | `~/.ultralytics/` |
| HuggingFace | `~/.cache/huggingface/` |
| PyTorch | `~/.cache/torch/` |

更改缓存位置:

```bash
export ULTRALYTICS_CONFIG_DIR=/data/cache/ultralytics
export HF_HOME=/data/cache/huggingface
export TORCH_HOME=/data/cache/torch
```

---

## 🔗 相关文档

- 🏗️ **[Handler 模式](../architecture/handlers.zh-CN.md)** — 模型实现方式
- 🔍 **[REST API](../api/rest-api.zh-CN.md)** — API 使用
- 🚀 **[安装](../getting-started/installation.zh-CN.md)** — 设置指南

---

<div align="center">

**[⬆ 返回顶部](#支持的模型参考)**

</div>
