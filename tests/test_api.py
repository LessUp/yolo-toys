import io
import os

import pytest
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("SKIP_WARMUP", "1")
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def image_bytes() -> bytes:
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
