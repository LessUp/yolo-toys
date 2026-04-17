"""
多模型管理器 - 策略模式重构版

使用 HandlerRegistry + BaseHandler 体系替代原有的 if/elif 链式调用，
每种模型类型的加载和推理逻辑被封装在独立的 Handler 中。
本模块仅保留面向上层（main.py / tests）的公共 API。
"""

import gc
import logging
import os
import time
import urllib.parse
import weakref
from typing import Any

import numpy as np
from cachetools import TTLCache

from app.handlers.registry import HandlerRegistry

logger = logging.getLogger(__name__)

try:
    import torch
except ImportError:
    torch = None

# Model cache configuration
CACHE_MAXSIZE = int(os.getenv("MODEL_CACHE_MAXSIZE", "10"))
CACHE_TTL = int(os.getenv("MODEL_CACHE_TTL", "3600"))  # 1 hour default
MEMORY_THRESHOLD = float(os.getenv("MODEL_MEMORY_THRESHOLD", "0.85"))  # 85% memory threshold


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


def get_memory_usage() -> float:
    """获取当前内存使用比例，用于缓存清理决策"""
    try:
        import psutil

        return psutil.virtual_memory().percent / 100
    except ImportError:
        return 0.0


class ModelCache(TTLCache):
    """带内存监控的 TTL 缓存"""

    def __init__(self, maxsize: int, ttl: float):
        super().__init__(maxsize=maxsize, ttl=ttl)
        self._access_times: dict[str, float] = {}

    def __getitem__(self, key: str) -> Any:
        value = super().__getitem__(key)
        self._access_times[key] = time.time()
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        # 内存压力检查
        if len(self) >= self.maxsize or get_memory_usage() > MEMORY_THRESHOLD:
            self._evict_lru()
        super().__setitem__(key, value)
        self._access_times[key] = time.time()

    def _evict_lru(self) -> None:
        """驱逐最久未使用的模型"""
        if not self._access_times:
            return
        oldest_key = min(self._access_times, key=self._access_times.get)
        logger.warning("内存压力，驱逐模型缓存: %s", oldest_key)
        self.pop(oldest_key, None)
        self._access_times.pop(oldest_key, None)
        # 尝试垃圾回收
        gc.collect()
        if torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()


class ModelManager:
    """统一模型管理器 - 委托 HandlerRegistry 完成加载和推理"""

    def __init__(self):
        self._device = get_device()
        self._registry = HandlerRegistry(self._device)
        # 使用 LRU + TTL 混合缓存
        self._cache = ModelCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
        self._load_times: dict[str, float] = {}
        self._access_count: dict[str, int] = {}

    @property
    def device(self) -> str:
        return self._device

    @property
    def cache(self) -> "ModelCache":
        """访问模型缓存（只读）"""
        return self._cache

    @property
    def cache_info(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "cache_size": len(self._cache),
            "cache_maxsize": self._cache.maxsize,
            "cache_ttl": self._cache.ttl,
            "cached_models": list(self._cache.keys()),
            "memory_usage": get_memory_usage(),
        }

    def clear_cache(self) -> None:
        """清空模型缓存"""
        cleared = len(self._cache)
        self._cache.clear()
        self._access_count.clear()
        gc.collect()
        if torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("模型缓存已清空: %d 个模型", cleared)

    def load_model(self, model_id: str) -> Any:
        """加载模型（带缓存），返回模型对象

        Args:
            model_id: 模型标识符

        Returns:
            加载的模型对象

        Raises:
            ValueError: 模型 ID 包含非法字符
        """
        # 安全验证：防止路径遍历攻击（包括 URL 编码绕过）
        if not model_id or not isinstance(model_id, str):
            raise ValueError("Model ID must be a non-empty string")

        # 解码 URL 编码后再次检查
        decoded_id = urllib.parse.unquote(model_id)
        forbidden_patterns = ["../", "..\\", "/", "\\", "\x00"]
        for pattern in forbidden_patterns:
            if pattern in model_id or pattern in decoded_id:
                raise ValueError("Invalid model ID: contains forbidden character sequence")

        if model_id in self._cache:
            self._access_count[model_id] = self._access_count.get(model_id, 0) + 1
            return self._cache[model_id][0]

        # 记录加载时间
        start_time = time.time()
        handler = self._registry.get_handler(model_id)
        model, processor = handler.load(model_id)
        load_time = time.time() - start_time

        self._cache[model_id] = (model, processor)
        self._load_times[model_id] = load_time
        self._access_count[model_id] = 1

        logger.info(
            "模型已加载: %s (handler=%s, load_time=%.2fs)",
            model_id,
            type(handler).__name__,
            load_time,
        )
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

        # 使用用户指定的设备或默认设备
        target_device = device or self._device

        return handler.infer(
            model,
            processor,
            image,
            conf=conf,
            iou=iou,
            max_det=max_det,
            device=target_device,
            imgsz=imgsz,
            half=half,
            text_queries=text_queries,
            question=question,
        )

    def get_stats(self) -> dict[str, Any]:
        """获取管理器统计信息"""
        return {
            "device": self._device,
            "cache_info": self.cache_info,
            "model_stats": {
                model_id: {
                    "load_time": self._load_times.get(model_id, 0),
                    "access_count": self._access_count.get(model_id, 0),
                }
                for model_id in self._cache.keys()
            },
        }


# 全局模型管理器实例
model_manager = ModelManager()
