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
    from app.main import model_manager

    def fake_infer(*, model_id: str, image, text_queries=None, question=None, **kwargs):
        h, w = image.shape[:2]
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


def test_health_ok(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert "version" in data
    assert "device" in data
    assert "default_model" in data


def test_models(client: TestClient):
    r = client.get("/models")
    assert r.status_code == 200
    data = r.json()
    assert "default" in data
    assert isinstance(data.get("categories"), dict)


def test_infer_endpoint(client: TestClient, image_bytes: bytes, mock_infer):
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?model=yolov8n.pt", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data.get("model") == "yolov8n.pt"
    assert data.get("task") == "detect"
    assert isinstance(data.get("detections"), list)


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
