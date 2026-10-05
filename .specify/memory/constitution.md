# flask-app-ml Constitution

## Preamble

This document establishes the governing principles for the **flask-app-ml** project — an academic initiative within a University Specialization program. The project's primary objective is to **deploy pre-trained machine learning models as a web application**, making inference capabilities accessible through a RESTful interface. Models are trained externally (Google Colab, Jupyter Notebooks) and exported as `.h5` artifacts for integration.

---

## I. Project Scope & Nature

This is an **academic deployment project**, not a production system. The focus is on:

- Serving pre-trained models via a web interface
- Demonstrating end-to-end ML pipeline integration (preprocessing → inference → response)
- Covering diverse model types: **regression**, **classification**, **supervised**, and **unsupervised** learning
- Supporting **text** and **image** input modalities

**Out of scope:** Online training, model retraining, hyperparameter tuning, and production-grade scalability.

---

## II. Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Web Framework | Flask | Lightweight, extensible, academic standard |
| ML Framework | TensorFlow / Keras | Native `.h5` support, industry standard |
| Image Processing | OpenCV | Efficient preprocessing pipeline |
| ORM | SQLAlchemy + Flask-Migrate | Structured data persistence |
| Database | SQLite (dev) / PostgreSQL (prod) | Configurable via environment |
| Python | 3.11+ | Type hints, modern syntax |

---

## III. Architectural Principles

### 3.1 Blueprint-Based Modularity

- Each resource (images, text, predictions, models) is a **Flask Blueprint**
- Blueprints are registered with explicit `url_prefix`
- Controllers handle business logic; models define data structures; templates render views

### 3.2 Lazy Model Loading

- Models are **loaded on-demand**, not at application startup
- A model registry manages availability and metadata
- Memory footprint remains bounded regardless of model count

### 3.3 Preprocessing Parity

- Preprocessing during inference **must match** training-time transformations exactly
- Document per model: input shape, normalization scheme, tokenization, resize dimensions
- OpenCV pipelines for images; Keras `Tokenizer` / padding for text

### 3.4 RESTful Inference API

- `POST /images/predict` — accepts an uploaded image, returns the prediction with confidence. This is the **single** prediction endpoint; duplicate prediction routes are not permitted.
- `GET /api/models` — lists available models with metadata (model listing, not a prediction endpoint)
- Responses are JSON: `{ "prediction": ..., "confidence": ..., "model": ... }`
- Clear error handling: model not found, invalid input, preprocessing failure

---

## IV. Model Management

### 4.1 Storage Convention

```
app/
└── models/
    ├── weights/           # .h5 files
    │   ├── image_classifier.h5
    │   └── text_regressor.h5
    └── registry.json      # Model metadata manifest
```

### 4.2 Model Metadata

Each registered model must document:

| Field | Description |
|-------|-------------|
| `name` | Human-readable identifier |
| `type` | regression / classification / clustering |
| `input_modality` | image / text |
| `input_shape` | Expected tensor dimensions |
| `output_shape` | Prediction output dimensions |
| `classes` | Label mapping (classification only) |
| `preprocessing` | Required transformation pipeline |
| `framework` | TensorFlow / Keras / OpenCV |

---

## V. Code Quality Standards

### 5.1 Documentation

- All modules, classes, and functions include **docstrings**
- README documents: setup, available models, API endpoints, usage examples
- Each model includes a card describing its origin, training data, and performance metrics

### 5.2 Testing

- Unit tests for preprocessing functions
- Integration tests for inference endpoints (model loads, prediction succeeds)
- Test fixtures use small, committed sample inputs — never download at test time

### 5.3 Code Style

- PEP 8 compliance
- Type hints on all public functions
- Absolute imports only (`from app.models import Image`)
- No backslashes in import statements

---

## VI. Data & Ethics

- No personally identifiable information (PII) is processed without explicit consent
- Model biases and limitations must be documented in the model card
- Academic integrity: all models must have clear provenance (training source, dataset, authorship)

---

## VII. Governance

- This constitution supersedes all other practices
- Amendments require: written proposal, rationale, and migration plan
- All feature specifications (`spec.md`) must demonstrate compliance with these principles
- The `/speckit.analyze` command verifies cross-artifact consistency against this constitution

---

## Amendment Log

### 1.1.0 — 2026-10-05 — Single prediction endpoint (`POST /images/predict`)

**Proposal**: In §3.4, replace the sanctioned prediction route `POST /api/predict` with `POST /images/predict`, and state that exactly one prediction endpoint is permitted. `GET /api/models` (model listing) is unchanged.

**Rationale**: The feature `001-image-ml-inference` serves prediction through a single endpoint to avoid duplicated endpoints/controllers. The previously named route (`/api/predict`) conflicted with the implemented route (`/images/predict`), producing a documented constitution deviation. Sanctioning the implemented route removes the deviation without adding a duplicate endpoint.

**Migration plan**:

1. Update §3.4 to name `POST /images/predict` as the single prediction endpoint.
2. In `.specify/specs/001-image-ml-inference/plan.md`, mark the §3.4 gate PASS and remove the corresponding Complexity Tracking entry.
3. Update `research.md` (R13) and the feature checklist note to reflect the amendment.
4. No code change is required: the implementation already serves `POST /images/predict`.
5. Future inference features MUST expose a single prediction endpoint; model listing remains at `GET /api/models`.

**Impact**: Non-breaking for the current implementation; aligns the governing document with the code.

---

**Version**: 1.1.0 | **Ratified**: 2026-10-02 | **Last Amended**: 2026-10-05
