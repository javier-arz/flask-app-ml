"""Unit tests for image decoding and preprocessing."""

import cv2
import numpy as np
import pytest

from app.ml import preprocessing


def _encode_png(array_rgb: np.ndarray) -> bytes:
    bgr = cv2.cvtColor(array_rgb, cv2.COLOR_RGB2BGR)
    ok, buffer = cv2.imencode(".png", bgr)
    assert ok
    return buffer.tobytes()


def test_decode_returns_none_for_empty_bytes():
    assert preprocessing.decode_image(b"") is None


def test_decode_returns_none_for_garbage():
    assert preprocessing.decode_image(b"this is not an image") is None


def test_decode_preserves_rgb_order():
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    image[:, :] = (255, 0, 0)  # red in RGB
    decoded = preprocessing.decode_image(_encode_png(image))
    assert decoded is not None
    assert tuple(int(v) for v in decoded[5, 5]) == (255, 0, 0)


def test_preprocess_shape_dtype_and_range():
    image = np.full((48, 48, 3), 128, dtype=np.uint8)
    array = preprocessing.preprocess_image(image)
    assert array.shape == (1, 32, 32, 3)
    assert array.dtype == np.float32
    assert float(array.min()) >= 0.0
    assert float(array.max()) <= 1.0
    assert float(array.max()) == pytest.approx(128 / 255, rel=1e-3)


def test_decode_then_preprocess_roundtrip():
    image = np.full((40, 40, 3), 200, dtype=np.uint8)
    decoded = preprocessing.decode_image(_encode_png(image))
    assert decoded is not None
    array = preprocessing.preprocess_image(decoded)
    assert array.shape == (1, 32, 32, 3)
