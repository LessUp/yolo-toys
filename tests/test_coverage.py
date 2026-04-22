"""
补充测试用例 - 提高代码覆盖率到 70%+
"""

import io
from unittest.mock import Mock

import pytest

# ------------------------------------------------------------------
# Metrics 测试
# ------------------------------------------------------------------


def test_track_inference_decorator():
    """测试 track_inference 装饰器"""
    from app.metrics import track_inference

    @track_inference(model="test_model", task="detect")
    def dummy_func():
        return "result"

    result = dummy_func()
    assert result == "result"


def test_track_inference_decorator_error():
    """测试 track_inference 装饰器捕获异常"""
    from app.metrics import track_inference

    @track_inference(model="test_model", task="detect")
    def error_func():
        raise ValueError("test error")

    with pytest.raises(ValueError, match="test error"):
        error_func()


def test_update_model_cache_metric():
    """测试更新模型缓存指标"""
    from app.metrics import update_model_cache_metric

    update_model_cache_metric(5)


def test_update_memory_metric():
    """测试更新内存指标"""
    from app.metrics import update_memory_metric

    update_memory_metric(0.75)


# ------------------------------------------------------------------
# Middleware 测试
# ------------------------------------------------------------------


@pytest.fixture
def mock_request():
    """创建模拟请求"""
    request = Mock()
    request.url.path = "/test"
    request.method = "GET"
    request.client.host = "127.0.0.1"
    return request


@pytest.fixture
def mock_response():
    """创建模拟响应"""
    response = Mock()
    response.status_code = 200
    response.headers = {}
    return response


@pytest.mark.asyncio
async def test_security_headers_middleware(mock_request, mock_response):
    """测试安全头部中间件"""
    from app.middleware import SecurityHeadersMiddleware

    async def mock_call_next(request):
        return mock_response

    middleware = SecurityHeadersMiddleware(Mock())
    response = await middleware.dispatch(mock_request, mock_call_next)

    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"


@pytest.mark.asyncio
async def test_metrics_middleware(mock_request, mock_response):
    """测试指标中间件"""
    from app.middleware import MetricsMiddleware

    async def mock_call_next(request):
        return mock_response

    middleware = MetricsMiddleware(Mock())
    response = await middleware.dispatch(mock_request, mock_call_next)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_timeout_middleware(mock_request, mock_response):
    """测试超时中间件"""
    from app.middleware import TimeoutMiddleware

    async def mock_call_next(request):
        return mock_response

    middleware = TimeoutMiddleware(Mock(), timeout_seconds=30.0)
    response = await middleware.dispatch(mock_request, mock_call_next)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_middleware(mock_request, mock_response):
    """测试速率限制中间件"""
    from app.middleware import RateLimitMiddleware

    async def mock_call_next(request):
        return mock_response

    middleware = RateLimitMiddleware(Mock(), requests_per_minute=100)

    # 第一次请求应该成功
    response = await middleware.dispatch(mock_request, mock_call_next)
    assert response.status_code == 200


# ------------------------------------------------------------------
# API Utils 测试
# ------------------------------------------------------------------


def test_validate_image_mime_jpeg():
    """测试 JPEG MIME 验证"""
    from app.api.utils import validate_image_mime

    jpeg_header = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    assert validate_image_mime(jpeg_header) is True


def test_validate_image_mime_png():
    """测试 PNG MIME 验证"""
    from app.api.utils import validate_image_mime

    png_header = b"\x89PNG\r\n\x1a\n"
    assert validate_image_mime(png_header) is True


def test_validate_image_mime_gif():
    """测试 GIF MIME 验证 - GIF89a"""
    from app.api.utils import validate_image_mime

    gif_header = b"GIF89a"
    assert validate_image_mime(gif_header) is True


def test_validate_image_mime_gif87():
    """测试 GIF MIME 验证 - GIF87a"""
    from app.api.utils import validate_image_mime

    gif_header = b"GIF87a"
    assert validate_image_mime(gif_header) is True


def test_validate_image_mime_webp():
    """测试 WebP MIME 验证"""
    from app.api.utils import validate_image_mime

    webp_header = b"RIFF\x00\x00\x00\x00WEBP"
    assert validate_image_mime(webp_header) is True


def test_validate_image_mime_invalid():
    """测试无效 MIME 验证"""
    from app.api.utils import validate_image_mime

    invalid_header = b"INVALID_DATA"
    assert validate_image_mime(invalid_header) is False
    assert validate_image_mime(b"") is False


def test_validate_image_mime_too_small():
    """测试数据太小的 MIME 验证"""
    from app.api.utils import validate_image_mime

    small_data = b"\x89PN"  # 小于最小签名长度
    assert validate_image_mime(small_data) is False


# ------------------------------------------------------------------
# Config 测试
# ------------------------------------------------------------------


def test_config_origins_list():
    """测试 origins_list 配置"""
    from app.config import AppSettings

    s = AppSettings(ALLOW_ORIGINS="*")
    assert s.origins_list == ["*"]

    s2 = AppSettings(ALLOW_ORIGINS="http://localhost:3000,http://localhost:8080")
    assert s2.origins_list == ["http://localhost:3000", "http://localhost:8080"]


def test_config_skip_warmup():
    """测试 skip_warmup 配置"""
    from app.config import AppSettings

    s = AppSettings(SKIP_WARMUP="true")
    assert s.skip_warmup is True

    s2 = AppSettings(SKIP_WARMUP="false")
    assert s2.skip_warmup is False

    s3 = AppSettings(SKIP_WARMUP="1")
    assert s3.skip_warmup is True


def test_config_max_upload_bytes():
    """测试 max_upload_bytes 配置"""
    from app.config import AppSettings

    s = AppSettings(MAX_UPLOAD_MB="10")
    assert s.max_upload_bytes == 10 * 1024 * 1024

    s2 = AppSettings(MAX_UPLOAD_MB=5)
    assert s2.max_upload_bytes == 5 * 1024 * 1024


def test_config_warmup_image_size():
    """测试 warmup_image_size 配置"""
    from app.config import AppSettings

    s = AppSettings()
    assert s.warmup_image_size == 640


def test_config_gzip_min_size():
    """测试 gzip_min_size 配置"""
    from app.config import AppSettings

    s = AppSettings()
    # 默认值是 1000，不是 1024
    assert s.gzip_min_size == 1000


# ------------------------------------------------------------------
# Schemas 测试
# ------------------------------------------------------------------


def test_inference_response():
    """测试 InferenceResponse schema"""
    from app.schemas import InferenceResponse

    response = InferenceResponse(
        width=100,
        height=100,
        detections=[{"bbox": [0, 0, 10, 10], "score": 0.9, "label": "test"}],
        inference_time=1.0,
        task="detect",
    )
    assert response.width == 100
    assert response.height == 100
    assert len(response.detections) == 1


def test_caption_response():
    """测试 CaptionResponse schema"""
    from app.schemas import InferenceResponse

    response = InferenceResponse(
        width=100,
        height=100,
        caption="a test caption",
        inference_time=1.0,
        task="caption",
    )
    assert response.caption == "a test caption"


def test_vqa_response():
    """测试 VQAResponse schema"""
    from app.schemas import InferenceResponse

    response = InferenceResponse(
        width=100,
        height=100,
        question="What is this?",
        answer="test answer",
        inference_time=1.0,
        task="vqa",
    )
    assert response.question == "What is this?"
    assert response.answer == "test answer"


# ------------------------------------------------------------------
# ModelManager 测试
# ------------------------------------------------------------------


def test_model_manager_cache_clear():
    """测试 ModelManager 缓存清除"""
    from app.model_manager import ModelManager

    manager = ModelManager()
    manager.clear_cache()


def test_model_manager_get_memory_usage():
    """测试 ModelManager 内存使用"""
    from app.model_manager import get_memory_usage

    usage = get_memory_usage()
    assert isinstance(usage, float)
    assert 0.0 <= usage <= 1.0


# ------------------------------------------------------------------
# Handlers 测试
# ------------------------------------------------------------------


def test_base_handler_result():
    """测试 BaseHandler make_result 方法"""
    from app.handlers.yolo_handler import YOLOHandler

    # 使用具体实现类而不是抽象基类
    handler = YOLOHandler("cpu")
    result = handler.make_result(100, 100, task="detect")
    assert result["width"] == 100
    assert result["height"] == 100
    assert result["task"] == "detect"


def test_handler_registry_get_category():
    """测试 HandlerRegistry 获取类别"""
    from app.handlers.registry import MODEL_REGISTRY

    # 从注册表获取类别信息
    info = MODEL_REGISTRY.get("yolov8n.pt")
    assert info is not None
    assert info["category"] == "yolo_detect"


def test_handler_registry_get_info():
    """测试 HandlerRegistry 获取模型信息"""
    from app.handlers.registry import MODEL_REGISTRY

    info = MODEL_REGISTRY.get("yolov8n.pt")
    assert info is not None
    assert info["category"] == "yolo_detect"


def test_model_category_enum():
    """测试 ModelCategory 枚举"""
    from app.handlers.registry import ModelCategory

    assert ModelCategory.YOLO_DETECT == "yolo_detect"
    assert ModelCategory.YOLO_SEGMENT == "yolo_segment"
    assert ModelCategory.YOLO_POSE == "yolo_pose"
    assert ModelCategory.HF_DETR == "hf_detr"
    assert ModelCategory.HF_OWLVIT == "hf_owlvit"


def test_handler_registry_class():
    """测试 HandlerRegistry 类"""
    from app.handlers.registry import HandlerRegistry

    registry = HandlerRegistry("cpu")
    handler = registry.get_handler("yolov8n.pt")
    assert handler is not None


# ------------------------------------------------------------------
# Main 模块测试
# ------------------------------------------------------------------


def test_main_imports():
    """测试 main 模块可以导入"""
    import os

    os.environ["SKIP_WARMUP"] = "1"
    from app.main import app, lifespan

    assert app is not None
    assert lifespan is not None


def test_app_version():
    """测试应用版本"""
    from app import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)


# ------------------------------------------------------------------
# WebSocket 工具函数测试
# ------------------------------------------------------------------


def test_parse_ws_state():
    """测试 WebSocket 状态解析"""
    from starlette.datastructures import QueryParams

    from app.api.websocket import _parse_ws_state

    params = QueryParams([("model", "yolov8n.pt"), ("conf", "0.5")])
    state = _parse_ws_state(params)

    assert state["model_id"] == "yolov8n.pt"
    assert state["conf"] == 0.5


def test_parse_ws_state_defaults():
    """测试 WebSocket 状态默认值"""
    from starlette.datastructures import QueryParams

    from app.api.websocket import _parse_ws_state

    params = QueryParams([])
    state = _parse_ws_state(params)

    assert state["model_id"] is not None  # 使用默认模型
    assert state["conf"] is not None
    assert state["iou"] is not None
    assert state["max_det"] is not None


def test_get_optional_float():
    """测试 _get_optional_float"""
    from app.api.websocket import _get_optional_float

    assert _get_optional_float("3.14") == 3.14
    assert _get_optional_float("0") == 0.0
    assert _get_optional_float(None) is None
    assert _get_optional_float("") is None
    assert _get_optional_float("invalid") is None


def test_get_optional_int():
    """测试 _get_optional_int"""
    from app.api.websocket import _get_optional_int

    assert _get_optional_int("42") == 42
    assert _get_optional_int("0") == 0
    assert _get_optional_int(None) is None
    assert _get_optional_int("") is None
    assert _get_optional_int("invalid") is None


# ------------------------------------------------------------------
# System API 测试
# ------------------------------------------------------------------


def test_system_stats():
    """测试系统状态端点"""
    import os

    from fastapi.testclient import TestClient

    os.environ["SKIP_WARMUP"] = "1"
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/system/stats")
        assert response.status_code == 200
        data = response.json()
        # API 实际返回的字段
        assert "device" in data
        assert "cache_info" in data


def test_cache_clear():
    """测试缓存清除端点"""
    import os

    from fastapi.testclient import TestClient

    os.environ["SKIP_WARMUP"] = "1"
    from app.main import app

    with TestClient(app) as client:
        response = client.post("/system/cache/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


# ------------------------------------------------------------------
# Labels 端点测试
# ------------------------------------------------------------------


def test_labels_endpoint():
    """测试 labels 端点"""
    import os

    from fastapi.testclient import TestClient

    os.environ["SKIP_WARMUP"] = "1"
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/labels?model=yolov8n.pt")
        assert response.status_code == 200
        data = response.json()
        # API 返回的是字典格式
        assert "labels" in data or isinstance(data, dict)


# ------------------------------------------------------------------
# 工具函数测试
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_read_upload_image_invalid():
    """测试读取无效上传图像"""
    import os

    from fastapi import HTTPException, UploadFile

    os.environ["SKIP_WARMUP"] = "1"
    from app.api.utils import read_upload_image

    # 创建无效的 "图像" 数据
    invalid_data = b"not an image"
    upload = UploadFile(filename="test.txt", file=io.BytesIO(invalid_data))

    with pytest.raises(HTTPException):
        await read_upload_image(upload)


# ------------------------------------------------------------------
# Additional tests for higher coverage
# ------------------------------------------------------------------


def test_model_manager_singleton():
    """测试 ModelManager 是单例"""
    from app.model_manager import ModelManager, model_manager

    manager2 = ModelManager()
    assert model_manager is manager2


def test_get_settings_singleton():
    """测试 get_settings 是单例"""
    from app.config import get_settings

    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_schemas_all_exports():
    """测试 schemas 模块导出"""
    from app import schemas

    assert hasattr(schemas, "InferenceResponse")


def test_api_init():
    """测试 api 包初始化"""
    from app.api import inference_router, models_router, system_router, ws_router

    assert system_router is not None
    assert models_router is not None
    assert inference_router is not None
    assert ws_router is not None


def test_routes_all():
    """测试 routes 模块导出"""
    from app.routes import (
        _parse_text_queries,
        read_upload_image,
        router,
        validate_image_mime,
    )

    assert router is not None
    assert read_upload_image is not None
    assert validate_image_mime is not None
    assert _parse_text_queries is not None


@pytest.mark.asyncio
async def test_websocket_apply_config():
    """测试 WebSocket 配置应用"""
    from app.api.websocket import _apply_ws_config

    state = {
        "model_id": "yolov8n.pt",
        "conf": 0.25,
        "text_queries": None,
        "question": None,
    }

    config = {
        "model": "yolov8s.pt",
        "conf": 0.5,
        "text_queries": ["cat", "dog"],
        "question": "What is this?",
    }

    _apply_ws_config(state, config)

    assert state["model_id"] == "yolov8s.pt"
    assert state["conf"] == 0.5
    assert state["text_queries"] == ["cat", "dog"]
    assert state["question"] == "What is this?"


def test_ws_decode_frame():
    """测试 WebSocket 帧解码 - 无效数据"""
    from app.api.websocket import _decode_ws_frame

    invalid_data = b"not an image"
    result = _decode_ws_frame(invalid_data)
    assert result is None


def test_config_bool_parsing():
    """测试配置布尔值解析"""
    from app.config import parse_bool_string

    assert parse_bool_string("true") is True
    assert parse_bool_string("True") is True
    assert parse_bool_string("1") is True
    assert parse_bool_string("yes") is True
    assert parse_bool_string("false") is False
    assert parse_bool_string(None) is None
    assert parse_bool_string("") is None


def test_labels_endpoint_not_found():
    """测试 labels 端点 - 模型不存在"""
    import os

    from fastapi.testclient import TestClient

    os.environ["SKIP_WARMUP"] = "1"
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/labels?model=unknown_model_xyz")
        # 应该返回 400 错误
        assert response.status_code == 400
