"""Lazy, thread-safe spam model loader and raw predictor.

The model is loaded on first use (constitution section 3.2) and reused across
requests. ``keras`` is imported lazily so that importing this module does not
require the heavy ML dependencies and so unit tests can stub ``predict``
without loading the real artifact.

The backend is selected via the ``KERAS_BACKEND`` environment variable.
The spam model requires ``tensorflow`` due to the ``TextVectorization`` layer.
"""

from __future__ import annotations

import os
import threading

# Must be set before Keras is imported (which happens lazily below).
os.environ["KERAS_BACKEND"] = "tensorflow"

_lock = threading.Lock()
_model = None


class SpamPredictorError(Exception):
    """Raised when the model cannot be loaded or inference fails."""


def _model_path() -> str:
    # Imported lazily to avoid a hard dependency at module import time.
    from app.ml.model_registry import get_model

    return get_model("spam_classifier").artifact_path


def load_model():
    """Return the cached model, loading it on first call (thread-safe)."""
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                try:
                    import keras

                    _model = keras.saving.load_model(_model_path())
                except Exception as exc:  # noqa: BLE001 - wrapped for the caller
                    raise SpamPredictorError(f"Could not load the model: {exc}") from exc
    return _model


def predict(text: str) -> tuple[int, float]:
    """Run inference and return ``(class_index, confidence_percent)``.

    ``class_index`` is 0 for "ham" (no spam) and 1 for "spam".
    ``confidence_percent`` is the probability expressed as a percentage
    rounded to one decimal place.
    """
    try:
        model = load_model()

        import numpy as np

        # The model has a TextVectorization layer, so we feed raw text
# as a batch of one string. Use dtype=object to avoid TensorFlow dtype issues.
        probabilities = model.predict(np.array([text], dtype=object), verbose=0)[0]
        # Output is a single sigmoid value: probability of spam
        spam_probability = float(probabilities[0])
        # class_index: 0 = ham, 1 = spam
        index = 1 if spam_probability >= 0.5 else 0
        # Confidence is the probability of the predicted class
        confidence = round(
            (spam_probability if index == 1 else 1.0 - spam_probability) * 100.0, 1
        )
        return index, confidence
    except SpamPredictorError:
        raise
    except Exception as exc:  # noqa: BLE001 - wrapped for the caller
        raise SpamPredictorError(f"Inference failed: {exc}") from exc
