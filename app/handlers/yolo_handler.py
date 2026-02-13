"""
YOLO 模型处理器 - 检测 / 分割 / 姿态估计
"""
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.handlers.base import BaseHandler


class YOLOHandler(BaseHandler):
    """处理所有 YOLO 系列模型（detect / segment / pose）"""

    def load(self, model_id: str) -> Tuple[Any, None]:
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("ultralytics not installed") from exc
        return YOLO(model_id), None

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
        t0 = time.time()
        dev = device or self._device

        kwargs: Dict[str, Any] = {
            "conf": conf,
            "iou": iou,
            "max_det": max_det,
            "verbose": False,
            "device": dev,
        }
        if imgsz:
            kwargs["imgsz"] = int(imgsz)
        if half and dev.startswith("cuda"):
            kwargs["half"] = True

        results = model(image, **kwargs)
        elapsed = (time.time() - t0) * 1000.0

        r = results[0]
        task = self._resolve_task(model, r)
        dets = self._parse_detections(r, task)

        return self.make_result(image, detections=dets, inference_time=elapsed, task=task)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_task(model: Any, result: Any) -> str:
        model_task = getattr(getattr(model, "model", None), "task", None)
        if model_task in ("detect", "segment", "pose"):
            return model_task
        if getattr(result, "masks", None) is not None:
            return "segment"
        if getattr(result, "keypoints", None) is not None:
            return "pose"
        return "detect"

    @staticmethod
    def _parse_detections(r: Any, task: str) -> List[Dict[str, Any]]:
        boxes = r.boxes
        dets: List[Dict[str, Any]] = []

        if boxes is None or boxes.xyxy is None or boxes.xyxy.shape[0] == 0:
            return dets

        xyxy = boxes.xyxy.detach().cpu().numpy()
        scores = boxes.conf.detach().cpu().numpy()
        classes = boxes.cls.detach().cpu().numpy().astype(int)
        names = r.names

        for i in range(xyxy.shape[0]):
            item: Dict[str, Any] = {
                "bbox": [float(v) for v in xyxy[i].tolist()],
                "score": float(scores[i]),
                "label": (
                    names.get(classes[i], str(classes[i]))
                    if isinstance(names, dict)
                    else str(classes[i])
                ),
            }

            # 分割多边形
            if task == "segment" and getattr(r, "masks", None) is not None:
                try:
                    masks_xy = getattr(r.masks, "xy", None)
                    if masks_xy is not None and i < len(masks_xy):
                        polys = masks_xy[i]
                        if polys is not None:
                            item["polygons"] = [[float(v) for v in polys.reshape(-1)]]
                except Exception:
                    pass

            # 关键点
            if task == "pose" and getattr(r, "keypoints", None) is not None:
                try:
                    kps_xy = getattr(r.keypoints, "xy", None)
                    if kps_xy is not None and i < len(kps_xy):
                        kps = kps_xy[i]
                        if kps is not None:
                            item["keypoints"] = [[float(x), float(y)] for x, y in kps.tolist()]
                except Exception:
                    pass

            dets.append(item)

        return dets
