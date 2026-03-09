"""
BLIP 多模态模型处理器 - 图像描述 / 视觉问答
"""

import time
from typing import Any

import numpy as np

from app.handlers.base import BaseHandler

try:
    import torch
except ImportError:
    torch = None

_HF_AVAILABLE = False
try:
    from transformers import BlipForConditionalGeneration, BlipProcessor

    _HF_AVAILABLE = True
except ImportError:
    pass


def _require_hf():
    if not _HF_AVAILABLE:
        raise RuntimeError("transformers not installed")


class BLIPCaptionHandler(BaseHandler):
    """BLIP 图像描述生成"""

    def load(self, model_id: str) -> tuple[Any, Any]:
        _require_hf()
        processor = BlipProcessor.from_pretrained(model_id)
        model = BlipForConditionalGeneration.from_pretrained(model_id)
        model = self._model_to_device(model)
        return model, processor

    def infer(
        self,
        model: Any,
        processor: Any,
        image: np.ndarray,
        *,
        conf: float = 0.25,
        iou: float = 0.45,
        max_det: int = 300,
        device: str | None = None,
        imgsz: int | None = None,
        half: bool = False,
        text_queries: list[str] | None = None,
        question: str | None = None,
    ) -> dict[str, Any]:
        t0 = time.time()
        pil_image = self.bgr_to_pil(image)

        inputs = processor(pil_image, return_tensors="pt")
        inputs = self._to_device(inputs)

        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=50)

        caption = processor.decode(out[0], skip_special_tokens=True)
        elapsed = (time.time() - t0) * 1000.0

        return self.make_result(image, inference_time=elapsed, task="caption", caption=caption)


class BLIPVQAHandler(BaseHandler):
    """BLIP 视觉问答"""

    def load(self, model_id: str) -> tuple[Any, Any]:
        _require_hf()
        from transformers import BlipForQuestionAnswering

        processor = BlipProcessor.from_pretrained(model_id)
        model = BlipForQuestionAnswering.from_pretrained(model_id)
        model = self._model_to_device(model)
        return model, processor

    def infer(
        self,
        model: Any,
        processor: Any,
        image: np.ndarray,
        *,
        conf: float = 0.25,
        iou: float = 0.45,
        max_det: int = 300,
        device: str | None = None,
        imgsz: int | None = None,
        half: bool = False,
        text_queries: list[str] | None = None,
        question: str | None = None,
    ) -> dict[str, Any]:
        t0 = time.time()
        q = question or "What is in this image?"
        pil_image = self.bgr_to_pil(image)

        inputs = processor(pil_image, q, return_tensors="pt")
        inputs = self._to_device(inputs)

        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=50)

        answer = processor.decode(out[0], skip_special_tokens=True)
        elapsed = (time.time() - t0) * 1000.0

        return self.make_result(
            image, inference_time=elapsed, task="vqa", question=q, answer=answer
        )
