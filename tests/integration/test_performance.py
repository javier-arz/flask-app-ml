"""Latency check for SC-001.

This measures end-to-end request overhead with the model stubbed (deterministic
and fast). Real inference timing depends on the host and model artifact; run the
quickstart scenarios for a full end-to-end measurement.
"""

import time

from app.ml import inference_service

from tests.helpers import image_upload

_LATENCY_BUDGET_SECONDS = 2.0
_SAMPLES = 10


def test_request_latency_within_budget(client, monkeypatch):
    monkeypatch.setattr(inference_service.predictor, "predict", lambda a: (0, 90.0))
    durations = []
    for _ in range(_SAMPLES):
        start = time.perf_counter()
        response = client.post(
            "/images/predict", data=image_upload(), content_type="multipart/form-data"
        )
        durations.append(time.perf_counter() - start)
        assert response.status_code == 200

    p95 = sorted(durations)[max(0, int(len(durations) * 0.95) - 1)]
    assert p95 < _LATENCY_BUDGET_SECONDS, f"p95 latency {p95:.3f}s exceeded budget"
