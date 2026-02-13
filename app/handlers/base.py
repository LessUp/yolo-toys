"""
模型处理器基类 - 定义统一接口
"""
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image


class BaseHandler(ABC):
    """所有模型处理器的基类"""

    def __init__(self, device: str):
        self._device = device

    @property
    def device(self) -> str:
        return self._device

    # ------------------------------------------------------------------
    # 子类必须实现
    # ------------------------------------------------------------------

    @abstractmethod
    def load(self, model_id: str) -> Tuple[Any, Optional[Any]]:
        """
        加载模型，返回 (model, processor)。
        processor 可为 None（如 YOLO 不需要独立 processor）。
        """

    @abstractmethod
    def infer(
        self,
        model: Any,
        processor: Optional[Any],
        image: np.ndarray,
        *,
        conf: float = 0.25,
        iou: float = 0.45,
        max_det: int = 300,
        device: Optional[str] = None,
        imgsz: Optional[int] = None,
        half: bool = False,
        text_queries: Optional[List[str]] = None,
        question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """执行推理，返回标准结果字典"""

    # ------------------------------------------------------------------
    # 公共工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def bgr_to_pil(image: np.ndarray) -> Image.Image:
        """OpenCV BGR ndarray → PIL RGB Image"""
        return Image.fromarray(image[:, :, ::-1])

    @staticmethod
    def image_hw(image: np.ndarray) -> Tuple[int, int]:
        """返回 (height, width)"""
        return image.shape[:2]

    @staticmethod
    def make_result(
        image: np.ndarray,
        *,
        detections: Optional[List[Dict[str, Any]]] = None,
        inference_time: float,
        task: str = "detect",
        **extra,
    ) -> Dict[str, Any]:
        """构造标准返回字典"""
        h, w = image.shape[:2]
        result: Dict[str, Any] = {
            "width": w,
            "height": h,
            "inference_time": inference_time,
            "task": task,
        }
        if detections is not None:
            result["detections"] = detections
        result.update(extra)
        return result

    def _to_device(self, inputs: Dict[str, Any], device: Optional[str] = None) -> Dict[str, Any]:
        """将 tensor dict 移动到指定设备"""
        target = device or self._device
        if target == "cpu":
            return inputs
        return {k: (v.to(target) if hasattr(v, "to") else v) for k, v in inputs.items()}
