"""
FastAPI 应用入口 - 使用 lifespan 管理生命周期
"""
import logging
from contextlib import asynccontextmanager

import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from app import __version__ as VERSION
from app.config import get_settings
from app.model_manager import model_manager
from app.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """应用生命周期：启动预热 / 关闭清理"""
    # ---- startup ----
    if not settings.skip_warmup:
        try:
            model_manager.load_model(settings.model_name)
            dummy = np.zeros((640, 640, 3), dtype=np.uint8)
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
    logger.info("应用关闭")


app = FastAPI(
    title="YOLO-Toys Vision API",
    description="多模型实时物体检测、分割、姿态估计和多模态分析 API",
    version=VERSION,
    lifespan=lifespan,
)

# 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Cache-Control", "no-store")
    return response


# 注册路由
app.include_router(router)

# 挂载静态文件（放在路由之后，确保 API 优先）
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
