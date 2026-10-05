"""Image decoding and preprocessing (OpenCV).

The preprocessing pipeline must match the model's training-time
transformations (constitution section 3.3). See ``research.md`` R3/R4:

    decode (BGR) -> convert to RGB -> resize 32x32 (INTER_AREA)
    -> float32 -> scale to [0, 1] -> add batch dimension
"""

from __future__ import annotations

import cv2
import numpy as np

#: Target input size expected by the registered model.
DEFAULT_SIZE: tuple[int, int] = (32, 32)

#: Scaling factor applied to pixel values (1/255 -> [0, 1]).
SCALE: float = 1.0 / 255.0


def decode_image(raw: bytes) -> np.ndarray | None:
    """Decode image bytes into an RGB array.

    Returns ``None`` when the bytes are empty or cannot be decoded as an
    image. Validation is performed by decoding the content rather than
    trusting the filename or declared MIME type.
    """
    if not raw:
        return None

    buffer = np.frombuffer(raw, dtype=np.uint8)
    image_bgr = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image_bgr is None:
        return None

    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def preprocess_image(
    image_rgb: np.ndarray,
    size: tuple[int, int] = DEFAULT_SIZE,
) -> np.ndarray:
    """Resize, normalize and batch an RGB image for inference.

    Returns an array of shape ``(1, size[0], size[1], 3)`` and dtype
    ``float32`` with values in ``[0, 1]``.
    """
    resized = cv2.resize(image_rgb, size, interpolation=cv2.INTER_AREA)
    normalized = resized.astype(np.float32) * SCALE
    return np.expand_dims(normalized, axis=0)
