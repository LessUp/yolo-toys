---
layout: default
title: Environment Variables
parent: Deployment
nav_order: 2
---

# Environment Variables Reference

Complete reference for all configuration options.

---

## 📋 Quick Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `MODEL_NAME` | `yolov8n.pt` | Default model |
| `DEVICE` | `auto` | Inference device |
| `CONF_THRESHOLD` | `0.25` | Detection confidence |
| `IOU_THRESHOLD` | `0.45` | NMS IoU threshold |
| `MAX_DET` | `300` | Max detections |
| `MAX_CONCURRENCY` | `4` | Concurrent requests |
| `SKIP_WARMUP` | `false` | Skip model warmup |

---

## 🔧 Server Configuration

### PORT

Server listening port.

```bash
PORT=8080
```

### HOST

Server bind address (Docker deployments).

```bash
HOST=0.0.0.0  # Listen on all interfaces
```

### ALLOW_ORIGINS

CORS allowed origins (comma-separated).

```bash
ALLOW_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ALLOW_ORIGINS=*  # Allow all (development only)
```

---

## 🤖 Model Configuration

### MODEL_NAME

Default model for inference.

```bash
MODEL_NAME=yolov8n.pt          # Fastest
MODEL_NAME=yolov8s.pt          # Balanced
MODEL_NAME=yolov8m.pt          # More accurate
MODEL_NAME=facebook/detr-resnet-50  # DETR
```

### DEVICE

Inference device selection.

```bash
DEVICE=auto     # Auto-detect (cuda > mps > cpu)
DEVICE=cpu      # Force CPU
DEVICE=cuda:0   # Specific GPU
DEVICE=mps      # Apple Silicon
```

### CONF_THRESHOLD

Minimum confidence for detections (0.0 - 1.0).

```bash
CONF_THRESHOLD=0.25  # Default
CONF_THRESHOLD=0.5   # Higher precision
CONF_THRESHOLD=0.1   # More detections
```

### IOU_THRESHOLD

IoU threshold for Non-Maximum Suppression.

```bash
IOU_THRESHOLD=0.45  # Default
IOU_THRESHOLD=0.3   # Stricter NMS
```

### MAX_DET

Maximum detections per image.

```bash
MAX_DET=300   # Default
MAX_DET=100   # Faster, fewer results
MAX_DET=1000  # Dense scenes
```

---

## ⚡ Performance Configuration

### MAX_CONCURRENCY

Maximum concurrent inference requests.

```bash
MAX_CONCURRENCY=4   # Default
MAX_CONCURRENCY=1   # Sequential processing
MAX_CONCURRENCY=8   # High-throughput
```

### SKIP_WARMUP

Skip model warmup on startup (faster startup, slower first request).

```bash
SKIP_WARMUP=false  # Default - warmup on startup
SKIP_WARMUP=true   # Skip warmup
```

### MAX_UPLOAD_MB

Maximum upload size in megabytes.

```bash
MAX_UPLOAD_MB=10   # Default
MAX_UPLOAD_MB=50   # Large images
```

---

## 🔒 Security Configuration

### LOG_LEVEL

Logging verbosity.

```bash
LOG_LEVEL=info   # Default
LOG_LEVEL=debug  # Detailed
LOG_LEVEL=warning  # Quiet
```

---

## 🐳 Docker-Specific

### NVIDIA_VISIBLE_DEVICES

GPU visibility for NVIDIA containers.

```bash
NVIDIA_VISIBLE_DEVICES=all     # All GPUs
NVIDIA_VISIBLE_DEVICES=0       # GPU 0 only
NVIDIA_VISIBLE_DEVICES=0,1     # GPUs 0 and 1
```

### TORCH_HOME

PyTorch cache directory.

```bash
TORCH_HOME=/app/cache/torch
```

### HF_HOME

HuggingFace cache directory.

```bash
HF_HOME=/app/cache/huggingface
```

### XDG_CACHE_HOME

General cache directory.

```bash
XDG_CACHE_HOME=/app/cache
```

---

## 📝 Example .env File

### Development

```bash
# Server
PORT=8000
ALLOW_ORIGINS=*

# Model
MODEL_NAME=yolov8n.pt
DEVICE=auto

# Performance
MAX_CONCURRENCY=4
SKIP_WARMUP=true

# Development
LOG_LEVEL=debug
```

### Production

```bash
# Server
PORT=8000
HOST=0.0.0.0
ALLOW_ORIGINS=https://yourdomain.com

# Model
MODEL_NAME=yolov8s.pt
DEVICE=auto
CONF_THRESHOLD=0.25
IOU_THRESHOLD=0.45
MAX_DET=300

# Performance
MAX_CONCURRENCY=4
SKIP_WARMUP=false
MAX_UPLOAD_MB=10

# Production
LOG_LEVEL=info
```

### GPU Server

```bash
# GPU Configuration
DEVICE=cuda:0
MODEL_NAME=yolov8m.pt

# High Performance
MAX_CONCURRENCY=8

# Cache
TORCH_HOME=/data/cache/torch
HF_HOME=/data/cache/huggingface
```

---

## 🔗 Related Documentation

- 🐳 **[Docker Deployment](./docker.md)** — Container deployment
- 🏗️ **[Architecture](../architecture/overview.md)** — System design
- 📖 **[Adding Models](../guides/adding-models.md)** — Custom model guide

---

<div align="center">

**[⬆ Back to Top](#environment-variables-reference)**

</div>
