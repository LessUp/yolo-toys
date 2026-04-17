"""
API 路由组合模块 - 向后兼容

所有路由已拆分为独立模块：
- app/api/system.py - 系统相关
- app/api/models.py - 模型管理
- app/api/inference.py - 推理端点
- app/api/websocket.py - WebSocket
- app/api/utils.py - 共享工具

此文件保留用于向后兼容，直接导出组合后的路由。
"""

from fastapi import APIRouter

from app.api.system import router as system_router
from app.api.models import router as models_router
from app.api.inference import router as inference_router
from app.api.websocket import router as ws_router

# 创建主路由
router = APIRouter()

# 包含所有子路由
router.include_router(system_router)
router.include_router(models_router)
router.include_router(inference_router)
router.include_router(ws_router)

# 向后兼容：导出工具函数
from app.api.utils import (
    read_upload_image,
    validate_image_mime,
    parse_optional_float,
    parse_optional_int,
    parse_text_queries,
)

__all__ = [
    "router",
    "read_upload_image",
    "validate_image_mime",
    "parse_optional_float",
    "parse_optional_int",
    "parse_text_queries",
]
