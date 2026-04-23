"""
HFHandler 单元测试 - 测试 HuggingFace 模型处理器的加载和推理逻辑

测试覆盖：
- DETRHandler 的加载和推理
- OWLViTHandler 的加载和推理
- GroundingDINOHandler 的加载和推理
- 文本查询参数处理
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.handlers.hf_handler import (
    DETRHandler,
    GroundingDINOHandler,
    OWLViTHandler,
)

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def test_image():
    """创建测试图像"""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture()
def mock_torch():
    """Mock torch 模块"""
    mock = MagicMock()
    mock.no_grad.return_value.__enter__ = MagicMock(return_value=None)
    mock.no_grad.return_value.__exit__ = MagicMock(return_value=None)
    mock.tensor = lambda x: MagicMock()
    return mock


@pytest.fixture()
def mock_detr_outputs():
    """创建模拟的 DETR 输出"""
    outputs = {
        "scores": MagicMock(),
        "labels": MagicMock(),
        "boxes": MagicMock(),
    }
    outputs["scores"].cpu.return_value.numpy.return_value = np.array([0.95, 0.75])
    outputs["labels"].cpu.return_value.numpy.return_value = np.array([1, 2])
    outputs["boxes"].cpu.return_value.numpy.return_value = np.array(
        [[10.0, 20.0, 100.0, 200.0], [50.0, 60.0, 150.0, 160.0]]
    )
    return outputs


@pytest.fixture()
def mock_owlvit_outputs():
    """创建模拟的 OWL-ViT 输出"""
    outputs = {
        "scores": MagicMock(),
        "labels": MagicMock(),
        "boxes": MagicMock(),
    }
    outputs["scores"].cpu.return_value.numpy.return_value = np.array([0.85])
    outputs["labels"].cpu.return_value.numpy.return_value = np.array([0])
    outputs["boxes"].cpu.return_value.numpy.return_value = np.array([[20.0, 30.0, 80.0, 90.0]])
    return outputs


# ------------------------------------------------------------------
# DETRHandler Tests
# ------------------------------------------------------------------


class TestDETRHandler:
    """DETR 处理器测试"""

    @pytest.fixture()
    def handler(self):
        return DETRHandler(device="cpu")

    def test_load_success(self, handler: DETRHandler):
        """测试成功加载 DETR 模型"""
        mock_model = MagicMock()
        mock_model.config = MagicMock()
        mock_model.config.id2label = {1: "person", 2: "car"}
        mock_processor = MagicMock()

        with (
            patch(
                "transformers.DetrForObjectDetection.from_pretrained",
                return_value=mock_model,
            ),
            patch(
                "transformers.DetrImageProcessor.from_pretrained",
                return_value=mock_processor,
            ),
        ):
            model, processor = handler.load("facebook/detr-resnet-50")
            assert model is mock_model
            assert processor is mock_processor

    def test_infer_detection(
        self,
        handler: DETRHandler,
        test_image: np.ndarray,
        mock_detr_outputs: dict,
    ):
        """测试 DETR 推理"""
        mock_model = MagicMock()
        mock_model.config.id2label = {1: "person", 2: "car"}
        mock_model.return_value = mock_detr_outputs

        mock_processor = MagicMock()
        mock_processor.return_value = {"pixel_values": MagicMock()}
        mock_processor.post_process_object_detection.return_value = [mock_detr_outputs]

        # Mock BGR to PIL conversion
        with patch.object(handler, "bgr_to_pil") as mock_bgr_to_pil:
            mock_bgr_to_pil.return_value = MagicMock(size=(640, 480))

            result = handler.infer(mock_model, mock_processor, test_image, conf=0.5)

        assert result["task"] == "detect"
        assert result["width"] == 640
        assert result["height"] == 480
        assert "detections" in result
        assert result["inference_time"] > 0

    def test_infer_with_custom_conf(
        self,
        handler: DETRHandler,
        test_image: np.ndarray,
    ):
        """测试自定义置信度阈值"""
        mock_model = MagicMock()
        mock_model.config.id2label = {}
        mock_processor = MagicMock()
        mock_processor.post_process_object_detection.return_value = [
            {"scores": MagicMock(), "labels": MagicMock(), "boxes": MagicMock()}
        ]

        with patch.object(handler, "bgr_to_pil"):
            handler.infer(mock_model, mock_processor, test_image, conf=0.8)

        # 验证 conf 被传递给后处理
        call_kwargs = mock_processor.post_process_object_detection.call_args[1]
        assert call_kwargs["threshold"] == 0.8


# ------------------------------------------------------------------
# OWLViTHandler Tests
# ------------------------------------------------------------------


class TestOWLViTHandler:
    """OWL-ViT 处理器测试"""

    @pytest.fixture()
    def handler(self):
        return OWLViTHandler(device="cpu")

    def test_load_success(self, handler: OWLViTHandler):
        """测试成功加载 OWL-ViT 模型"""
        mock_model = MagicMock()
        mock_processor = MagicMock()

        with (
            patch(
                "transformers.AutoModelForZeroShotObjectDetection.from_pretrained",
                return_value=mock_model,
            ),
            patch(
                "transformers.AutoProcessor.from_pretrained",
                return_value=mock_processor,
            ),
        ):
            model, processor = handler.load("google/owlvit-base-patch32")
            assert model is mock_model
            assert processor is mock_processor

    def test_infer_with_text_queries(
        self,
        handler: OWLViTHandler,
        test_image: np.ndarray,
        mock_owlvit_outputs: dict,
    ):
        """测试使用文本查询的 OWL-ViT 推理"""
        mock_model = MagicMock()
        mock_model.return_value = mock_owlvit_outputs

        mock_processor = MagicMock()
        mock_processor.post_process_object_detection.return_value = [mock_owlvit_outputs]

        with patch.object(handler, "bgr_to_pil"):
            result = handler.infer(
                mock_model,
                mock_processor,
                test_image,
                conf=0.1,
                text_queries=["cat", "dog"],
            )

        assert result["task"] == "detect"
        assert result["text_queries"] == ["cat", "dog"]
        assert "detections" in result

    def test_infer_default_queries(
        self,
        handler: OWLViTHandler,
        test_image: np.ndarray,
        mock_owlvit_outputs: dict,
    ):
        """测试默认查询词"""
        mock_model = MagicMock()
        mock_model.return_value = mock_owlvit_outputs
        mock_processor = MagicMock()
        mock_processor.post_process_object_detection.return_value = [mock_owlvit_outputs]

        with patch.object(handler, "bgr_to_pil"):
            result = handler.infer(mock_model, mock_processor, test_image)

        assert result["text_queries"] == ["object"]

    def test_infer_label_from_queries(
        self,
        handler: OWLViTHandler,
        test_image: np.ndarray,
        mock_owlvit_outputs: dict,
    ):
        """测试从查询词获取标签"""
        mock_owlvit_outputs["labels"].cpu.return_value.numpy.return_value = np.array([1])
        mock_model = MagicMock()
        mock_model.return_value = mock_owlvit_outputs
        mock_processor = MagicMock()
        mock_processor.post_process_object_detection.return_value = [mock_owlvit_outputs]

        with patch.object(handler, "bgr_to_pil"):
            result = handler.infer(
                mock_model,
                mock_processor,
                test_image,
                text_queries=["cat", "dog", "bird"],
            )

        # label index 1 should map to "dog"
        assert result["detections"][0]["label"] == "dog"


# ------------------------------------------------------------------
# GroundingDINOHandler Tests
# ------------------------------------------------------------------


class TestGroundingDINOHandler:
    """Grounding DINO 处理器测试"""

    @pytest.fixture()
    def handler(self):
        return GroundingDINOHandler(device="cpu")

    def test_load_success(self, handler: GroundingDINOHandler):
        """测试成功加载 Grounding DINO 模型"""
        mock_model = MagicMock()
        mock_processor = MagicMock()

        with (
            patch(
                "transformers.AutoModelForZeroShotObjectDetection.from_pretrained",
                return_value=mock_model,
            ),
            patch(
                "transformers.AutoProcessor.from_pretrained",
                return_value=mock_processor,
            ),
        ):
            model, processor = handler.load("IDEA-Research/grounding-dino-tiny")
            assert model is mock_model
            assert processor is mock_processor

    def test_infer_with_text_queries(
        self,
        handler: GroundingDINOHandler,
        test_image: np.ndarray,
    ):
        """测试使用文本查询的 Grounding DINO 推理"""
        mock_model = MagicMock()
        mock_model.return_value = {}

        mock_processor = MagicMock()
        mock_processor.post_process_grounded_object_detection.return_value = [
            {
                "boxes": MagicMock(),
                "scores": MagicMock(),
                "labels": ["a cat"],
            }
        ]
        # Mock detach for numpy conversion
        mock_processor.post_process_grounded_object_detection.return_value[0][
            "boxes"
        ].detach.return_value.cpu.return_value.numpy.return_value = np.array(
            [[10.0, 20.0, 100.0, 200.0]]
        )
        mock_processor.post_process_grounded_object_detection.return_value[0][
            "scores"
        ].detach.return_value.cpu.return_value.numpy.return_value = np.array([0.9])

        with patch.object(handler, "bgr_to_pil"):
            result = handler.infer(
                mock_model,
                mock_processor,
                test_image,
                conf=0.25,
                text_queries=["cat"],
            )

        assert result["task"] == "detect"
        assert result["text_queries"] == ["cat"]

    def test_prepare_labels_with_articles(self, handler: GroundingDINOHandler):
        """测试标签预处理 - 已有冠词"""
        labels = GroundingDINOHandler._prepare_labels(["a cat", "the dog", "an apple"])
        assert labels == ["a cat", "the dog", "an apple"]

    def test_prepare_labels_without_articles(self, handler: GroundingDINOHandler):
        """测试标签预处理 - 添加冠词"""
        labels = GroundingDINOHandler._prepare_labels(["cat", "dog", "bird"])
        assert labels == ["a cat", "a dog", "a bird"]

    def test_prepare_labels_empty_queries(self, handler: GroundingDINOHandler):
        """测试标签预处理 - 空查询"""
        labels = GroundingDINOHandler._prepare_labels([])
        assert labels == ["a object"]

    def test_prepare_labels_whitespace_queries(self, handler: GroundingDINOHandler):
        """测试标签预处理 - 空白查询"""
        labels = GroundingDINOHandler._prepare_labels(["  ", "cat", ""])
        assert labels == ["a cat"]

    def test_infer_empty_results(
        self,
        handler: GroundingDINOHandler,
        test_image: np.ndarray,
    ):
        """测试空结果处理"""
        mock_model = MagicMock()
        mock_model.return_value = {}

        mock_processor = MagicMock()
        mock_processor.post_process_grounded_object_detection.return_value = [
            {
                "boxes": MagicMock(),
                "scores": MagicMock(),
                "labels": [],
            }
        ]
        mock_processor.post_process_grounded_object_detection.return_value[0][
            "boxes"
        ].detach.return_value.cpu.return_value.numpy.return_value = np.zeros((0, 4))
        mock_processor.post_process_grounded_object_detection.return_value[0][
            "scores"
        ].detach.return_value.cpu.return_value.numpy.return_value = np.zeros((0,))

        with patch.object(handler, "bgr_to_pil"):
            result = handler.infer(mock_model, mock_processor, test_image)

        assert result["detections"] == []


# ------------------------------------------------------------------
# Error Handling Tests
# ------------------------------------------------------------------


class TestHFHandlerErrors:
    """HuggingFace 处理器错误处理测试"""

    def test_detr_infer_error(self, test_image: np.ndarray):
        """测试 DETR 推理异常"""
        handler = DETRHandler(device="cpu")
        mock_model = MagicMock()
        mock_model.side_effect = RuntimeError("Model error")
        mock_processor = MagicMock()

        with (
            patch.object(handler, "bgr_to_pil"),
            pytest.raises(RuntimeError, match="Model error"),
        ):
            handler.infer(mock_model, mock_processor, test_image)

    def test_owlvit_infer_error(self, test_image: np.ndarray):
        """测试 OWL-ViT 推理异常"""
        handler = OWLViTHandler(device="cpu")
        mock_model = MagicMock()
        mock_model.side_effect = RuntimeError("Inference failed")
        mock_processor = MagicMock()

        with (
            patch.object(handler, "bgr_to_pil"),
            pytest.raises(RuntimeError, match="Inference failed"),
        ):
            handler.infer(mock_model, mock_processor, test_image)

    def test_grounding_dino_missing_post_process(self, test_image: np.ndarray):
        """测试 Grounding DINO 缺少后处理方法"""
        handler = GroundingDINOHandler(device="cpu")
        mock_model = MagicMock()
        mock_model.return_value = {}
        mock_processor = MagicMock()
        # 删除 post_process_grounded_object_detection 方法
        delattr(mock_processor, "post_process_grounded_object_detection")

        with (
            patch.object(handler, "bgr_to_pil"),
            pytest.raises(RuntimeError, match="transformers 版本过低"),
        ):
            handler.infer(mock_model, mock_processor, test_image)
