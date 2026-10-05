"""Unit tests for the raw predictor (model stubbed)."""

import numpy as np

from app.ml import predictor


class _StubModel:
    """Minimal stand-in for a Keras model exposing ``predict``."""

    def __init__(self, probabilities):
        self._probabilities = probabilities

    def predict(self, array, verbose=0):  # noqa: ARG002 - matches Keras API
        return np.array([self._probabilities])


def _probs(top_index: int, top_value: float) -> list[float]:
    values = [(1.0 - top_value) / 9] * 10
    values[top_index] = top_value
    return values


def test_predict_returns_argmax_and_confidence(monkeypatch):
    monkeypatch.setattr(predictor, "load_model", lambda: _StubModel(_probs(3, 0.87)))
    index, confidence = predictor.predict(np.zeros((1, 32, 32, 3), dtype=np.float32))
    assert index == 3
    assert confidence == 87.0


def test_predict_rounds_confidence_to_one_decimal(monkeypatch):
    monkeypatch.setattr(predictor, "load_model", lambda: _StubModel(_probs(0, 0.32456)))
    index, confidence = predictor.predict(np.zeros((1, 32, 32, 3), dtype=np.float32))
    assert index == 0
    assert confidence == 32.5


def test_predict_wraps_errors(monkeypatch):
    def _boom(*_args, **_kwargs):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(predictor, "load_model", _boom)
    try:
        predictor.predict(np.zeros((1, 32, 32, 3), dtype=np.float32))
    except predictor.PredictorError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected PredictorError")
