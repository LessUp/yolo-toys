"""
FastAPI 应用入口 - 使用 lifespan 管理生命周期
"""

import logging
from contextlib import asynccontextmanager

import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app import __version__ as VERSION
from app.config import get_settings
from app.middleware import (
    MetricsMiddleware,
    SecurityHeadersMiddleware,
    TimeoutMiddleware,
    RateLimitMiddleware,
)
from app.model_manager import model_manager
from app.routes import router
from app.metrics import update_model_cache_metric, update_memory_metric
from app.model_manager import get_memory_usage

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """应用生命周期：启动预热 / 关闭清理"""
    # ---- startup ----
    logger.info("Starting YOLO-Toys v%s", VERSION)
    logger.info("Device: %s", model_manager.device)
    logger.info("Cache config: maxsize=%s, ttl=%ss", 
                model_manager.cache.maxsize,
                model_manager.cache.ttl)

    if not settings.skip_warmup:
        try:
            model_manager.load_model(settings.model_name)
            dummy = np.zeros(
                (settings.warmup_image_size, settings.warmup_image_size, 3), dtype=np.uint8
            )
            model_manager.infer(
                model_id=settings.model_name,
                image=dummy,
                conf=settings.conf_threshold,
                iou=settings.iou_threshold,
                max_det=settings.max_det,
            )
            logger.info("模型预热完成: %s", settings.model_name)
        except Exception as e:
            logger.warning("模型预热失败: %s", e)
    else:
        logger.info("跳过模型预热 (SKIP_WARMUP)")

    yield

    # ---- shutdown ----
    logger.info("应用关闭，清理资源...")
    model_manager.clear_cache()
    logger.info("资源清理完成")


app = FastAPI(
    title="YOLO-Toys Vision API",
    description="多模型实时物体检测、分割、姿态估计和多模态分析 API",
    version=VERSION,
    lifespan=lifespan,
)

# 中间件（注意添加顺序：先添加的最后执行）
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(TimeoutMiddleware, timeout_seconds=60.0)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.max_concurrency * 60  # 基于并发数调整
)
app.add_middleware(GZipMiddleware, minimum_size=settings.gzip_min_size)

# CORS - 使用更安全的配置
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials="*" not in settings.origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=600,
)


# Prometheus 指标端点
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus 指标导出端点"""
    # 更新动态指标
    update_model_cache_metric(len(model_manager.cache))
    update_memory_metric(get_memory_usage())
    return PlainTextResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST
    )


# 注册路由（保持向后兼容的根路径）
app.include_router(router)

# 挂载静态文件（放在路由之后，确保 API 优先）
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
