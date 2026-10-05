# Implementation Plan: Image ML Inference & Confidence Messaging

**Branch**: `001-image-ml-inference` | **Date**: 2026-10-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `.specify/specs/001-image-ml-inference/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

## Summary

Replace the stub in `ImageController` with real inference using the user-provided CIFAR-10 Keras model. The inference capability is exposed through **a single prediction endpoint** — `POST /images/predict` — and the available model is listed through `GET /api/models`. Duplicate prediction routes (`/images/analyze` and `/api/predict`) were removed so there is one implementation and one endpoint.

The endpoint decodes and preprocesses the uploaded image, runs a lazily-loaded singleton classifier, and returns the predicted category, a confidence percentage, and an uncertainty note when confidence is strictly below 50%.

Because the project runs on Python 3.14 and TensorFlow publishes no 3.14 wheels (only cp310–cp313) while JAX publishes no Windows wheels, inference runs on **Keras 3 with the PyTorch backend**. Keras is the framework named in the constitution; the backend is a runtime detail.

## Technical Context

**Language/Version**: Python 3.14.7 (existing `venv`; constitution requires 3.11+)

**Primary Dependencies**:
- Existing: Flask 3.1.3, Werkzeug 3.1.9, python-dotenv
- New: `keras` 3.13.2 (matches the artifact's `keras_version`), `torch` 2.14.1 (CPU, Keras backend), `numpy` 2.5.3, `opencv-python-headless` 5.0.0.93 (abi3)
- Testing: `pytest` 9.1.1 (already installed)

**Storage**: Model artifact on disk at `app/models/weights/cifar10.keras` plus a metadata manifest at `app/models/registry.json`. No database schema changes.

**Testing**: pytest — unit tests (preprocessing, predictor, inference service, registry) and integration tests (`POST /images/predict`, `GET /api/models`, error paths). Committed small sample fixtures; unit tests stub the model to avoid loading the real artifact.

**Target Platform**: Windows 10/11 development (local Flask server); Linux-compatible.

**Project Type**: Web application (Flask server-rendered templates + AJAX + JSON API).

**Performance Goals**: A prediction for a valid image within 2 seconds for at least 95% of requests (SC-001). Model loaded once and reused across requests (FR-011).

**Constraints**: Model input tensor `(32, 32, 3)`; 10 CIFAR-10 classes; confidence threshold 50%; upload size bounded via `MAX_CONTENT_LENGTH`; exactly one prediction endpoint (FR-015/FR-017).

**Scale/Scope**: Academic deployment; single model; one image per request; low concurrency.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate (from `.specify/memory/constitution.md`) | Status | Notes |
|-----------------------------------------------|--------|-------|
| 3.1 Blueprint-based modularity | PASS | `images` blueprint (index + predict) and `api` blueprint (`/api/models`); ML infrastructure isolated in `app/ml/`. |
| 3.2 Lazy model loading | PASS | Predictor loads the model on first use via a guarded singleton; no load at app startup. Registry provides metadata/availability. |
| 3.3 Preprocessing parity | PASS | Input shape, color order, resize, and normalization documented in `research.md`/`data-model.md`. |
| 3.4 RESTful inference API | PASS | Constitution amended to v1.1.0: the sanctioned single prediction endpoint is `POST /images/predict`, and `GET /api/models` lists models. |
| II. Technology stack — Python 3.11+ | PASS | Python 3.14.7 satisfies 3.11+. |
| II. Technology stack — TensorFlow/Keras | PASS | Framework is Keras (explicitly listed). The PyTorch backend is a runtime detail; TensorFlow is unavailable on Python 3.14. |
| II. Technology stack — OpenCV | PASS | Image decoding/resize via `opencv-python-headless` (abi3 wheel supports 3.14). |
| 5.1 Documentation | PASS | Docstrings on all public functions; model card for the CIFAR-10 artifact. |
| 5.2 Testing | PASS | Unit tests for preprocessing, predictor, inference service, and registry; integration tests for the endpoint and error paths; committed sample fixtures. |
| 5.3 Code style | PASS | PEP 8, type hints on public functions, absolute imports. |
| VI. Data & ethics | PASS | No PII; image is not persisted; model card documents provenance and limitations. |

**Post-Phase 1 re-check**: All gates PASS. §3.4 is satisfied as of constitution v1.1.0 (single prediction endpoint `POST /images/predict`).

## Project Structure

### Documentation (this feature)

```text
.specify/specs/001-image-ml-inference/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── predict.openapi.yaml   # POST /images/predict
│   └── api.openapi.yaml       # GET /api/models
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── ml/                          # ML infrastructure (single source of truth)
│   ├── __init__.py
│   ├── model_registry.py        # Loads/validates registry.json; typed metadata accessor
│   ├── preprocessing.py         # Decode, color-convert, resize, normalize (OpenCV)
│   ├── predictor.py             # Lazy singleton loader + raw top-1 prediction
│   └── inference_service.py     # Orchestration: validate -> preprocess -> predict -> result
├── models/
│   ├── registry.json            # Model metadata manifest (constitution 4.1/4.2)
│   └── weights/
│       ├── cifar10.keras        # Model artifact (provided by user)
│       └── cifar10.md           # Model card
├── controllers/
│   ├── image_controller.py      # index() + predict()  (the prediction endpoint)
│   └── api_controller.py        # models()             (model listing)
├── routes/
│   ├── images/routes.py         # GET /images/, POST /images/predict
│   └── api/routes.py            # GET /api/models
├── templates/
│   └── images/index.html        # Renders data.message / data.error
app/__init__.py                  # Registers blueprints; JSON 413 handler
config/
└── base_config.py               # MAX_CONTENT_LENGTH, threshold, model paths
tests/
├── conftest.py
├── helpers.py
├── unit/
│   ├── test_preprocessing.py
│   ├── test_predictor.py
│   ├── test_inference_service.py
│   └── test_model_registry.py
├── integration/
│   ├── test_images_predict.py
│   ├── test_api_models.py
│   ├── test_error_safety.py
│   └── test_performance.py
└── fixtures/
    └── cifar10_samples/
```

**Structure Decision**: Keep the existing single Flask application layout. `app/ml/inference_service.py` is the single source of truth for prediction; the `images` blueprint exposes it at `POST /images/predict` and the `api` blueprint exposes model listing at `GET /api/models`. Model assets follow the constitution's storage convention.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. The previous §3.4 deviation was resolved by constitution amendment **v1.1.0**, which sanctions `POST /images/predict` as the single prediction endpoint.
