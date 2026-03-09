"""
模型注册表 - 集中管理所有模型元数据与处理器映射
"""

from typing import Any

from app.handlers.base import BaseHandler
from app.handlers.blip_handler import BLIPCaptionHandler, BLIPVQAHandler
from app.handlers.hf_handler import DETRHandler, GroundingDINOHandler, OWLViTHandler
from app.handlers.yolo_handler import YOLOHandler


class ModelCategory:
    """模型类别常量"""

    YOLO_DETECT = "yolo_detect"
    YOLO_SEGMENT = "yolo_segment"
    YOLO_POSE = "yolo_pose"
    HF_DETR = "hf_detr"
    HF_OWLVIT = "hf_owlvit"
    HF_GROUNDING_DINO = "hf_grounding_dino"
    MULTIMODAL_CAPTION = "multimodal_caption"
    MULTIMODAL_VQA = "multimodal_vqa"


# 类别 → 处理器类映射
_CATEGORY_HANDLER_MAP = {
    ModelCategory.YOLO_DETECT: YOLOHandler,
    ModelCategory.YOLO_SEGMENT: YOLOHandler,
    ModelCategory.YOLO_POSE: YOLOHandler,
    ModelCategory.HF_DETR: DETRHandler,
    ModelCategory.HF_OWLVIT: OWLViTHandler,
    ModelCategory.HF_GROUNDING_DINO: GroundingDINOHandler,
    ModelCategory.MULTIMODAL_CAPTION: BLIPCaptionHandler,
    ModelCategory.MULTIMODAL_VQA: BLIPVQAHandler,
}

# 模型注册表：模型 ID → 元数据
MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    # YOLO 检测
    "yolov8n.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Nano",
        "description": "超轻量检测模型，适合实时场景，速度最快",
        "speed": "极快",
        "accuracy": "中等",
    },
    "yolov8s.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Small",
        "description": "轻量检测模型，平衡速度与精度",
        "speed": "快",
        "accuracy": "较好",
    },
    "yolov8m.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Medium",
        "description": "中等规模检测模型，精度更高",
        "speed": "中等",
        "accuracy": "高",
    },
    "yolov8l.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 Large",
        "description": "大规模检测模型，高精度",
        "speed": "较慢",
        "accuracy": "很高",
    },
    "yolov8x.pt": {
        "category": ModelCategory.YOLO_DETECT,
        "name": "YOLOv8 XLarge",
        "description": "超大规模检测模型，最高精度",
        "speed": "慢",
        "accuracy": "最高",
    },
    # YOLO 分割
    "yolov8n-seg.pt": {
        "category": ModelCategory.YOLO_SEGMENT,
        "name": "YOLOv8 Nano Seg",
        "description": "超轻量实例分割模型",
        "speed": "极快",
        "accuracy": "中等",
    },
    "yolov8s-seg.pt": {
        "category": ModelCategory.YOLO_SEGMENT,
        "name": "YOLOv8 Small Seg",
        "description": "轻量实例分割模型",
        "speed": "快",
        "accuracy": "较好",
    },
    "yolov8m-seg.pt": {
        "category": ModelCategory.YOLO_SEGMENT,
        "name": "YOLOv8 Medium Seg",
        "description": "中等规模实例分割模型",
        "speed": "中等",
        "accuracy": "高",
    },
    # YOLO 姿态
    "yolov8n-pose.pt": {
        "category": ModelCategory.YOLO_POSE,
        "name": "YOLOv8 Nano Pose",
        "description": "超轻量姿态估计模型",
        "speed": "极快",
        "accuracy": "中等",
    },
    "yolov8s-pose.pt": {
        "category": ModelCategory.YOLO_POSE,
        "name": "YOLOv8 Small Pose",
        "description": "轻量姿态估计模型，检测人体关键点",
        "speed": "快",
        "accuracy": "较好",
    },
    "yolov8m-pose.pt": {
        "category": ModelCategory.YOLO_POSE,
        "name": "YOLOv8 Medium Pose",
        "description": "中等规模姿态估计模型",
        "speed": "中等",
        "accuracy": "高",
    },
    # HuggingFace DETR
    "facebook/detr-resnet-50": {
        "category": ModelCategory.HF_DETR,
        "name": "DETR ResNet-50",
        "description": "Facebook 的 DEtection TRansformer，端到端目标检测",
        "speed": "中等",
        "accuracy": "高",
    },
    "facebook/detr-resnet-101": {
        "category": ModelCategory.HF_DETR,
        "name": "DETR ResNet-101",
        "description": "DETR 大规模版本，更高精度",
        "speed": "较慢",
        "accuracy": "很高",
    },
    # OWL-ViT
    "google/owlvit-base-patch32": {
        "category": ModelCategory.HF_OWLVIT,
        "name": "OWL-ViT Base",
        "description": "开放词汇检测，可检测任意文本描述的物体",
        "speed": "中等",
        "accuracy": "高",
    },
    # Grounding DINO
    "IDEA-Research/grounding-dino-tiny": {
        "category": ModelCategory.HF_GROUNDING_DINO,
        "name": "Grounding DINO Tiny",
        "description": "先进的开放集检测模型，支持文本提示",
        "speed": "中等",
        "accuracy": "很高",
    },
    # 多模态 - 图像描述
    "Salesforce/blip-image-captioning-base": {
        "category": ModelCategory.MULTIMODAL_CAPTION,
        "name": "BLIP Caption Base",
        "description": "图像描述生成模型，自动生成图像内容描述",
        "speed": "中等",
        "accuracy": "高",
    },
    "Salesforce/blip-image-captioning-large": {
        "category": ModelCategory.MULTIMODAL_CAPTION,
        "name": "BLIP Caption Large",
        "description": "大规模图像描述模型，更丰富的描述",
        "speed": "较慢",
        "accuracy": "很高",
    },
    # 多模态 - VQA
    "Salesforce/blip-vqa-base": {
        "category": ModelCategory.MULTIMODAL_VQA,
        "name": "BLIP VQA Base",
        "description": "视觉问答模型，可回答关于图像的问题",
        "speed": "中等",
        "accuracy": "高",
    },
}

# 类别显示名称
_CATEGORY_DISPLAY_NAMES = {
    ModelCategory.YOLO_DETECT: "YOLO 检测",
    ModelCategory.YOLO_SEGMENT: "YOLO 分割",
    ModelCategory.YOLO_POSE: "YOLO 姿态",
    ModelCategory.HF_DETR: "DETR 检测",
    ModelCategory.HF_OWLVIT: "开放词汇检测",
    ModelCategory.HF_GROUNDING_DINO: "Grounding DINO",
    ModelCategory.MULTIMODAL_CAPTION: "图像描述",
    ModelCategory.MULTIMODAL_VQA: "视觉问答",
}


class HandlerRegistry:
    """处理器注册表 - 根据模型 ID 获取对应 Handler"""

    def __init__(self, device: str):
        self._device = device
        self._handler_cache: dict[str, BaseHandler] = {}

    def get_handler(self, model_id: str) -> BaseHandler:
        """获取模型对应的处理器实例（带缓存）"""
        category = self._resolve_category(model_id)
        handler_cls = _CATEGORY_HANDLER_MAP.get(category)
        if handler_cls is None:
            raise ValueError(f"Unknown model category for {model_id}")

        cls_name = handler_cls.__name__
        if cls_name not in self._handler_cache:
            self._handler_cache[cls_name] = handler_cls(self._device)
        return self._handler_cache[cls_name]

    @staticmethod
    def _resolve_category(model_id: str) -> str:
        """推断模型类别"""
        info = MODEL_REGISTRY.get(model_id)
        if info:
            return info["category"]

        # 未注册的 .pt 文件按 YOLO 处理
        if model_id.endswith(".pt"):
            lower = model_id.lower()
            if "seg" in lower:
                return ModelCategory.YOLO_SEGMENT
            if "pose" in lower:
                return ModelCategory.YOLO_POSE
            return ModelCategory.YOLO_DETECT

        # 按名称模式猜测 HuggingFace 模型
        lower = model_id.lower()
        if "detr" in lower:
            return ModelCategory.HF_DETR
        if "owlvit" in lower:
            return ModelCategory.HF_OWLVIT
        if "grounding" in lower or "dino" in lower:
            return ModelCategory.HF_GROUNDING_DINO
        if "blip" in lower and "vqa" in lower:
            return ModelCategory.MULTIMODAL_VQA
        if "blip" in lower and ("caption" in lower or "captioning" in lower):
            return ModelCategory.MULTIMODAL_CAPTION

        # 含 / 的尝试作为 DETR 兜底
        if "/" in model_id:
            return ModelCategory.HF_DETR

        raise ValueError(f"Unknown model: {model_id}")


def get_available_models() -> dict[str, dict[str, Any]]:
    """获取可用模型列表，按类别分组"""
    categories: dict[str, dict[str, Any]] = {}
    for cat_key, display_name in _CATEGORY_DISPLAY_NAMES.items():
        categories[cat_key] = {"name": display_name, "models": []}

    for model_id, info in MODEL_REGISTRY.items():
        cat = info.get("category", "")
        if cat in categories:
            categories[cat]["models"].append(
                {
                    "id": model_id,
                    "name": info.get("name", model_id),
                    "description": info.get("description", ""),
                    "speed": info.get("speed", ""),
                    "accuracy": info.get("accuracy", ""),
                }
            )

    return {k: v for k, v in categories.items() if v["models"]}


def get_model_info(model_id: str) -> dict[str, Any] | None:
    """获取模型信息"""
    return MODEL_REGISTRY.get(model_id)
