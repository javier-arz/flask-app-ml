"""Shared test helpers for building valid image uploads."""

from __future__ import annotations

import io

import cv2
import numpy as np


def make_image_bytes(size: tuple[int, int] = (32, 32), color=(120, 130, 140)) -> bytes:
    """Return PNG bytes for a solid-color image (BGR color order)."""
    image = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    image[:, :] = color
    ok, buffer = cv2.imencode(".png", image)
    assert ok, "failed to encode test image"
    return buffer.tobytes()


def image_upload(size: tuple[int, int] = (32, 32), filename: str = "sample.png") -> dict:
    """Return a Flask test-client ``data`` dict with a valid image file."""
    return {"image": (io.BytesIO(make_image_bytes(size)), filename)}
