"""
BLIPHandler 单元测试 - 测试 BLIP 多模态处理器的加载和推理逻辑

测试覆盖：
- BLIPCaptionHandler 的加载和推理
- BLIPVQAHandler 的加载和推理
- 参数传递和结果格式
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.handlers.blip_handler import BLIPCaptionHandler, BLIPVQAHandler

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def test_image():
    """创建测试图像"""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture()
def mock_blip_caption_model():
    """创建模拟的 BLIP Caption 模型"""
    model = MagicMock()
    model.generate.return_value = [[101, 202, 303]]  # 模拟 token IDs
    return model


@pytest.fixture()
def mock_blip_caption_processor():
    """创建模拟的 BLIP Caption processor"""
    processor = MagicMock()
    processor.return_value = {"pixel_values": MagicMock(), "input_ids": MagicMock()}
    processor.decode.return_value = "a cat sitting on a couch"
    return processor


@pytest.fixture()
def mock_blip_vqa_model():
    """创建模拟的 BLIP VQA 模型"""
    model = MagicMock()
    model.generate.return_value = [[101, 202, 303]]
    return model


@pytest.fixture()
def mock_blip_vqa_processor():
    """创建模拟的 BLIP VQA processor"""
    processor = MagicMock()
    processor.return_value = {"pixel_values": MagicMock(), "input_ids": MagicMock()}
    processor.decode.return_value = "orange"
    return processor


# ------------------------------------------------------------------
# BLIPCaptionHandler Tests
# ------------------------------------------------------------------


class TestBLIPCaptionHandler:
    """BLIP Caption 处理器测试"""

    @pytest.fixture()
    def handler(self):
        return BLIPCaptionHandler(device="cpu")

    def test_load_success(self, handler: BLIPCaptionHandler):
        """测试成功加载 BLIP Caption 模型"""
        mock_model = MagicMock()
        mock_processor = MagicMock()

        with (
            patch("app.handlers.blip_handler._require_hf"),
            patch("transformers.BlipProcessor.from_pretrained", return_value=mock_processor),
            patch(
                "transformers.BlipForConditionalGeneration.from_pretrained",
                return_value=mock_model,
            ),
            patch.object(handler, "_model_to_device", return_value=mock_model) as mock_to_device,
        ):
            model, processor = handler.load("Salesforce/blip-image-captioning-base")

        assert model is mock_model
        assert processor is mock_processor
        mock_to_device.assert_called_once_with(mock_model)

    def test_infer_caption(
        self,
        handler: BLIPCaptionHandler,
        test_image: np.ndarray,
        mock_blip_caption_model: MagicMock,
        mock_blip_caption_processor: MagicMock,
    ):
        """测试图像描述生成"""
        result = handler.infer(
            mock_blip_caption_model,
            mock_blip_caption_processor,
            test_image,
        )

        assert result["task"] == "caption"
        assert result["width"] == 640
        assert result["height"] == 480
        assert "caption" in result
        assert result["caption"] == "a cat sitting on a couch"
        assert result["inference_time"] > 0

    def test_infer_calls_processor(
        self,
        handler: BLIPCaptionHandler,
        test_image: np.ndarray,
        mock_blip_caption_model: MagicMock,
        mock_blip_caption_processor: MagicMock,
    ):
        """测试 processor 被正确调用"""
        handler.infer(mock_blip_caption_model, mock_blip_caption_processor, test_image)

        # 验证 processor 被调用
        mock_blip_caption_processor.assert_called_once()

    def test_infer_calls_model_generate(
        self,
        handler: BLIPCaptionHandler,
        test_image: np.ndarray,
        mock_blip_caption_model: MagicMock,
        mock_blip_caption_processor: MagicMock,
    ):
        """测试模型 generate 被调用"""
        handler.infer(mock_blip_caption_model, mock_blip_caption_processor, test_image)

        # 验证 generate 被调用
        mock_blip_caption_model.generate.assert_called_once()

    def test_infer_decoder_call(
        self,
        handler: BLIPCaptionHandler,
        test_image: np.ndarray,
        mock_blip_caption_model: MagicMock,
        mock_blip_caption_processor: MagicMock,
    ):
        """测试 decode 被正确调用"""
        handler.infer(mock_blip_caption_model, mock_blip_caption_processor, test_image)

        # 验证 decode 被调用
        mock_blip_caption_processor.decode.assert_called_once_with(
            [101, 202, 303], skip_special_tokens=True
        )

    def test_infer_error(
        self,
        handler: BLIPCaptionHandler,
        test_image: np.ndarray,
    ):
        """测试推理异常处理"""
        mock_model = MagicMock()
        mock_model.generate.side_effect = RuntimeError("CUDA error")
        mock_processor = MagicMock()

        with pytest.raises(RuntimeError, match="CUDA error"):
            handler.infer(mock_model, mock_processor, test_image)


# ------------------------------------------------------------------
# BLIPVQAHandler Tests
# ------------------------------------------------------------------


class TestBLIPVQAHandler:
    """BLIP VQA 处理器测试"""

    @pytest.fixture()
    def handler(self):
        return BLIPVQAHandler(device="cpu")

    def test_load_success(self, handler: BLIPVQAHandler):
        """测试成功加载 BLIP VQA 模型"""
        mock_model = MagicMock()
        mock_processor = MagicMock()

        with (
            patch("app.handlers.blip_handler._require_hf"),
            patch("transformers.BlipProcessor.from_pretrained", return_value=mock_processor),
            patch(
                "transformers.BlipForQuestionAnswering.from_pretrained",
                return_value=mock_model,
            ),
            patch.object(handler, "_model_to_device", return_value=mock_model) as mock_to_device,
        ):
            model, processor = handler.load("Salesforce/blip-vqa-base")

        assert model is mock_model
        assert processor is mock_processor
        mock_to_device.assert_called_once_with(mock_model)

    def test_infer_vqa(
        self,
        handler: BLIPVQAHandler,
        test_image: np.ndarray,
        mock_blip_vqa_model: MagicMock,
        mock_blip_vqa_processor: MagicMock,
    ):
        """测试视觉问答"""
        result = handler.infer(
            mock_blip_vqa_model,
            mock_blip_vqa_processor,
            test_image,
            question="What color is the cat?",
        )

        assert result["task"] == "vqa"
        assert result["width"] == 640
        assert result["height"] == 480
        assert "answer" in result
        assert result["answer"] == "orange"
        assert result["question"] == "What color is the cat?"
        assert result["inference_time"] > 0

    def test_infer_default_question(
        self,
        handler: BLIPVQAHandler,
        test_image: np.ndarray,
        mock_blip_vqa_model: MagicMock,
        mock_blip_vqa_processor: MagicMock,
    ):
        """测试默认问题"""
        result = handler.infer(
            mock_blip_vqa_model,
            mock_blip_vqa_processor,
            test_image,
        )

        assert result["question"] == "What is in this image?"

    def test_infer_processor_with_question(
        self,
        handler: BLIPVQAHandler,
        test_image: np.ndarray,
        mock_blip_vqa_model: MagicMock,
        mock_blip_vqa_processor: MagicMock,
    ):
        """测试 processor 接收到问题"""
        handler.infer(
            mock_blip_vqa_model,
            mock_blip_vqa_processor,
            test_image,
            question="How many cats?",
        )

        # 验证 processor 被调用且包含问题
        call_args = mock_blip_vqa_processor.call_args
        assert call_args[0][1] == "How many cats?"

    def test_infer_error(
        self,
        handler: BLIPVQAHandler,
        test_image: np.ndarray,
    ):
        """测试推理异常处理"""
        mock_model = MagicMock()
        mock_model.generate.side_effect = RuntimeError("Model error")
        mock_processor = MagicMock()

        with pytest.raises(RuntimeError, match="Model error"):
            handler.infer(mock_model, mock_processor, test_image, question="test?")


# ------------------------------------------------------------------
# Device Handling Tests
# ------------------------------------------------------------------


class TestBlipDeviceHandling:
    """设备处理测试"""

    def test_caption_handler_cuda_device(self):
        """测试 CUDA 设备上的 Caption Handler"""
        handler = BLIPCaptionHandler(device="cuda:0")
        assert handler.device == "cuda:0"

    def test_vqa_handler_cuda_device(self):
        """测试 CUDA 设备上的 VQA Handler"""
        handler = BLIPVQAHandler(device="cuda:0")
        assert handler.device == "cuda:0"

    def test_model_to_device_called(self, test_image: np.ndarray):
        """测试模型被移动到设备"""
        handler = BLIPCaptionHandler(device="cuda:0")
        mock_model = MagicMock()

        # 直接测试 _model_to_device 方法
        result = handler._model_to_device(mock_model)
        assert result is not None


# ------------------------------------------------------------------
# BGR to PIL Conversion Tests
# ------------------------------------------------------------------


class TestBgrToPil:
    """BGR 到 PIL 转换测试"""

    def test_bgr_to_pil_conversion(self, test_image: np.ndarray):
        """测试 BGR 到 PIL 转换"""
        from app.handlers.base import BaseHandler

        pil_image = BaseHandler.bgr_to_pil(test_image)

        assert pil_image.size == (640, 480)
        assert pil_image.mode == "RGB"

    def test_bgr_to_pil_color_order(self):
        """测试颜色通道顺序"""
        from app.handlers.base import BaseHandler

        # 创建纯蓝色 BGR 图像 (B=255, G=0, R=0)
        bgr_image = np.zeros((100, 100, 3), dtype=np.uint8)
        bgr_image[:, :, 0] = 255  # B channel

        pil_image = BaseHandler.bgr_to_pil(bgr_image)

        # BGR 的蓝色在 RGB 中应该是 (R=0, G=0, B=255)
        pixel = pil_image.getpixel((50, 50))
        assert pixel[0] == 0  # R
        assert pixel[1] == 0  # G
        assert pixel[2] == 255  # B
