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

- `POST /api/predict` — accepts input, returns prediction with confidence
- `GET /api/models` — lists available models with metadata
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

**Version**: 1.0.0 | **Ratified**: 2026-10-02 | **Last Amended**: 2026-10-02
