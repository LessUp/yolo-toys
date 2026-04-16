# 安装指南

本指南涵盖在你的系统上安装和设置 YOLO-Toys 的所有方法。

<p align="center">
  <a href="installation.md">English</a> •
  <a href="./">⬅ 返回入门指南</a>
</p>

---

## 📋 系统要求

### 最低要求

| 组件 | 要求 |
|------|------|
| **Python** | 3.11 或更高版本 |
| **内存** | 4 GB（建议 8 GB+）|
| **存储** | 2 GB 可用空间 |
| **操作系统** | Linux、macOS 或 Windows |

### GPU 支持（可选）

| 硬件 | 要求 |
|------|------|
| **NVIDIA** | CUDA 11.8+ 与 cuDNN |
| **Apple Silicon** | macOS 12.3+ 支持 MPS |
| **AMD** | ROCm（社区支持）|

### 浏览器要求

使用 Web 界面需要：
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- 实时检测需要摄像头访问权限

---

## 🐍 方法一：Python 原生安装（开发推荐）

### 步骤 1：克隆仓库

```bash
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys
```

### 步骤 2：创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# Linux/macOS 激活
source .venv/bin/activate

# Windows PowerShell 激活
.venv\Scripts\Activate.ps1
```

### 步骤 3：安装依赖

```bash
# 安装运行时依赖
pip install -r requirements.txt

#（可选）安装开发依赖
pip install -r requirements-dev.txt
```

### 步骤 4：配置环境

```bash
# 复制环境文件示例
cp .env.example .env

# 编辑 .env 自定义设置
# nano .env  # 或使用你喜欢的编辑器
```

### 步骤 5：验证安装

```bash
# 运行代码检查验证安装
make lint

# 运行测试
make test
```

---

## 🐳 方法二：Docker

### 前提条件

- 已安装 Docker 20.10+
- 已安装 Docker Compose 2.0+（用于 compose 方式）

### Docker 快速开始

```bash
# 克隆仓库
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys

# 复制环境文件
cp .env.example .env

# 构建并运行
docker build -t yolo-toys .
docker run -p 8000:8000 --env-file .env yolo-toys
```

### 使用 Docker Compose（生产推荐）

```bash
# 复制环境文件
cp .env.example .env

# 启动服务
docker-compose up --build -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🖥️ GPU 设置

### NVIDIA GPU (CUDA)

1. **验证 CUDA 安装**：
   ```bash
   nvidia-smi
   ```

2. **安装带 CUDA 的 PyTorch**：
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. **在 .env 中设置设备**：
   ```bash
   DEVICE=cuda:0
   ```

### Apple Silicon (MPS)

无需额外设置。系统将自动检测并在 Apple Silicon Mac 上使用 MPS 后端。

验证 MPS 是否可用：
```python
python -c "import torch; print(torch.backends.mps.is_available())"
```

---

## 🔧 故障排除

### 问题：导入时出现 `ModuleNotFoundError`

**解决方案**：确保你在虚拟环境中且所有依赖已安装：
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 问题：CUDA 内存不足

**解决方案**：使用更小的模型或减少并发请求数：
```bash
# 在 .env 中
MODEL_NAME=yolov8n.pt  # 使用 nano 模型
MAX_CONCURRENCY=2      # 减少并发数
```

### 问题：模型下载速度慢

**解决方案**：在环境中配置镜像源：
```bash
# HuggingFace 模型
export HF_ENDPOINT=https://hf-mirror.com

# PyTorch
export TORCH_HOME=/path/to/cache
```

### 问题：端口 8000 已被占用

**解决方案**：在 `.env` 中更改端口：
```bash
PORT=8080
```

---

## ✅ 下一步

YOLO-Toys 安装完成后：

1. **[快速开始](./quickstart.zh-CN.md)** — 运行第一次检测
2. **[API 参考](../api/rest-api.zh-CN.md)** — 学习 API 用法
3. **[部署指南](../deployment/docker.zh-CN.md)** — 生产环境部署

---

<div align="center">

**[⬆ 返回顶部](#安装指南)**

</div>
