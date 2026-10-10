# Implementation Plan: Spam ML Inference

**Branch**: `003-spam-ml-inference` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-spam-ml-inference/spec.md`

## Summary

Implementar una operación de detección de spam siguiendo la misma arquitectura que `/images/predict`. El modelo `mi_modelo_spam.keras` es un clasificador binario (spam/no-spam) con una capa `TextVectorization` integrada que maneja todo el preprocesamiento internamente. Se creará un blueprint `spam` con su controlador, servicio de inferencia y plantilla web.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Flask, Keras 3, TensorFlow (backend para TextVectorization), NumPy

**Storage**: N/A (no se requiere persistencia para esta funcionalidad)

**Testing**: pytest (unit tests para preprocessing, integration tests para el endpoint)

**Target Platform**: Windows/Linux server (aplicación web Flask)

**Project Type**: Web service (Flask blueprint)

**Performance Goals**: Respuesta en menos de 5 segundos por análisis

**Constraints**: El modelo requiere `KERAS_BACKEND=tensorflow` debido a la capa `TextVectorization`

**Scale/Scope**: Académico — un modelo de spam, un endpoint de predicción, una página web

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| §3.1 Blueprint-Based Modularity | PASS | Se creará blueprint `spam` con estructura idéntica a `images` |
| §3.2 Lazy Model Loading | PASS | El modelo se cargará perezosamente usando el patrón de `predictor.py` |
| §3.3 Preprocessing Parity | PASS | El modelo tiene `TextVectorization` integrada — no requiere preprocesamiento externo |
| §3.4 RESTful Inference API | PASS | `POST /spam/predict` para predicción, `GET /api/models` para listado |
| §4.1 Storage Convention | PASS | El modelo se copiará a `app/models/weights/mi_modelo_spam.keras` |
| §4.2 Model Metadata | PASS | Se registrará en `registry.json` con todos los campos requeridos |
| §5.1 Documentation | PASS | Docstrings en todos los módulos |
| §5.2 Testing | PASS | Unit + integration tests |
| §5.3 Code Style | PASS | PEP 8, type hints, absolute imports |

## Project Structure

### Documentation (this feature)

```text
specs/003-spam-ml-inference/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── spam-predict.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── controllers/
│   └── spam_controller.py       # Nuevo: controlador para detección de spam
├── ml/
│   ├── spam_predictor.py        # Nuevo: loader perezoso del modelo de spam
│   └── inference_service.py     # Modificado: agregar analyze_text()
├── models/
│   ├── weights/
│   │   └── mi_modelo_spam.keras  # Nuevo: artefacto del modelo
│   └── registry.json            # Modificado: agregar entrada del modelo de spam
├── routes/
│   └── spam/
│       ├── __init__.py          # Nuevo: blueprint spam
│       └── routes.py            # Nuevo: rutas / y /predict
├── templates/
│   └── spam/
│       └── index.html           # Nuevo: página web de detección de spam
└── __init__.py                  # Modificado: registrar blueprint spam

tests/
├── unit/
│   └── test_spam_predictor.py   # Nuevo: unit tests
└── integration/
    └── test_spam_predict.py     # Nuevo: integration tests
```

**Structure Decision**: Se sigue la misma estructura que la funcionalidad de imágenes, creando un blueprint `spam` paralelo al blueprint `images`.

## Complexity Tracking

> No violations — all constitution gates pass.
