"""Integration tests asserting errors are safe and do not leak internals (FR-013, SC-008)."""

import io

from app.ml import inference_service

from tests.helpers import image_upload

_FORBIDDEN_TOKENS = (
    "Traceback",
    'File "',
    "site-packages",
    "app\\ml",
    "app/ml",
    ".py",
    "Keras",
    "keras",
    "torch",
    "cv2",
)


def _assert_clean(message: str) -> None:
    assert message, "error message must not be empty"
    for token in _FORBIDDEN_TOKENS:
        assert token not in message, f"leaked internal token {token!r} in {message!r}"


def test_missing_file_error_is_clean(client):
    response = client.post("/images/predict")
    _assert_clean(response.get_json()["error"])


def test_undecodable_error_is_clean(client):
    response = client.post(
        "/images/predict",
        data={"image": (io.BytesIO(b"garbage"), "x.png")},
        content_type="multipart/form-data",
    )
    _assert_clean(response.get_json()["error"])


def test_inference_failure_error_is_clean(client, monkeypatch):
    def _boom(array):  # noqa: ARG001
        raise RuntimeError("internal detail: C:\\secret\\path\\model.keras")

    monkeypatch.setattr(inference_service.predictor, "predict", _boom)
    response = client.post(
        "/images/predict", data=image_upload(), content_type="multipart/form-data"
    )
    assert response.status_code == 500
    _assert_clean(response.get_json()["error"])


def test_oversized_payload_returns_413(client, app):
    app.config["MAX_CONTENT_LENGTH"] = 10  # force the limit for this test
    response = client.post(
        "/images/predict", data=image_upload(), content_type="multipart/form-data"
    )
    assert response.status_code == 413
    _assert_clean(response.get_json()["error"])
