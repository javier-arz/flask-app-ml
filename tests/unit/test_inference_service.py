"""Unit tests for the shared inference orchestration (predictor stubbed)."""

import io

import pytest
from werkzeug.datastructures import FileStorage

from app.ml import inference_service
from app.ml.inference_service import InferenceError, analyze_file

from tests.helpers import make_image_bytes


def _upload(data: bytes, filename: str = "sample.png") -> FileStorage:
    return FileStorage(stream=io.BytesIO(data), filename=filename)


def _stub(index: int, confidence: float):
    return lambda array: (index, confidence)


def test_missing_file_raises_400():
    with pytest.raises(InferenceError) as exc:
        analyze_file(None)
    assert exc.value.status_code == 400
    assert exc.value.message == inference_service.NO_IMAGE_MESSAGE


def test_empty_filename_raises_400():
    with pytest.raises(InferenceError) as exc:
        analyze_file(_upload(make_image_bytes(), filename=""))
    assert exc.value.status_code == 400
    assert exc.value.message == inference_service.NO_IMAGE_MESSAGE


def test_undecodable_raises_400():
    with pytest.raises(InferenceError) as exc:
        analyze_file(_upload(b"not an image"))
    assert exc.value.status_code == 400
    assert exc.value.message == inference_service.INVALID_IMAGE_MESSAGE


def test_inference_failure_raises_500(monkeypatch):
    def _boom(array):  # noqa: ARG001
        raise RuntimeError("model exploded")

    monkeypatch.setattr(inference_service.predictor, "predict", _boom)
    with pytest.raises(InferenceError) as exc:
        analyze_file(_upload(make_image_bytes()))
    assert exc.value.status_code == 500
    assert exc.value.message == inference_service.INFERENCE_FAILURE_MESSAGE


def test_confident_result(monkeypatch):
    monkeypatch.setattr(inference_service.predictor, "predict", _stub(3, 87.0))
    result = analyze_file(_upload(make_image_bytes()))
    assert result.prediction == "gato"
    assert result.confidence == 87.0
    assert result.uncertain is False
    assert result.model == "cifar10"
    assert "No estoy completamente seguro" not in result.message
    assert "87.0% de certeza" in result.message


@pytest.mark.parametrize(
    "confidence,uncertain",
    [(49.9, True), (50.0, False), (50.1, False)],
)
def test_threshold_boundary(monkeypatch, confidence, uncertain):
    monkeypatch.setattr(inference_service.predictor, "predict", _stub(0, confidence))
    result = analyze_file(_upload(make_image_bytes()))
    assert result.uncertain is uncertain
    assert ("No estoy completamente seguro" in result.message) is uncertain


def test_result_is_json_serializable(monkeypatch):
    monkeypatch.setattr(inference_service.predictor, "predict", _stub(0, 10.0))
    payload = analyze_file(_upload(make_image_bytes())).to_dict()
    assert set(payload) == {"message", "prediction", "confidence", "uncertain", "model"}


def test_list_models_exposes_cifar10():
    models = inference_service.list_models()
    assert any(model["name"] == "cifar10" for model in models)
    assert all("artifact_path" not in model for model in models)
