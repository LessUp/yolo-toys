"""
HuggingFace Transformers 模型处理器 - DETR / OWL-ViT / Grounding DINO
"""

import importlib.util
import logging
import time
from typing import Any

import numpy as np

from app.config import get_settings
from app.handlers.base import BaseHandler

try:
    import torch
except ImportError:
    torch = None

_HF_AVAILABLE = importlib.util.find_spec("transformers") is not None

logger = logging.getLogger(__name__)
settings = get_settings()


def _require_hf() -> None:
    """Check if HuggingFace transformers is available."""
    if not _HF_AVAILABLE:
        raise RuntimeError("transformers not installed")


def _require_torch() -> Any:
    """Return torch module when available."""
    if torch is None:
        raise RuntimeError("torch not installed")
    return torch


# ======================================================================
# DETR
# ======================================================================


class DETRHandler(BaseHandler):
    """Facebook DETR 目标检测"""

    def load(self, model_id: str) -> tuple[Any, Any]:
        _require_hf()
        from transformers import DetrForObjectDetection, DetrImageProcessor

        processor = DetrImageProcessor.from_pretrained(model_id)
        model = DetrForObjectDetection.from_pretrained(model_id)
        model = self._model_to_device(model)
        return model, processor

    def infer(
        self,
        model: Any,
        processor: Any,
        image: np.ndarray,
        *,
        conf: float = 0.5,
        iou: float = 0.45,
        max_det: int = 300,
        device: str | None = None,
        imgsz: int | None = None,
        half: bool = False,
        text_queries: list[str] | None = None,
        question: str | None = None,
    ) -> dict[str, Any]:
        t0 = time.time()
        torch_module = _require_torch()
        pil_image = self.bgr_to_pil(image)

        inputs = processor(images=pil_image, return_tensors="pt")
        inputs = self._to_device(inputs)

        try:
            with torch_module.no_grad():
                outputs = model(**inputs)
        except Exception as e:
            logger.error("DETR 推理失败: %s", e)
            raise

        target_sizes = torch_module.as_tensor([pil_image.size[::-1]])
        if self._device != "cpu":
            target_sizes = target_sizes.to(self._device)

        results = processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=conf
        )[0]

        elapsed = (time.time() - t0) * 1000.0

        dets = []
        for score, label, box in zip(
            results["scores"].cpu().numpy(),
            results["labels"].cpu().numpy(),
            results["boxes"].cpu().numpy(),
            strict=False,
        ):
            dets.append(
                {
                    "bbox": [float(v) for v in box],
                    "score": float(score),
                    "label": model.config.id2label.get(int(label), str(label)),
                }
            )

        return self.make_result(image, detections=dets, inference_time=elapsed, task="detect")


# ======================================================================
# OWL-ViT
# ======================================================================


class OWLViTHandler(BaseHandler):
    """Google OWL-ViT 开放词汇检测"""

    def load(self, model_id: str) -> tuple[Any, Any]:
        _require_hf()
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
        model = self._model_to_device(model)
        return model, processor

    def infer(
        self,
        model: Any,
        processor: Any,
        image: np.ndarray,
        *,
        conf: float = 0.1,
        iou: float = 0.45,
        max_det: int = 300,
        device: str | None = None,
        imgsz: int | None = None,
        half: bool = False,
        text_queries: list[str] | None = None,
        question: str | None = None,
    ) -> dict[str, Any]:
        t0 = time.time()
        torch_module = _require_torch()
        queries = text_queries or ["object"]
        pil_image = self.bgr_to_pil(image)

        inputs = processor(text=queries, images=pil_image, return_tensors="pt")
        inputs = self._to_device(inputs)

        try:
            with torch_module.no_grad():
                outputs = model(**inputs)
        except Exception as e:
            logger.error("OWL-ViT 推理失败: %s", e)
            raise

        target_sizes = torch_module.as_tensor([pil_image.size[::-1]])
        if self._device != "cpu":
            target_sizes = target_sizes.to(self._device)
        results = processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=conf
        )[0]

        elapsed = (time.time() - t0) * 1000.0

        dets = []
        for score, label, box in zip(
            results["scores"].cpu().numpy(),
            results["labels"].cpu().numpy(),
            results["boxes"].cpu().numpy(),
            strict=False,
        ):
            dets.append(
                {
                    "bbox": [float(v) for v in box],
                    "score": float(score),
                    "label": queries[int(label)] if int(label) < len(queries) else str(label),
                }
            )

        return self.make_result(
            image, detections=dets, inference_time=elapsed, task="detect", text_queries=queries
        )


# ======================================================================
# Grounding DINO
# ======================================================================


class GroundingDINOHandler(BaseHandler):
    """IDEA-Research Grounding DINO 开放集检测"""

    def load(self, model_id: str) -> tuple[Any, Any]:
        _require_hf()
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
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
        torch_module = _require_torch()
        queries = text_queries or ["object"]
        pil_image = self.bgr_to_pil(image)

        labels = self._prepare_labels(queries)

        # 优先使用 list[list[str]] 的新格式；若不兼容则回退到句号分隔字符串
        try:
            inputs = processor(images=pil_image, text=[labels], return_tensors="pt")
        except Exception:
            text_str = ". ".join(labels)
            if not text_str.endswith("."):
                text_str += "."
            inputs = processor(images=pil_image, text=text_str, return_tensors="pt")

        inputs = self._to_device(inputs)

        try:
            with torch_module.no_grad():
                outputs = model(**inputs)
        except Exception as e:
            logger.error("GroundingDINO 推理失败: %s", e)
            raise

        if not hasattr(processor, "post_process_grounded_object_detection"):
            raise RuntimeError("transformers 版本过低，缺少 GroundingDINO 后处理方法")

        results = processor.post_process_grounded_object_detection(
            outputs=outputs,
            input_ids=inputs.get("input_ids"),
            threshold=float(conf),
            text_threshold=settings.grounding_text_threshold,
            target_sizes=[pil_image.size[::-1]],
            text_labels=[labels],
        )
        result = results[0] if results else {}

        boxes = result.get("boxes")
        scores = result.get("scores")
        det_labels = result.get("labels") or result.get("text_labels") or []

        boxes_np = (
            boxes.detach().cpu().numpy()
            if boxes is not None and hasattr(boxes, "detach")
            else np.zeros((0, 4))
        )
        scores_np = (
            scores.detach().cpu().numpy()
            if scores is not None and hasattr(scores, "detach")
            else np.zeros((0,))
        )

        dets: list[dict[str, Any]] = []
        for i in range(int(scores_np.shape[0])):
            raw_label = det_labels[i] if i < len(det_labels) else ""
            label = (
                ", ".join(str(x) for x in raw_label)
                if isinstance(raw_label, list | tuple)
                else str(raw_label)
            )
            dets.append(
                {
                    "bbox": [float(v) for v in boxes_np[i].tolist()],
                    "score": float(scores_np[i]),
                    "label": label,
                }
            )

        elapsed = (time.time() - t0) * 1000.0
        return self.make_result(
            image, detections=dets, inference_time=elapsed, task="detect", text_queries=queries
        )

    @staticmethod
    def _prepare_labels(queries: list[str]) -> list[str]:
        labels: list[str] = []
        for q in queries:
            q = str(q).strip()
            if not q:
                continue
            if q.lower().startswith(("a ", "an ", "the ")):
                labels.append(q)
            else:
                labels.append(f"a {q}")
        return labels or ["a object"]
