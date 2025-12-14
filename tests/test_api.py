import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("SKIP_WARMUP", "1")
    from app.main import app

    with TestClient(app) as c:
        yield c


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
