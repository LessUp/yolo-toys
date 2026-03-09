# ---- Stage 1: 依赖安装 ----
FROM python:3.11-slim AS deps

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# ---- Stage 2: 运行时镜像 ----
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HF_HOME=/app/.cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=deps /install /usr/local

RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser
WORKDIR /app

COPY yolov8*.pt ./
COPY app ./app
COPY frontend ./frontend

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
