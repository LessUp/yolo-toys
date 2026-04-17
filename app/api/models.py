"""
模型管理 API 路由

- /models - 模型列表
- /models/{id} - 模型详情
- /labels - 模型标签
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.handlers.registry import get_available_models, get_model_info
from app.model_manager import model_manager

router = APIRouter(tags=["Models"])
settings = get_settings()


@router.get("/models")
async def list_models() -> dict[str, Any]:
    """获取所有可用模型，按类别分组"""
    return {
        "default": settings.model_name,
        "categories": get_available_models(),
    }


@router.get("/models/{model_id:path}")
async def model_info(model_id: str) -> dict[str, Any]:
    """获取指定模型的详细信息"""
    info = get_model_info(model_id)
    if not info:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"id": model_id, **info}


@router.get("/labels")
async def labels(model: str | None = Query(default=None)) -> dict[str, Any]:
    """获取模型的标签列表"""
    model_id = model or settings.model_name
    try:
        m = model_manager.load_model(model_id)
        names = getattr(getattr(m, "model", None), "names", None)
        if isinstance(names, dict):
            ordered = [names[k] for k in sorted(names.keys())]
        elif isinstance(names, list | tuple):
            ordered = list(names)
        else:
            ordered = []
        return {"model": model_id, "labels": ordered}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
