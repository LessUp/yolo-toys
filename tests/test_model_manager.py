"""
ModelManager 单元测试 - 测试模型管理器的缓存和推理逻辑

测试覆盖：
- 缓存命中/未命中场景
- TTL 过期清理
- 缓存清理
- 并发模型加载
"""

import threading
from unittest.mock import MagicMock

import numpy as np
import pytest


class TestModelManagerCache:
    """ModelManager 缓存测试"""

    def test_cache_hit(self, monkeypatch):
        """测试缓存命中场景"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        # Mock handler 和 registry
        mock_model = MagicMock()
        mock_handler = MagicMock()
        mock_handler.load.return_value = (mock_model, None)

        monkeypatch.setattr(manager._registry, "get_handler", lambda _: mock_handler)

        # 第一次加载
        model1 = manager.load_model("yolov8n.pt")
        assert model1 is mock_model

        # 第二次应该命中缓存
        model2 = manager.load_model("yolov8n.pt")
        assert model1 is model2
        # load 只应该被调用一次
        mock_handler.load.assert_called_once()

    def test_cache_miss_different_models(self, monkeypatch):
        """测试不同模型的缓存未命中"""
        from app import model_manager
        from app.model_manager import ModelManager

        manager = ModelManager()
        monkeypatch.setattr(model_manager, "get_memory_usage", lambda: 0.0)

        models = {"yolov8n.pt": MagicMock(), "yolov8s.pt": MagicMock()}

        def mock_get_handler(model_id):
            handler = MagicMock()
            handler.load.return_value = (models[model_id], None)
            return handler

        monkeypatch.setattr(manager._registry, "get_handler", mock_get_handler)

        model1 = manager.load_model("yolov8n.pt")
        model2 = manager.load_model("yolov8s.pt")

        assert model1 is not model2
        assert len(manager.cache) == 2

    def test_cache_clear(self, monkeypatch):
        """测试缓存清理"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        mock_handler = MagicMock()
        mock_handler.load.return_value = (MagicMock(), None)
        monkeypatch.setattr(manager._registry, "get_handler", lambda _: mock_handler)

        # 加载模型
        manager.load_model("yolov8n.pt")
        assert len(manager.cache) == 1

        # 清理缓存
        manager.clear_cache()
        assert len(manager.cache) == 0

    def test_cache_info(self, monkeypatch):
        """测试缓存信息"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        mock_handler = MagicMock()
        mock_handler.load.return_value = (MagicMock(), None)
        monkeypatch.setattr(manager._registry, "get_handler", lambda _: mock_handler)

        manager.load_model("yolov8n.pt")
        info = manager.cache_info

        assert info["cache_size"] == 1
        assert "cache_maxsize" in info
        assert "cache_ttl" in info

    def test_cache_maxsize(self):
        """测试缓存最大大小限制"""
        from app.model_manager import ModelManager

        manager = ModelManager()
        maxsize = manager.cache.maxsize

        assert maxsize > 0
        assert isinstance(maxsize, int)

    def test_device_property(self):
        """测试设备属性"""
        from app.model_manager import ModelManager

        manager = ModelManager()
        device = manager.device

        assert device in ["cpu", "cuda:0", "mps"]

    def test_concurrent_load(self, monkeypatch):
        """测试并发模型加载安全性"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        mock_model = MagicMock()
        mock_handler = MagicMock()
        mock_handler.load.return_value = (mock_model, None)

        call_count = [0]

        def track_load(model_id):
            call_count[0] += 1
            return (mock_model, None)

        mock_handler.load.side_effect = track_load
        monkeypatch.setattr(manager._registry, "get_handler", lambda _: mock_handler)

        results = []
        errors = []

        def load_model():
            try:
                model = manager.load_model("yolov8n.pt")
                results.append(model)
            except Exception as e:
                errors.append(e)

        # 启动多个线程同时加载
        threads = [threading.Thread(target=load_model) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 应该成功
        assert len(errors) == 0
        assert len(results) == 5


class TestModelManagerInfer:
    """ModelManager 推理测试"""

    def test_infer_with_cached_model(self, monkeypatch):
        """测试使用缓存的模型进行推理"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        mock_model = MagicMock()
        mock_handler = MagicMock()
        mock_handler.load.return_value = (mock_model, None)
        mock_handler.infer.return_value = {
            "width": 640,
            "height": 480,
            "detections": [],
            "inference_time": 10.0,
            "task": "detect",
        }

        monkeypatch.setattr(manager._registry, "get_handler", lambda _: mock_handler)

        image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = manager.infer(model_id="yolov8n.pt", image=image)

        assert result["task"] == "detect"
        assert result["width"] == 640

    def test_infer_with_parameters(self, monkeypatch):
        """测试推理参数传递"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        mock_model = MagicMock()
        mock_handler = MagicMock()
        mock_handler.load.return_value = (mock_model, None)
        mock_handler.infer.return_value = {
            "width": 100,
            "height": 100,
            "detections": [],
            "inference_time": 5.0,
            "task": "detect",
        }

        monkeypatch.setattr(manager._registry, "get_handler", lambda _: mock_handler)

        image = np.zeros((100, 100, 3), dtype=np.uint8)
        manager.infer(
            model_id="yolov8n.pt",
            image=image,
            conf=0.5,
            iou=0.3,
            max_det=100,
        )

        # 验证参数被传递给 handler
        call_kwargs = mock_handler.infer.call_args[1]
        assert call_kwargs["conf"] == 0.5
        assert call_kwargs["iou"] == 0.3
        assert call_kwargs["max_det"] == 100


class TestModelManagerStats:
    """ModelManager 统计测试"""

    def test_get_stats(self, monkeypatch):
        """测试获取统计信息"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        mock_handler = MagicMock()
        mock_handler.load.return_value = (MagicMock(), None)
        monkeypatch.setattr(manager._registry, "get_handler", lambda _: mock_handler)

        stats = manager.get_stats()

        assert "cache_info" in stats
        assert "device" in stats
        assert "model_stats" in stats


class TestModelManagerValidation:
    """ModelManager 验证测试"""

    def test_invalid_model_id_empty(self):
        """测试空模型 ID"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        with pytest.raises(ValueError, match="non-empty string"):
            manager.load_model("")

    def test_invalid_model_id_none(self):
        """测试 None 模型 ID"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        with pytest.raises(ValueError, match="non-empty string"):
            manager.load_model(None)  # type: ignore

    def test_invalid_model_id_path_traversal(self):
        """测试路径遍历攻击"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        with pytest.raises(ValueError, match="forbidden character"):
            manager.load_model("../../../etc/passwd")

    def test_invalid_model_id_url_encoded(self):
        """测试 URL 编码路径遍历"""
        from app.model_manager import ModelManager

        manager = ModelManager()

        with pytest.raises(ValueError, match="forbidden character"):
            manager.load_model("%2e%2e%2fetc%2fpasswd")
