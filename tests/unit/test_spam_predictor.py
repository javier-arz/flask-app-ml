"""Unit tests for the spam predictor module."""

from __future__ import annotations

import pytest

from app.ml import spam_predictor


class TestSpamPredictorError:
    """Tests for the SpamPredictorError exception."""

    def test_error_is_exception(self):
        """SpamPredictorError should be an Exception subclass."""
        assert issubclass(spam_predictor.SpamPredictorError, Exception)

    def test_error_message(self):
        """SpamPredictorError should store the message."""
        error = spam_predictor.SpamPredictorError("test error")
        assert str(error) == "test error"


class TestLoadModel:
    """Tests for the load_model function."""

    def test_load_model_returns_model(self, monkeypatch):
        """load_model should return a model object."""
        mock_model = object()

        def mock_load(path):
            return mock_model

        monkeypatch.setattr("keras.saving.load_model", mock_load)
        monkeypatch.setattr(spam_predictor, "_model_path", lambda: "fake/path.keras")

        # Reset the cached model
        monkeypatch.setattr(spam_predictor, "_model", None)

        result = spam_predictor.load_model()
        assert result is mock_model

    def test_load_model_uses_cache(self, monkeypatch):
        """load_model should return cached model on subsequent calls."""
        mock_model = object()
        call_count = 0

        def mock_load(path):
            nonlocal call_count
            call_count += 1
            return mock_model

        monkeypatch.setattr("keras.saving.load_model", mock_load)
        monkeypatch.setattr(spam_predictor, "_model_path", lambda: "fake/path.keras")

        # Reset the cached model
        monkeypatch.setattr(spam_predictor, "_model", None)

        result1 = spam_predictor.load_model()
        result2 = spam_predictor.load_model()
        assert result1 is mock_model
        assert result2 is mock_model
        assert call_count == 1  # Only loaded once

    def test_load_model_raises_on_failure(self, monkeypatch):
        """load_model should raise SpamPredictorError on failure."""
        def mock_load(path):
            raise RuntimeError("Model file not found")

        monkeypatch.setattr("keras.saving.load_model", mock_load)
        monkeypatch.setattr(spam_predictor, "_model_path", lambda: "fake/path.keras")

        # Reset the cached model
        monkeypatch.setattr(spam_predictor, "_model", None)

        with pytest.raises(spam_predictor.SpamPredictorError, match="Could not load"):
            spam_predictor.load_model()


class TestPredict:
    """Tests for the predict function."""

    def test_predict_returns_tuple(self, monkeypatch):
        """predict should return (class_index, confidence_percent)."""
        mock_model = type("MockModel", (), {
            "predict": lambda self, x, verbose: [[0.1]]  # Low spam probability
        })()

        monkeypatch.setattr(spam_predictor, "load_model", lambda: mock_model)

        index, confidence = spam_predictor.predict("Hello, how are you?")
        assert isinstance(index, int)
        assert isinstance(confidence, float)
        assert index == 0  # ham
        assert confidence == 90.0  # 1.0 - 0.1 = 0.9 -> 90.0%

    def test_predict_spam_text(self, monkeypatch):
        """predict should classify spam text correctly."""
        mock_model = type("MockModel", (), {
            "predict": lambda self, x, verbose: [[0.95]]  # High spam probability
        })()

        monkeypatch.setattr(spam_predictor, "load_model", lambda: mock_model)

        index, confidence = spam_predictor.predict("¡Gana dinero gratis!")
        assert index == 1  # spam
        assert confidence == 95.0

    def test_predict_raises_on_model_error(self, monkeypatch):
        """predict should raise SpamPredictorError on model failure."""
        def mock_load():
            raise spam_predictor.SpamPredictorError("Could not load model")

        monkeypatch.setattr(spam_predictor, "load_model", mock_load)

        with pytest.raises(spam_predictor.SpamPredictorError):
            spam_predictor.predict("test")
