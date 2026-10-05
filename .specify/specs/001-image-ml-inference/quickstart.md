# Quickstart: Image ML Inference & Confidence Messaging

**Feature**: `001-image-ml-inference` | **Date**: 2026-10-05

Validation guide to prove the feature works end-to-end. This is a run/validation guide, not an implementation reference.

---

## Prerequisites

- Python 3.14 (existing `venv`).
- The model artifact `best_cifar10.keras` available (source: `F:\estudio\Especialización IA\Machine Learning Avanzado\best_cifar10.keras`).
- Environment variables configured as usual (`.env` with `SECRET_KEY`, `FLASK_CONFIG`, `APP_NAME`, database URI, `KERAS_BACKEND=torch`).

---

## Setup

1. Activate the virtual environment (Windows PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. Install the dependencies (see `plan.md` Technical Context):
   ```powershell
   pip install -r requirements.txt
   ```

3. Select the Keras backend (set in `.env` or the shell):
   ```powershell
   $env:KERAS_BACKEND = "torch"
   ```

4. Place the model artifact and registry:
   ```text
   app/models/weights/cifar10.keras   # copied from the source path above
   app/models/registry.json           # metadata manifest (see data-model.md §1)
   ```

---

## Run

```powershell
flask run
```

Open `http://127.0.0.1:5000/images`.

---

## Validation scenarios

Prediction is served by a single endpoint, `POST /images/predict`; `GET /api/models` lists the available model.

| # | Scenario | Steps | Expected outcome |
|---|----------|-------|------------------|
| 1 | Confident prediction | Select a clear CIFAR-10-like image (e.g., a car or a cat), click **Enviar** | HTTP 200; page shows a category and a confidence ≥ 50%; no uncertainty statement |
| 2 | Prediction (API) | `curl -F "image=@sample.png" http://127.0.0.1:5000/images/predict` | HTTP 200 JSON with `prediction`, `confidence`, `uncertain`, `message`, `model` |
| 3 | Model listing | `curl http://127.0.0.1:5000/api/models` | HTTP 200 JSON listing `cifar10` with metadata; no `artifact_path` exposed |
| 4 | Single endpoint | Request `POST /images/analyze` or `POST /api/predict` | HTTP 404 (routes removed) |
| 5 | Uncertain prediction | Select an ambiguous/noisy image | HTTP 200; confidence < 50%; `uncertain=true`; message ends with "No estoy completamente seguro de esta predicción." |
| 6 | Boundary value | Feed a prediction whose confidence is exactly 50.0% | `uncertain` is `false`; no uncertainty statement |
| 7 | No file | Submit without a file | HTTP 400 with a clear error |
| 8 | Non-image / corrupt | Send a `.txt` renamed to `.png` or a truncated image | HTTP 400 with "El archivo no es una imagen válida..." |
| 9 | Oversized file | Send an image larger than 5 MB | HTTP 413 with the size error |
| 10 | Determinism | Analyze the same image twice | Identical `prediction` and `confidence` both times |
| 11 | No internal leakage | Trigger scenarios 7–9 | No file paths, stack traces, or library names in any message |
| 12 | Model reuse | Submit several images in a row | First request loads the model; subsequent requests are faster (no reload) |

---

## Automated tests

```powershell
pytest -q
```

Expected:
- Unit tests validate preprocessing (shape `(1, 32, 32, 3)`, `float32`, range `[0, 1]`, RGB order), registry parsing, the shared orchestration, and the threshold/message logic (using a stubbed model).
- Integration tests assert:
  - valid fixture image → `200` with `message`, `prediction`, `confidence`, `uncertain`, `model`;
  - `GET /api/models` → `200` with the model metadata;
  - missing file → `400`; undecodable bytes → `400`; oversized → `413`; model failure → `500`.

---

## Reference

- Prediction contract: [`contracts/predict.openapi.yaml`](./contracts/predict.openapi.yaml)
- Model listing contract: [`contracts/api.openapi.yaml`](./contracts/api.openapi.yaml)
- Data model: [`data-model.md`](./data-model.md)
- Preprocessing/normalization decisions: [`research.md`](./research.md) (R3 — validate empirically)

---

## Notes / known risks

- **Normalization is unverified** (research R3). If predictions look wrong on known samples, change the scaling strategy in one place and re-run scenario 1.
- **Backend**: Keras 3 + PyTorch is used because TensorFlow has no Python 3.14 wheels. Keras is the framework named in the constitution; the backend is selected via `KERAS_BACKEND`. If a TensorFlow-capable environment becomes available, switching backends should require only that variable plus a dependency install.
- **Single source of truth**: the prediction endpoint calls `app/ml/inference_service.py`; there is no duplicated inference logic.
