"""
API 路由模块

将路由按功能拆分为独立模块：
- system: 系统相关 (health, stats, cache)
- models: 模型管理 (models, labels)
- inference: 推理端点 (infer, caption, vqa)
- websocket: WebSocket 实时推理
- utils: 共享工具函数
"""

from app.api.inference import router as inference_router
from app.api.models import router as models_router
from app.api.system import router as system_router
from app.api.websocket import router as ws_router

__all__ = [
    "system_router",
    "models_router",
    "inference_router",
    "ws_router",
]
