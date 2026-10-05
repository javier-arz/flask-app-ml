"""Inference orchestration.

The single prediction endpoint ``POST /images/predict`` delegates here so the
HTTP layer stays free of ML logic.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass

from app.ml import predictor, preprocessing
from app.ml.model_registry import get_model, load_registry

logger = logging.getLogger(__name__)

NO_IMAGE_MESSAGE = "No se recibió ninguna imagen."
INVALID_IMAGE_MESSAGE = (
    "El archivo no es una imagen válida o el formato no está soportado."
)
INFERENCE_FAILURE_MESSAGE = "No fue posible analizar la imagen en este momento."
UNCERTAIN_SUFFIX = " No estoy completamente seguro de esta predicción."


class InferenceError(Exception):
    """A user-facing error with an associated HTTP status code."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class PredictionResult:
    """Outcome of a single successful analysis."""

    message: str
    prediction: str
    confidence: float
    uncertain: bool
    model: str

    def to_dict(self) -> dict:
        """Serialize to the JSON response shape shared by both endpoints."""
        return asdict(self)


def analyze_file(file_storage) -> PredictionResult:
    """Validate, preprocess and classify an uploaded image.

    Args:
        file_storage: A Werkzeug ``FileStorage`` (or ``None``).

    Returns:
        A :class:`PredictionResult` on success.

    Raises:
        InferenceError: with an HTTP status code (400 or 500) for every
            failure mode, so controllers only have to translate it to JSON.
    """
    if file_storage is None or not getattr(file_storage, "filename", ""):
        raise InferenceError(NO_IMAGE_MESSAGE, 400)

    raw = file_storage.read()
    if not raw:
        raise InferenceError(NO_IMAGE_MESSAGE, 400)

    image_rgb = preprocessing.decode_image(raw)
    if image_rgb is None:
        raise InferenceError(INVALID_IMAGE_MESSAGE, 400)

    image_array = preprocessing.preprocess_image(image_rgb)

    model_metadata = get_model()
    try:
        class_index, confidence = predictor.predict(image_array)
    except Exception:  # noqa: BLE001 - log details, return a generic error
        logger.exception("Image inference failed")
        raise InferenceError(INFERENCE_FAILURE_MESSAGE, 500) from None

    if not 0 <= class_index < len(model_metadata.classes):
        logger.error("Model returned out-of-range class index %s", class_index)
        raise InferenceError(INFERENCE_FAILURE_MESSAGE, 500)

    label = model_metadata.classes[class_index]["label"]
    uncertain = confidence < float(model_metadata.confidence_threshold)

    message = f"Detecté: {label} ({confidence:.1f}% de certeza)."
    if uncertain:
        message += UNCERTAIN_SUFFIX

    return PredictionResult(
        message=message,
        prediction=label,
        confidence=confidence,
        uncertain=uncertain,
        model=model_metadata.name,
    )


def list_models() -> list[dict]:
    """Return the public metadata view of every registered model."""
    return [model.public_view() for model in load_registry()]
