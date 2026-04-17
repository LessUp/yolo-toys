"""
共享测试 fixtures - 统一管理测试依赖

所有测试共享的 fixtures 定义在此文件中，避免在每个测试文件中重复定义。
"""

import io
import os
from types import SimpleNamespace
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """创建 FastAPI 测试客户端（模块级别，只初始化一次）"""
    os.environ.setdefault("SKIP_WARMUP", "1")
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def image_bytes() -> bytes:
    """创建测试用的 PNG 图像字节"""
    img = Image.new("RGB", (32, 32), (255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture()
def image_bytes_jpeg() -> bytes:
    """创建测试用的 JPEG 图像字节"""
    img = Image.new("RGB", (32, 32), (0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


@pytest.fixture()
def large_image_bytes() -> bytes:
    """创建较大的测试图像（用于测试文件大小限制）"""
    img = Image.new("RGB", (640, 480), (0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture()
def mock_infer(monkeypatch: pytest.MonkeyPatch):
    """Mock model_manager.infer 方法，返回模拟的推理结果"""
    from app.model_manager import model_manager

    def fake_infer(*, model_id: str, image, text_queries=None, question=None, **kwargs):
        h, w = image.shape[:2]
        if model_id == "unknown":
            raise ValueError("Unknown model category for unknown")
        if model_id.startswith("Salesforce/blip-image-captioning"):
            return {
                "width": w,
                "height": h,
                "caption": "test caption",
                "inference_time": 1.0,
                "task": "caption",
            }
        if model_id.startswith("Salesforce/blip-vqa"):
            return {
                "width": w,
                "height": h,
                "question": question or "",
                "answer": "test answer",
                "inference_time": 2.0,
                "task": "vqa",
            }
        return {
            "width": w,
            "height": h,
            "detections": [
                {
                    "bbox": [0.0, 0.0, 10.0, 10.0],
                    "score": 0.9,
                    "label": "obj",
                }
            ],
            "inference_time": 3.0,
            "task": "detect",
            "text_queries": text_queries,
        }

    monkeypatch.setattr(model_manager, "infer", fake_infer)
    return fake_infer


@pytest.fixture()
def mock_load_model(monkeypatch: pytest.MonkeyPatch):
    """Mock model_manager.load_model 方法"""
    from app.model_manager import model_manager

    def fake_load_model(model_id: str):
        return SimpleNamespace(model=SimpleNamespace(names={0: "cat", 1: "person"}))

    monkeypatch.setattr(model_manager, "load_model", fake_load_model)
    return fake_load_model


@pytest.fixture()
def mock_load_model_with_names(monkeypatch: pytest.MonkeyPatch):
    """Mock model_manager.load_model，支持自定义标签"""

    def create_mock(names):
        from app.model_manager import model_manager

        def fake_load_model(model_id: str):
            return SimpleNamespace(model=SimpleNamespace(names=names))

        monkeypatch.setattr(model_manager, "load_model", fake_load_model)
        return fake_load_model

    return create_mock
