import io
import os
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

# 使用 conftest.py 中的共享 fixtures
# client, image_bytes, mock_infer 等 fixtures 从 conftest.py 导入


# ------------------------------------------------------------------
# 本地 fixtures (特定于本文件的测试数据)
# ------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
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
def mock_infer(monkeypatch):
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


# ------------------------------------------------------------------
# 基础端点
# ------------------------------------------------------------------


def test_health_ok(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert "version" in data
    assert "device" in data
    assert "default_model" in data
    assert "defaults" in data
    defaults = data["defaults"]
    assert "conf" in defaults
    assert "iou" in defaults
    assert "max_det" in defaults


def test_models(client: TestClient):
    r = client.get("/models")
    assert r.status_code == 200
    data = r.json()
    assert "default" in data
    assert isinstance(data.get("categories"), dict)
    cats = data["categories"]
    assert "yolo_detect" in cats
    assert len(cats["yolo_detect"]["models"]) > 0


def test_model_info_found(client: TestClient):
    r = client.get("/models/yolov8s.pt")
    assert r.status_code == 200
    data = r.json()
    assert data.get("id") == "yolov8s.pt"
    assert "category" in data
    assert "name" in data


def test_model_info_not_found(client: TestClient):
    r = client.get("/models/nonexistent-model-xyz")
    assert r.status_code == 404


def test_labels_dict_names(client: TestClient, monkeypatch):
    from app.model_manager import model_manager

    monkeypatch.setattr(
        model_manager,
        "load_model",
        lambda model_id: SimpleNamespace(model=SimpleNamespace(names={1: "person", 0: "cat"})),
    )

    r = client.get("/labels?model=yolov8n.pt")
    assert r.status_code == 200
    assert r.json() == {"model": "yolov8n.pt", "labels": ["cat", "person"]}


def test_labels_sequence_names(client: TestClient, monkeypatch):
    from app.model_manager import model_manager

    monkeypatch.setattr(
        model_manager,
        "load_model",
        lambda model_id: SimpleNamespace(model=SimpleNamespace(names=("cat", "person"))),
    )

    r = client.get("/labels?model=yolov8s.pt")
    assert r.status_code == 200
    assert r.json() == {"model": "yolov8s.pt", "labels": ["cat", "person"]}


def test_labels_error_returns_400(client: TestClient, monkeypatch):
    from app.model_manager import model_manager

    def raise_error(model_id):
        raise ValueError("bad model")

    monkeypatch.setattr(model_manager, "load_model", raise_error)

    r = client.get("/labels?model=broken")
    assert r.status_code == 400
    assert r.json()["detail"] == "bad model"


# ------------------------------------------------------------------
# 推理端点
# ------------------------------------------------------------------


def test_infer_endpoint(client: TestClient, image_bytes: bytes, mock_infer):
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?model=yolov8n.pt", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data.get("model") == "yolov8n.pt"
    assert data.get("task") == "detect"
    assert isinstance(data.get("detections"), list)
    assert data.get("inference_time") > 0


def test_infer_unknown_model_returns_400(client: TestClient, image_bytes: bytes, mock_infer):
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?model=unknown", files=files)
    assert r.status_code == 400
    data = r.json()
    assert "Unknown model category" in data.get("detail", "")


def test_infer_invalid_content_type(client: TestClient):
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    r = client.post("/infer", files=files)
    assert r.status_code == 400


def test_infer_empty_file(client: TestClient):
    files = {"file": ("test.png", b"", "image/png")}
    r = client.post("/infer", files=files)
    assert r.status_code == 400


def test_caption_endpoint(client: TestClient, image_bytes: bytes, mock_infer):
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/caption", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data.get("task") == "caption"
    assert isinstance(data.get("caption"), str)
    assert data.get("model") == "Salesforce/blip-image-captioning-base"


def test_vqa_endpoint(client: TestClient, image_bytes: bytes, mock_infer):
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/vqa?question=What%20is%20in%20this%20image%3F", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data.get("task") == "vqa"
    assert isinstance(data.get("answer"), str)
    assert data.get("model") == "Salesforce/blip-vqa-base"


def test_vqa_missing_question(client: TestClient, image_bytes: bytes):
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/vqa", files=files)
    assert r.status_code == 422


# ------------------------------------------------------------------
# WebSocket 端点
# ------------------------------------------------------------------


def test_websocket_connect(client: TestClient, mock_infer):
    with client.websocket_connect("/ws?model=yolov8n.pt") as ws:
        data = ws.receive_json()
        assert data.get("type") == "ready"
        assert data.get("model") == "yolov8n.pt"


def test_websocket_binary_inference(client: TestClient, image_bytes: bytes, mock_infer):
    with client.websocket_connect("/ws?model=yolov8n.pt") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "ready"

        ws.send_bytes(image_bytes)
        result = ws.receive_json()
        assert result.get("type") == "result"
        assert "data" in result
        assert result["data"].get("task") == "detect"


def test_websocket_config_update(client: TestClient, mock_infer):
    with client.websocket_connect("/ws?model=yolov8n.pt") as ws:
        ws.receive_json()  # ready

        ws.send_json({"type": "config", "model": "yolov8s.pt", "conf": 0.5})
        resp = ws.receive_json()
        assert resp.get("type") == "config_updated"
        assert resp.get("model") == "yolov8s.pt"


def test_websocket_config_can_clear_queries_and_question(
    client: TestClient, image_bytes: bytes, monkeypatch
):
    from app.model_manager import model_manager

    calls = []

    def fake_infer(*, model_id: str, image, text_queries=None, question=None, **kwargs):
        calls.append(
            {
                "model_id": model_id,
                "text_queries": text_queries,
                "question": question,
            }
        )
        h, w = image.shape[:2]
        return {
            "width": w,
            "height": h,
            "detections": [],
            "inference_time": 1.0,
            "task": "detect",
            "text_queries": text_queries,
            "question": question,
        }

    monkeypatch.setattr(model_manager, "infer", fake_infer)

    with client.websocket_connect("/ws?model=yolov8n.pt&text_queries=cat,dog&question=what") as ws:
        ws.receive_json()  # ready

        ws.send_bytes(image_bytes)
        result = ws.receive_json()
        assert result["type"] == "result"
        assert calls[-1]["text_queries"] == ["cat", "dog"]
        assert calls[-1]["question"] == "what"

        ws.send_json({"type": "config", "text_queries": [], "question": None})
        resp = ws.receive_json()
        assert resp["type"] == "config_updated"

        ws.send_bytes(image_bytes)
        result = ws.receive_json()
        assert result["type"] == "result"
        assert calls[-1]["text_queries"] is None
        assert calls[-1]["question"] is None


def test_websocket_query_params_preserve_zero_and_false_values(
    client: TestClient, image_bytes: bytes, monkeypatch
):
    from app.model_manager import model_manager

    calls = []

    def fake_infer(*, model_id: str, image, conf=None, iou=None, max_det=None, half=None, **kwargs):
        calls.append(
            {
                "model_id": model_id,
                "conf": conf,
                "iou": iou,
                "max_det": max_det,
                "half": half,
            }
        )
        h, w = image.shape[:2]
        return {
            "width": w,
            "height": h,
            "detections": [],
            "inference_time": 1.0,
            "task": "detect",
        }

    monkeypatch.setattr(model_manager, "infer", fake_infer)

    with client.websocket_connect("/ws?model=yolov8n.pt&conf=0&iou=0&max_det=0&half=0") as ws:
        ws.receive_json()  # ready
        ws.send_bytes(image_bytes)
        result = ws.receive_json()
        assert result["type"] == "result"
        assert calls[-1]["conf"] == 0.0
        assert calls[-1]["iou"] == 0.0
        assert calls[-1]["max_det"] == 0
        assert calls[-1]["half"] is False


# ------------------------------------------------------------------
# 注册表 / 处理器单元测试
# ------------------------------------------------------------------


def test_handler_registry_resolve():
    from app.handlers.registry import HandlerRegistry

    reg = HandlerRegistry("cpu")
    handler = reg.get_handler("yolov8s.pt")
    from app.handlers.yolo_handler import YOLOHandler

    assert isinstance(handler, YOLOHandler)


def test_handler_registry_unknown():
    from app.handlers.registry import HandlerRegistry

    reg = HandlerRegistry("cpu")
    with pytest.raises(ValueError, match="Unknown model"):
        reg.get_handler("totally-invalid-model")


def test_get_available_models():
    from app.handlers.registry import get_available_models

    cats = get_available_models()
    assert "yolo_detect" in cats
    assert any(m["id"] == "yolov8s.pt" for m in cats["yolo_detect"]["models"])


def test_config_settings():
    from app.config import AppSettings

    s = AppSettings(
        PORT=9000,
        MODEL_NAME="yolov8n.pt",
        ALLOW_ORIGINS="http://a.com,http://b.com",
        MAX_UPLOAD_MB=5,
    )
    assert s.port == 9000
    assert s.origins_list == ["http://a.com", "http://b.com"]
    assert s.max_upload_bytes == 5 * 1024 * 1024


@pytest.mark.parametrize("raw", ["1", "true", "yes", "on", True])
def test_config_skip_warmup_true_values(raw):
    from app.config import AppSettings

    assert AppSettings(SKIP_WARMUP=raw).skip_warmup is True


@pytest.mark.parametrize("raw", ["0", "false", "no", "off", "", False])
def test_config_skip_warmup_false_values(raw):
    from app.config import AppSettings

    assert AppSettings(SKIP_WARMUP=raw).skip_warmup is False


def test_config_skip_warmup_invalid_value():
    from app.config import AppSettings

    with pytest.raises(ValueError, match="SKIP_WARMUP must be a boolean value"):
        AppSettings(SKIP_WARMUP="not-a-bool")


def test_parse_bool_string_invalid_value():
    from app.config import parse_bool_string

    assert parse_bool_string("not-a-bool") is None


def test_parse_bool_string_empty_value():
    from app.config import parse_bool_string

    assert parse_bool_string("") is False


# ------------------------------------------------------------------
# 参数范围验证测试
# ------------------------------------------------------------------


def test_infer_conf_out_of_range_high(client: TestClient, image_bytes: bytes):
    """测试 conf 参数超出上限"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?conf=1.5", files=files)
    assert r.status_code == 422  # Validation error


def test_infer_conf_out_of_range_low(client: TestClient, image_bytes: bytes):
    """测试 conf 参数低于下限"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?conf=-0.1", files=files)
    assert r.status_code == 422


def test_infer_iou_out_of_range(client: TestClient, image_bytes: bytes):
    """测试 iou 参数超出范围"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?iou=2.0", files=files)
    assert r.status_code == 422


def test_infer_max_det_out_of_range(client: TestClient, image_bytes: bytes):
    """测试 max_det 参数超出范围"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?max_det=2000", files=files)  # max is 1000
    assert r.status_code == 422


def test_infer_max_det_zero(client: TestClient, image_bytes: bytes):
    """测试 max_det 参数为零"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?max_det=0", files=files)  # must be > 0
    assert r.status_code == 422


def test_infer_imgsz_out_of_range(client: TestClient, image_bytes: bytes):
    """测试 imgsz 参数超出范围"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?imgsz=8192", files=files)  # max is 4096
    assert r.status_code == 422


def test_infer_imgsz_too_small(client: TestClient, image_bytes: bytes):
    """测试 imgsz 参数过小"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?imgsz=16", files=files)  # min is 32
    assert r.status_code == 422


def test_infer_valid_boundary_values(client: TestClient, image_bytes: bytes, mock_infer):
    """测试边界值应该被接受"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    # 测试边界值
    r2 = client.post("/infer?conf=0.0", files=files)
    assert r2.status_code == 200


# ------------------------------------------------------------------
# 模型 ID 安全验证测试
# ------------------------------------------------------------------


def test_model_id_path_traversal_attack(client: TestClient, image_bytes: bytes):
    """测试模型 ID 路径遍历攻击"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    # 尝试路径遍历
    r = client.post("/infer?model=../etc/passwd", files=files)
    assert r.status_code == 400


def test_model_id_parent_directory_attack(client: TestClient, image_bytes: bytes):
    """测试模型 ID 包含父目录引用"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?model=..\\windows\\system32", files=files)
    assert r.status_code == 400


def test_model_id_slash_in_name(client: TestClient, image_bytes: bytes):
    """测试模型 ID 包含斜杠"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?model=some/path/model.pt", files=files)
    assert r.status_code == 400


def test_model_info_path_traversal(client: TestClient):
    """测试模型信息端点的路径遍历"""
    r = client.get("/models/../etc/passwd")
    # 应该返回 404 (路由不匹配) 或 400 (验证错误)，不应暴露文件系统
    assert r.status_code in [400, 404]


# ------------------------------------------------------------------
# URL 编码路径遍历测试
# ------------------------------------------------------------------


def test_model_id_url_encoded_path_traversal(client: TestClient, image_bytes: bytes):
    """测试模型 ID URL 编码路径遍历攻击"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    # %2e%2e%2f 是 ../ 的 URL 编码
    r = client.post("/infer?model=%2e%2e%2fetc%2fpasswd", files=files)
    assert r.status_code == 400


def test_model_id_double_url_encoded(client: TestClient, image_bytes: bytes):
    """测试双重 URL 编码攻击"""
    files = {"file": ("test.png", image_bytes, "image/png")}
    # %252e%252e%252f 是 ../ 的双重 URL 编码
    r = client.post("/infer?model=%252e%252e%252fetc%252fpasswd", files=files)
    # 应该被验证或找不到模型
    assert r.status_code in [400, 404]


# ------------------------------------------------------------------
# Handler 工具方法测试
# ------------------------------------------------------------------


def test_base_handler_bgr_to_pil():
    """测试 BGR 到 PIL 转换"""
    from app.handlers.base import BaseHandler

    # 创建 BGR 图像 (蓝色)
    bgr_image = np.zeros((100, 100, 3), dtype=np.uint8)
    bgr_image[:, :, 0] = 255  # B 通道为 255

    pil_image = BaseHandler.bgr_to_pil(bgr_image)

    assert pil_image.size == (100, 100)
    assert pil_image.mode == "RGB"
    # BGR 的蓝色转换为 RGB 的红色
    pixel = pil_image.getpixel((50, 50))
    assert pixel[0] == 0  # R
    assert pixel[1] == 0  # G
    assert pixel[2] == 255  # B


def test_base_handler_make_result():
    """测试结果字典构造"""
    from app.handlers.base import BaseHandler

    image = np.zeros((480, 640, 3), dtype=np.uint8)
    detections = [{"bbox": [0, 0, 10, 10], "score": 0.9, "label": "test"}]

    result = BaseHandler.make_result(
        image, detections=detections, inference_time=15.5, task="detect"
    )

    assert result["width"] == 640
    assert result["height"] == 480
    assert result["inference_time"] == 15.5
    assert result["task"] == "detect"
    assert result["detections"] == detections


def test_base_handler_make_result_with_extra():
    """测试结果字典构造（带额外字段）"""
    from app.handlers.base import BaseHandler

    image = np.zeros((100, 100, 3), dtype=np.uint8)

    result = BaseHandler.make_result(
        image,
        inference_time=10.0,
        task="caption",
        caption="a test image",
        extra_field="extra_value",
    )

    assert result["caption"] == "a test image"
    assert result["extra_field"] == "extra_value"


# ------------------------------------------------------------------
# 工具函数测试
# ------------------------------------------------------------------


def test_parse_text_queries_string():
    """测试文本查询解析（字符串）"""
    from app.routes import _parse_text_queries

    result = _parse_text_queries("cat, dog, bird")
    assert result == ["cat", "dog", "bird"]


def test_parse_text_queries_list():
    """测试文本查询解析（列表）"""
    from app.routes import _parse_text_queries

    result = _parse_text_queries(["cat", "dog"])
    assert result == ["cat", "dog"]


def test_parse_text_queries_empty():
    """测试文本查询解析（空值）"""
    from app.routes import _parse_text_queries

    assert _parse_text_queries(None) is None
    assert _parse_text_queries("") is None
    assert _parse_text_queries("   ") is None


def test_get_optional_float():
    """测试可选浮点数解析"""
    from app.routes import _get_optional_float

    assert _get_optional_float("3.14") == 3.14
    assert _get_optional_float("0") == 0.0
    assert _get_optional_float(None) is None
    assert _get_optional_float("") is None
    assert _get_optional_float("invalid") is None


def test_get_optional_int():
    """测试可选整数解析"""
    from app.routes import _get_optional_int

    assert _get_optional_int("42") == 42
    assert _get_optional_int("0") == 0
    assert _get_optional_int(None) is None
    assert _get_optional_int("") is None
    assert _get_optional_int("invalid") is None


# ------------------------------------------------------------------
# ModelManager 测试
# ------------------------------------------------------------------


def test_model_manager_device_property():
    """测试 ModelManager 设备属性"""
    from app.model_manager import ModelManager

    manager = ModelManager()
    assert manager.device in ["cpu", "cuda:0", "mps"]


def test_model_manager_invalid_model_id_empty():
    """测试空模型 ID"""
    from app.model_manager import ModelManager

    manager = ModelManager()
    with pytest.raises(ValueError, match="non-empty string"):
        manager.load_model("")


def test_model_manager_invalid_model_id_none():
    """测试 None 模型 ID"""
    from app.model_manager import ModelManager

    manager = ModelManager()
    with pytest.raises(ValueError, match="non-empty string"):
        manager.load_model(None)  # type: ignore


# ------------------------------------------------------------------
# 配置测试
# ------------------------------------------------------------------


def test_config_log_level():
    """测试 LOG_LEVEL 配置"""
    from app.config import AppSettings

    s = AppSettings(LOG_LEVEL="DEBUG")
    assert s.log_level == "DEBUG"

    s2 = AppSettings(LOG_LEVEL="warning")
    assert s2.log_level == "WARNING"


def test_config_log_level_invalid():
    """测试无效 LOG_LEVEL"""
    from app.config import AppSettings

    s = AppSettings(LOG_LEVEL="INVALID")
    assert s.log_level == "INFO"  # 回退到默认


def test_config_default_models():
    """测试默认模型配置"""
    from app.config import AppSettings

    s = AppSettings()
    assert s.default_caption_model == "Salesforce/blip-image-captioning-base"
    assert s.default_vqa_model == "Salesforce/blip-vqa-base"
    assert s.blip_max_tokens == 50
    assert s.grounding_text_threshold == 0.25
