"""
系统相关 API 路由

- /health - 健康检查
- /system/stats - 系统统计
- /system/cache/clear - 清空缓存
"""

from typing import Any

from fastapi import APIRouter

from app import __version__ as VERSION
from app.config import get_settings
from app.model_manager import model_manager

router = APIRouter(tags=["System"])
settings = get_settings()


@router.get("/health")
async def health() -> dict[str, Any]:
    """健康检查端点 - 包含系统和缓存状态"""
    return {
        "status": "ok",
        "version": VERSION,
        "device": model_manager.device,
        "default_model": settings.model_name,
        "defaults": {
            "conf": settings.conf_threshold,
            "iou": settings.iou_threshold,
            "max_det": settings.max_det,
        },
        "cache": model_manager.cache_info,
    }


@router.get("/system/stats")
async def system_stats() -> dict[str, Any]:
    """获取系统统计信息（管理员用）"""
    return model_manager.get_stats()


@router.post("/system/cache/clear")
async def clear_cache() -> dict[str, Any]:
    """清空模型缓存（管理员用）"""
    before_size = len(model_manager.cache)
    model_manager.clear_cache()
    return {
        "status": "ok",
        "cleared_models": before_size,
        "message": "Model cache cleared successfully"
    }
