"""
Prometheus 指标导出
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from prometheus_client import Counter, Gauge, Histogram, Info

# Application info
APP_INFO = Info("yolo_toys_info", "Application information")
APP_INFO.info({"version": "3.1.0", "framework": "fastapi"})

# Request metrics
INFERENCE_REQUESTS = Counter(
    "inference_requests_total", "Total inference requests", ["model", "task", "status"]
)

INFERENCE_LATENCY = Histogram(
    "inference_duration_seconds",
    "Inference latency in seconds",
    ["model", "task"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

INFERENCE_INPUT_SIZE = Histogram(
    "inference_input_size_bytes",
    "Input image size in bytes",
    buckets=[1024, 4096, 16384, 65536, 262144, 1048576, 4194304],
)

# Model metrics
MODEL_LOAD_TIME = Gauge("model_load_duration_seconds", "Time to load model", ["model_id"])

MODEL_CACHE_SIZE = Gauge("model_cache_size", "Current number of cached models")

MODEL_MEMORY_USAGE = Gauge("model_memory_usage_ratio", "Current memory usage ratio")

# WebSocket metrics
WEBSOCKET_CONNECTIONS = Gauge(
    "websocket_connections_active", "Number of active WebSocket connections"
)

WEBSOCKET_MESSAGES = Counter(
    "websocket_messages_total", "Total WebSocket messages", ["message_type", "direction"]
)

# HTTP metrics
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint", "status_code"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

F = TypeVar("F", bound=Callable[..., Any])


def track_inference(model: str, task: str = "detect"):
    """装饰器：跟踪推理调用"""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            status = "success"
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                duration = time.time() - start
                INFERENCE_REQUESTS.labels(model=model, task=task, status=status).inc()
                INFERENCE_LATENCY.labels(model=model, task=task).observe(duration)

        return cast(F, wrapper)

    return decorator


def update_model_cache_metric(size: int) -> None:
    """更新缓存大小指标"""
    MODEL_CACHE_SIZE.set(size)


def update_memory_metric(usage: float) -> None:
    """更新内存使用指标"""
    MODEL_MEMORY_USAGE.set(usage)
