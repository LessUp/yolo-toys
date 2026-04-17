# Docker 部署

使用 Docker 容器部署 YOLO-Toys。

<p align="center">
  <a href="docker.md">English</a> •
  <a href="./">⬅ 返回部署文档</a>
</p>

---

## 📋 前提条件

- Docker 20.10+
- Docker Compose 2.0+（可选，用于 compose 部署）
- 4GB+ 可用内存
- 2GB+ 空闲磁盘空间

---

## 🚀 快速开始

### 使用 Docker Run

```bash
# 克隆仓库
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys

# 复制环境配置
cp .env.example .env

# 构建镜像
docker build -t yolo-toys .

# 运行容器
docker run -d \
  --name yolo-toys \
  -p 8000:8000 \
  --env-file .env \
  -v model-cache:/root/.cache \
  yolo-toys
```

### 使用 Docker Compose（推荐）

```bash
# 克隆并配置
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys
cp .env.example .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🐳 Dockerfile 参考

### 多阶段构建

```dockerfile
# 阶段 1：构建器
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 阶段 2：运行时
FROM python:3.11-slim

WORKDIR /app

# 复制已安装的包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制应用
COPY app/ ./app/
COPY frontend/ ./frontend/

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**优点：**
- 最终镜像更小
- 运行时无构建依赖
- 部署更快

---

## ⚙️ docker-compose.yml 参考

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

### 选项说明

| 选项 | 描述 |
|------|------|
| `build: .` | 从本地 Dockerfile 构建 |
| `ports` | 映射主机:容器端口 |
| `environment` | 环境变量 |
| `volumes` | 持久化存储挂载 |
| `restart` | 自动重启策略 |
| `healthcheck` | 容器健康监控 |

---

## 🖥️ GPU 支持

### NVIDIA GPU (CUDA)

#### 带 GPU 的 docker-compose.yml

```yaml
services:
  yolo-toys:
    build: .
    runtime: nvidia  # 使用 NVIDIA 容器运行时
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - DEVICE=cuda:0
    # ... 其他选项
```

#### 带 GPU 的 Docker Run

```bash
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -e DEVICE=cuda:0 \
  yolo-toys
```

#### 前提条件

1. 安装 NVIDIA Container Toolkit：
```bash
# Ubuntu
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

2. 验证 GPU 支持：
```bash
docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi
```

### Apple Silicon (MPS)

适用于 Mac 的 Docker Desktop 不支持 Apple Silicon 的 GPU 直通。如需 MPS 支持，请使用原生 Python 安装。

---

## 🔧 生产部署

### 环境变量

为生产创建 `.env` 文件：

```bash
# 服务器配置
PORT=8000
ALLOW_ORIGINS=https://yourdomain.com

# 模型配置
MODEL_NAME=yolov8s.pt
CONF_THRESHOLD=0.25
IOU_THRESHOLD=0.45
MAX_DET=300
DEVICE=auto

# 性能
MAX_CONCURRENCY=4
SKIP_WARMUP=false

# 可选：设置模型缓存路径
TORCH_HOME=/app/cache/torch
HF_HOME=/app/cache/huggingface
```

### 反向代理（Nginx）

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

        # WebSocket 支持
        proxy_read_timeout 86400;
    }
}
```

### SSL (Let's Encrypt)

```bash
# 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 自动续期已自动配置
```

---

## 📊 监控

### 健康检查

```bash
# 检查容器健康状态
docker ps

# 查看健康状态
docker inspect --format='{{.State.Health.Status}}' yolo-toys

# 手动健康检查
curl http://localhost:8000/health
```

### 日志

```bash
# 查看实时日志
docker logs -f yolo-toys

# 查看最后 100 行
docker logs --tail 100 yolo-toys

# 带时间戳查看日志
docker logs -t yolo-toys
```

### 资源使用

```bash
# 容器统计
docker stats yolo-toys

# 详细检查
docker inspect yolo-toys
```

---

## 🔒 安全最佳实践

### 非 root 用户

修改 Dockerfile 以非 root 运行：

```dockerfile
# 添加非 root 用户
RUN useradd -m -u 1000 appuser
USER appuser
```

### 只读文件系统

```bash
docker run -d \
  --read-only \
  --tmpfs /tmp \
  -v model-cache:/app/cache \
  yolo-toys
```

### 资源限制

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

## 🔄 更新

### 更新到新版本

```bash
# 拉取最新代码
git pull origin main

# 重建并重启
docker-compose down
docker-compose up --build -d

# 清理旧镜像
docker image prune -f
```

### 滚动更新（零停机）

```bash
# 启动新容器
docker-compose up -d --no-deps --scale yolo-toys=2

# 移除旧容器
docker-compose stop yolo-toys_1
docker-compose rm yolo-toys_1

# 缩容
docker-compose up -d --scale yolo-toys=1
```

---

## 🐛 故障排除

### 容器无法启动

```bash
# 检查错误日志
docker logs yolo-toys

# 验证环境
docker exec yolo-toys env | grep MODEL

# 容器内测试
docker exec -it yolo-toys python -c "import torch; print(torch.__version__)"
```

### 内存不足

```bash
# 检查内存使用
docker stats --no-stream

# 带内存限制重启
docker run -m 4g --memory-swap 4g yolo-toys

# 使用更小模型
export MODEL_NAME=yolov8n.pt
```

### 模型加载慢

```bash
# 预下载模型
mkdir -p model-cache/huggingface
docker run -v $(pwd)/model-cache:/root/.cache yolo-toys python -c \
  "from app.model_manager import ModelManager; ModelManager().load_model('yolov8n.pt')"
```

---

## 🔗 相关文档

- 🚀 **[安装](../getting-started/installation.zh-CN.md)** — 原生安装
- ⚙️ **[环境变量](./environments.md)** — 配置参考
- 🏗️ **[架构](../architecture/overview.zh-CN.md)** — 系统设计

---

<div align="center">

**[⬆ 返回顶部](#docker-部署)**

</div>
