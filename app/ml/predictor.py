"""Lazy, thread-safe model loader and raw predictor.

The model is loaded on first use (constitution section 3.2) and reused across
requests (spec FR-011). ``keras`` is imported lazily so that importing this
module does not require the heavy ML dependencies and so unit tests can stub
``predict`` without loading the real artifact.

The backend is selected via the ``KERAS_BACKEND`` environment variable
(default ``torch`` for this project).
"""

from __future__ import annotations

import os
import threading

# Must be set before Keras is imported (which happens lazily below).
os.environ.setdefault("KERAS_BACKEND", "torch")

_lock = threading.Lock()
_model = None


class PredictorError(Exception):
    """Raised when the model cannot be loaded or inference fails."""


def _model_path() -> str:
    # Imported lazily to avoid a hard dependency at module import time.
    from app.ml.model_registry import get_model

    return get_model().artifact_path


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
                    raise PredictorError(f"Could not load the model: {exc}") from exc
    return _model


def predict(image_array) -> tuple[int, float]:
    """Run inference and return ``(class_index, confidence_percent)``.

    ``confidence_percent`` is the top-1 probability expressed as a percentage
    rounded to one decimal place.
    """
    try:
        model = load_model()

        import numpy as np

        probabilities = model.predict(image_array, verbose=0)[0]
        index = int(np.argmax(probabilities))
        confidence = round(float(probabilities[index]) * 100.0, 1)
        return index, confidence
    except PredictorError:
        raise
    except Exception as exc:  # noqa: BLE001 - wrapped for the caller
        raise PredictorError(f"Inference failed: {exc}") from exc
