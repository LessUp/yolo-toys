---
layout: default
title: 环境变量
parent: 部署
nav_order: 2
lang: zh-CN
---

# 环境变量参考

所有配置选项的完整参考。

---

## 📋 快速参考

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `PORT` | `8000` | 服务端口 |
| `MODEL_NAME` | `yolov8n.pt` | 默认模型 |
| `DEVICE` | `auto` | 推理设备 |
| `CONF_THRESHOLD` | `0.25` | 检测置信度 |
| `IOU_THRESHOLD` | `0.45` | NMS IoU 阈值 |
| `MAX_DET` | `300` | 最大检测数 |
| `MAX_CONCURRENCY` | `4` | 并发请求数 |
| `SKIP_WARMUP` | `false` | 跳过模型预热 |

---

## 🔧 服务配置

### PORT

服务监听端口。

```bash
PORT=8080
```

### HOST

服务绑定地址（Docker 部署）。

```bash
HOST=0.0.0.0  # 监听所有接口
```

### ALLOW_ORIGINS

CORS 允许的源（逗号分隔）。

```bash
ALLOW_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ALLOW_ORIGINS=*  # 允许所有（仅开发环境）
```

---

## 🤖 模型配置

### MODEL_NAME

推理默认模型。

```bash
MODEL_NAME=yolov8n.pt          # 最快
MODEL_NAME=yolov8s.pt          # 平衡
MODEL_NAME=yolov8m.pt          # 更准确
MODEL_NAME=facebook/detr-resnet-50  # DETR
```

### DEVICE

推理设备选择。

```bash
DEVICE=auto     # 自动检测 (cuda > mps > cpu)
DEVICE=cpu      # 强制 CPU
DEVICE=cuda:0   # 指定 GPU
DEVICE=mps      # Apple Silicon
```

### CONF_THRESHOLD

检测最小置信度 (0.0 - 1.0)。

```bash
CONF_THRESHOLD=0.25  # 默认
CONF_THRESHOLD=0.5   # 更高精度
CONF_THRESHOLD=0.1   # 更多检测
```

### IOU_THRESHOLD

非极大值抑制的 IoU 阈值。

```bash
IOU_THRESHOLD=0.45  # 默认
IOU_THRESHOLD=0.3   # 更严格的 NMS
```

### MAX_DET

每张图片最大检测数。

```bash
MAX_DET=300   # 默认
MAX_DET=100   # 更快，结果更少
MAX_DET=1000  # 密集场景
```

---

## ⚡ 性能配置

### MAX_CONCURRENCY

最大并发推理请求数。

```bash
MAX_CONCURRENCY=4   # 默认
MAX_CONCURRENCY=1   # 顺序处理
MAX_CONCURRENCY=8   # 高吞吐量
```

### SKIP_WARMUP

启动时跳过模型预热（启动更快，首次请求较慢）。

```bash
SKIP_WARMUP=false  # 默认 - 启动时预热
SKIP_WARMUP=true   # 跳过预热
```

### MAX_UPLOAD_MB

上传文件最大大小（MB）。

```bash
MAX_UPLOAD_MB=10   # 默认
MAX_UPLOAD_MB=50   # 大图片
```

---

## 🔒 安全配置

### LOG_LEVEL

日志详细程度。

```bash
LOG_LEVEL=info   # 默认
LOG_LEVEL=debug  # 详细
LOG_LEVEL=warning  # 安静
```

---

## 🐳 Docker 专用

### NVIDIA_VISIBLE_DEVICES

NVIDIA 容器的 GPU 可见性。

```bash
NVIDIA_VISIBLE_DEVICES=all     # 所有 GPU
NVIDIA_VISIBLE_DEVICES=0       # 仅 GPU 0
NVIDIA_VISIBLE_DEVICES=0,1     # GPU 0 和 1
```

### TORCH_HOME

PyTorch 缓存目录。

```bash
TORCH_HOME=/app/cache/torch
```

### HF_HOME

HuggingFace 缓存目录。

```bash
HF_HOME=/app/cache/huggingface
```

---

## 📝 示例 .env 文件

### 开发环境

```bash
# 服务
PORT=8000
ALLOW_ORIGINS=*

# 模型
MODEL_NAME=yolov8n.pt
DEVICE=auto

# 性能
MAX_CONCURRENCY=4
SKIP_WARMUP=true

# 开发
LOG_LEVEL=debug
```

### 生产环境

```bash
# 服务
PORT=8000
HOST=0.0.0.0
ALLOW_ORIGINS=https://yourdomain.com

# 模型
MODEL_NAME=yolov8s.pt
DEVICE=auto
CONF_THRESHOLD=0.25
IOU_THRESHOLD=0.45
MAX_DET=300

# 性能
MAX_CONCURRENCY=4
SKIP_WARMUP=false
MAX_UPLOAD_MB=10

# 生产
LOG_LEVEL=info
```

### GPU 服务器

```bash
# GPU 配置
DEVICE=cuda:0
MODEL_NAME=yolov8m.pt

# 高性能
MAX_CONCURRENCY=8

# 缓存
TORCH_HOME=/data/cache/torch
HF_HOME=/data/cache/huggingface
```

---

## 🔗 相关文档

- 🐳 **[Docker 部署](./docker.zh-CN.md)** — 容器部署
- 🏗️ **[架构](../architecture/overview.zh-CN.md)** — 系统设计
- 📖 **[添加模型](../guides/adding-models.zh-CN.md)** — 自定义模型指南

---

<div align="center">

**[⬆ 返回顶部](#环境变量参考)**

</div>
