"""Integration tests for the prediction endpoint: POST /images/predict."""

import io

from app.ml import inference_service

from tests.helpers import image_upload


def test_valid_image_returns_prediction(client, monkeypatch):
    monkeypatch.setattr(inference_service.predictor, "predict", lambda a: (3, 87.0))
    response = client.post(
        "/images/predict", data=image_upload(), content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    for key in ("message", "prediction", "confidence", "uncertain", "model"):
        assert key in data
    assert data["prediction"] == "gato"
    assert data["confidence"] == 87.0
    assert data["uncertain"] is False
    assert data["model"] == "cifar10"


def test_no_file_returns_400(client):
    response = client.post("/images/predict")
    assert response.status_code == 400
    assert response.get_json()["error"] == inference_service.NO_IMAGE_MESSAGE


def test_undecodable_returns_400(client):
    response = client.post(
        "/images/predict",
        data={"image": (io.BytesIO(b"not an image"), "x.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == inference_service.INVALID_IMAGE_MESSAGE


def test_uncertain_result_includes_statement(client, monkeypatch):
    monkeypatch.setattr(inference_service.predictor, "predict", lambda a: (0, 32.4))
    response = client.post(
        "/images/predict", data=image_upload(), content_type="multipart/form-data"
    )
    data = response.get_json()
    assert data["uncertain"] is True
    assert "No estoy completamente seguro de esta predicción." in data["message"]


def test_boundary_fifty_percent_is_confident(client, monkeypatch):
    monkeypatch.setattr(inference_service.predictor, "predict", lambda a: (0, 50.0))
    response = client.post(
        "/images/predict", data=image_upload(), content_type="multipart/form-data"
    )
    data = response.get_json()
    assert data["uncertain"] is False
    assert "No estoy completamente seguro" not in data["message"]


def test_determinism_same_image_twice(client, monkeypatch):
    monkeypatch.setattr(inference_service.predictor, "predict", lambda a: (2, 64.5))
    first = client.post(
        "/images/predict", data=image_upload(), content_type="multipart/form-data"
    ).get_json()
    second = client.post(
        "/images/predict", data=image_upload(), content_type="multipart/form-data"
    ).get_json()
    assert first["prediction"] == second["prediction"]
    assert first["confidence"] == second["confidence"]
