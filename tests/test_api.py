"""Tests for FastAPI application endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    """Health endpoint should return application status."""
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload
    assert payload["status"] == "ok"


def test_feature_metadata_endpoint() -> None:
    """Feature metadata endpoint should expose feature list."""
    response = client.get("/feature-metadata")

    assert response.status_code == 200
    payload = response.json()
    assert "features" in payload
    assert len(payload["features"]) == 13
    assert payload["target"] == "medv"


def test_predict_endpoint_success(monkeypatch) -> None:
    """Prediction endpoint should return rounded prediction value."""

    class DummyModel:
        """Simple stub model for API tests."""

        def predict(self, x_data):
            return [25.67891]

    from app import main

    monkeypatch.setattr(main, "load_model", lambda: DummyModel())

    payload = {
        "crim": 0.02729,
        "zn": 0.0,
        "indus": 7.07,
        "chas": 0,
        "nox": 0.469,
        "rm": 7.185,
        "age": 61.1,
        "dis": 4.9671,
        "rad": 2,
        "tax": 242,
        "ptratio": 17.8,
        "black": 392.83,
        "lstat": 4.03,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json() == {"predicted_medv": 25.6789}


def test_predict_endpoint_validation_error() -> None:
    """Prediction endpoint should return 422 for invalid payload."""
    payload = {
        "crim": 0.02729,
        "zn": 0.0,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422