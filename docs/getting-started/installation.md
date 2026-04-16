# Installation Guide

This guide covers all the ways to install and set up YOLO-Toys on your system.

<p align="center">
  <a href="installation.zh-CN.md">简体中文</a> •
  <a href="./">⬅ Back to Getting Started</a>
</p>

---

## 📋 System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.11 or higher |
| **RAM** | 4 GB (8 GB+ recommended) |
| **Storage** | 2 GB free space |
| **OS** | Linux, macOS, or Windows |

### GPU Support (Optional)

| Hardware | Requirements |
|----------|--------------|
| **NVIDIA** | CUDA 11.8+ with cuDNN |
| **Apple Silicon** | macOS 12.3+ with MPS support |
| **AMD** | ROCm (community supported) |

### Browser Requirements

For the web interface:
- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Camera access permission for live detection

---

## 🐍 Method 1: Python Native (Recommended for Development)

### Step 1: Clone the Repository

```bash
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on Linux/macOS
source .venv/bin/activate

# Activate on Windows PowerShell
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# (Optional) Install development dependencies
pip install -r requirements-dev.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env to customize settings
# nano .env  # or use your preferred editor
```

### Step 5: Verify Installation

```bash
# Run linting to verify setup
make lint

# Run tests
make test
```

---

## 🐳 Method 2: Docker

### Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ (for compose method)

### Quick Start with Docker

```bash
# Clone repository
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys

# Copy environment file
cp .env.example .env

# Build and run
docker build -t yolo-toys .
docker run -p 8000:8000 --env-file .env yolo-toys
```

### Using Docker Compose (Recommended for Production)

```bash
# Copy environment file
cp .env.example .env

# Start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🖥️ GPU Setup

### NVIDIA GPU (CUDA)

1. **Verify CUDA Installation**:
   ```bash
   nvidia-smi
   ```

2. **Install PyTorch with CUDA**:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Set Device in .env**:
   ```bash
   DEVICE=cuda:0
   ```

### Apple Silicon (MPS)

No additional setup required. The system will automatically detect and use MPS backend on Apple Silicon Macs.

To verify MPS is available:
```python
python -c "import torch; print(torch.backends.mps.is_available())"
```

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError` during import

**Solution**: Ensure you're in the virtual environment and all dependencies are installed:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: CUDA out of memory

**Solution**: Use a smaller model or reduce concurrent requests:
```bash
# In .env
MODEL_NAME=yolov8n.pt  # Use nano model
MAX_CONCURRENCY=2      # Reduce concurrency
```

### Issue: Model download is slow

**Solution**: Configure mirror sources in your environment:
```bash
# For HuggingFace models
export HF_ENDPOINT=https://hf-mirror.com

# For PyTorch
export TORCH_HOME=/path/to/cache
```

### Issue: Port 8000 is already in use

**Solution**: Change the port in `.env`:
```bash
PORT=8080
```

---

## ✅ Next Steps

Now that YOLO-Toys is installed:

1. **[Quick Start](./quickstart.md)** — Run your first detection
2. **[API Reference](../api/rest-api.md)** — Learn the API
3. **[Deployment Guide](../deployment/docker.md)** — Production deployment

---

<div align="center">

**[⬆ Back to Top](#installation-guide)**

</div>
