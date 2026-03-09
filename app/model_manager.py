"""
多模型管理器 - 策略模式重构版

使用 HandlerRegistry + BaseHandler 体系替代原有的 if/elif 链式调用，
每种模型类型的加载和推理逻辑被封装在独立的 Handler 中。
本模块仅保留面向上层（main.py / tests）的公共 API。
"""

import logging
import os
from typing import Any

import numpy as np

from app.handlers.registry import HandlerRegistry

logger = logging.getLogger(__name__)

try:
    import torch
except ImportError:
    torch = None


def get_device() -> str:
    """自动选择最佳设备"""
    device_env = os.getenv("DEVICE", "").strip()
    if device_env:
        return device_env
    if torch is not None:
        if hasattr(torch, "cuda") and torch.cuda.is_available():
            return "cuda:0"
        if (
            hasattr(torch, "backends")
            and hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            return "mps"
    return "cpu"


class ModelManager:
    """统一模型管理器 - 委托 HandlerRegistry 完成加载和推理"""

    def __init__(self):
        self._device = get_device()
        self._registry = HandlerRegistry(self._device)
        # 缓存：model_id → (model, processor)
        self._cache: dict[str, tuple] = {}

    @property
    def device(self) -> str:
        return self._device

    def load_model(self, model_id: str) -> Any:
        """加载模型（带缓存），返回模型对象"""
        if model_id in self._cache:
            return self._cache[model_id][0]

        handler = self._registry.get_handler(model_id)
        model, processor = handler.load(model_id)
        self._cache[model_id] = (model, processor)
        logger.info("模型已加载: %s (handler=%s)", model_id, type(handler).__name__)
        return model

    def infer(
        self,
        *,
        model_id: str,
        image: np.ndarray,
        conf: float = 0.25,
        iou: float = 0.45,
        max_det: int = 300,
        device: str | None = None,
        imgsz: int | None = None,
        half: bool = False,
        text_queries: list[str] | None = None,
        question: str | None = None,
    ) -> dict[str, Any]:
        """统一推理接口 - 自动路由到对应 Handler"""
        # 确保模型已加载
        self.load_model(model_id)

        handler = self._registry.get_handler(model_id)
        model, processor = self._cache[model_id]

        return handler.infer(
            model,
            processor,
            image,
            conf=conf,
            iou=iou,
            max_det=max_det,
            device=device,
            imgsz=imgsz,
            half=half,
            text_queries=text_queries,
            question=question,
        )


# 全局模型管理器实例
model_manager = ModelManager()
