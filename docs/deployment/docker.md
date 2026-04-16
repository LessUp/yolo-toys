# Docker Deployment

Deploy YOLO-Toys using Docker containers.

<p align="center">
  <a href="docker.zh-CN.md">简体中文</a> •
  <a href="./">⬅ Back to Deployment</a>
</p>

---

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+ (optional, for compose deployment)
- 4GB+ available RAM
- 2GB+ free disk space

---

## 🚀 Quick Start

### Using Docker Run

```bash
# Clone repository
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys

# Copy environment configuration
cp .env.example .env

# Build image
docker build -t yolo-toys .

# Run container
docker run -d \
  --name yolo-toys \
  -p 8000:8000 \
  --env-file .env \
  -v model-cache:/root/.cache \
  yolo-toys
```

### Using Docker Compose (Recommended)

```bash
# Clone and configure
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys
cp .env.example .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🐳 Dockerfile Reference

### Multi-Stage Build

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY app/ ./app/
COPY frontend/ ./frontend/

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Benefits:**
- Smaller final image size
- No build dependencies in runtime
- Faster deployments

---

## ⚙️ docker-compose.yml Reference

```yaml
services:
  yolo-toys:
    build: .
    container_name: yolo-toys
    ports:
      - "8000:8000"
    environment:
      - MODEL_NAME=yolov8n.pt
      - DEVICE=cpu
      - MAX_CONCURRENCY=4
      - SKIP_WARMUP=false
    volumes:
      - model-cache:/root/.cache
      - ./.env:/app/.env:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  model-cache:
    driver: local
```

### Options Explained

| Option | Description |
|--------|-------------|
| `build: .` | Build from local Dockerfile |
| `ports` | Map host:container ports |
| `environment` | Environment variables |
| `volumes` | Persistent storage mounts |
| `restart` | Auto-restart policy |
| `healthcheck` | Container health monitoring |

---

## 🖥️ GPU Support

### NVIDIA GPU (CUDA)

#### docker-compose.yml with GPU

```yaml
services:
  yolo-toys:
    build: .
    runtime: nvidia  # Use NVIDIA Container Runtime
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - DEVICE=cuda:0
    # ... other options
```

#### Docker Run with GPU

```bash
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -e DEVICE=cuda:0 \
  yolo-toys
```

#### Prerequisites

1. Install NVIDIA Container Toolkit:
```bash
# On Ubuntu
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

2. Verify GPU support:
```bash
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi
```

### Apple Silicon (MPS)

Docker Desktop for Mac does not support GPU passthrough for Apple Silicon. Use native Python installation for MPS support.

---

## 🔧 Production Deployment

### Environment Variables

Create a `.env` file for production:

```bash
# Server Configuration
PORT=8000
ALLOW_ORIGINS=https://yourdomain.com

# Model Configuration
MODEL_NAME=yolov8s.pt
CONF_THRESHOLD=0.25
IOU_THRESHOLD=0.45
MAX_DET=300
DEVICE=auto

# Performance
MAX_CONCURRENCY=4
SKIP_WARMUP=false

# Optional: Set model cache path
TORCH_HOME=/app/cache/torch
HF_HOME=/app/cache/huggingface
```

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/yolo-toys
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }
}
```

### SSL with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

---

## 📊 Monitoring

### Health Checks

```bash
# Check container health
docker ps

# View health status
docker inspect --format='{{.State.Health.Status}}' yolo-toys

# Manual health check
curl http://localhost:8000/health
```

### Logs

```bash
# View live logs
docker logs -f yolo-toys

# View last 100 lines
docker logs --tail 100 yolo-toys

# View logs with timestamps
docker logs -t yolo-toys
```

### Resource Usage

```bash
# Container stats
docker stats yolo-toys

# Detailed inspection
docker inspect yolo-toys
```

---

## 🔒 Security Best Practices

### Non-Root User

Modify Dockerfile to run as non-root:

```dockerfile
# Add non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

### Read-Only Filesystem

```bash
docker run -d \
  --read-only \
  --tmpfs /tmp \
  -v model-cache:/app/cache \
  yolo-toys
```

### Resource Limits

```yaml
# docker-compose.yml
services:
  yolo-toys:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

---

## 🔄 Updates

### Update to New Version

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Clean up old images
docker image prune -f
```

### Rolling Update (Zero-Downtime)

```bash
# Start new container
docker-compose up -d --no-deps --scale yolo-toys=2

# Remove old container
docker-compose stop yolo-toys_1
docker-compose rm yolo-toys_1

# Scale back down
docker-compose up -d --scale yolo-toys=1
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker logs yolo-toys

# Verify environment
docker exec yolo-toys env | grep MODEL

# Test inside container
docker exec -it yolo-toys python -c "import torch; print(torch.__version__)"
```

### Out of Memory

```bash
# Check memory usage
docker stats --no-stream

# Restart with memory limit
docker run -m 4g --memory-swap 4g yolo-toys

# Use smaller model
export MODEL_NAME=yolov8n.pt
```

### Slow Model Loading

```bash
# Pre-download models
mkdir -p model-cache/huggingface
docker run -v $(pwd)/model-cache:/root/.cache yolo-toys python -c \
  "from app.model_manager import ModelManager; ModelManager().load_model('yolov8n.pt')"
```

---

## 🔗 Related Documentation

- 🚀 **[Installation](../getting-started/installation.md)** — Native installation
- ⚙️ **[Environment Variables](./environments.md)** — Configuration reference
- 🏗️ **[Architecture](../architecture/overview.md)** — System design

---

<div align="center">

**[⬆ Back to Top](#docker-deployment)**

</div>
