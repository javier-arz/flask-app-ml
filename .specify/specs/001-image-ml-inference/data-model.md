# Phase 1 Data Model: Image ML Inference & Confidence Messaging

**Feature**: `001-image-ml-inference` | **Date**: 2026-10-05

This feature adds no database entities. It introduces in-memory/on-disk data structures used at request time. The **Prediction Result** and **Analysis Error** structures are produced by the single prediction endpoint `POST /images/predict`. `GET /api/models` returns **Model Metadata**, not predictions.

---

## 1. Model Metadata (on disk: `app/models/registry.json`)

Describes an available model. Follows constitution 4.2.

| Field | Type | Required | Description / Validation |
|-------|------|----------|--------------------------|
| `name` | string | yes | Human-readable identifier (e.g., `"cifar10"`). |
| `type` | string | yes | One of `regression`, `classification`, `clustering`. Here: `classification`. |
| `input_modality` | string | yes | One of `image`, `text`. Here: `image`. |
| `input_shape` | array[int] | yes | Expected tensor shape. Here: `[32, 32, 3]`. |
| `output_shape` | array[int] | yes | Prediction output shape. Here: `[10]`. |
| `classes` | array[object] | yes | Ordered list of `{ "key": "<english>", "label": "<spanish>" }`, index = output index. Length MUST equal `output_shape[0]`. |
| `preprocessing` | object | yes | `{ "color_order": "RGB", "resize": [32,32], "interpolation": "INTER_AREA", "scale": "1/255", "dtype": "float32" }`. |
| `framework` | string | yes | `"keras"` (backend recorded separately, e.g., `"backend": "torch"`). |
| `artifact_path` | string | yes | Path relative to the registry file, e.g., `"weights/cifar10.keras"`. MUST resolve to an existing file. |
| `confidence_threshold` | number | yes | Percentage (0–100) below which a prediction is uncertain. Here: `50`. |

**Validation rules**:
- `type`, `input_modality` MUST be within the allowed sets.
- `len(classes) == output_shape[0]`.
- `artifact_path` MUST resolve under `app/models/` (no path traversal).
- `confidence_threshold` MUST be between 0 and 100.

**Exposure**: `GET /api/models` returns the list of model metadata entries (identifier, type, input modality, shapes, category set, framework). `artifact_path` SHOULD be omitted or sanitized in the API response so internal paths are not exposed (FR-013).

---

## 2. Prediction Result (in memory, serialized to JSON)

Represents one successful analysis. Returned by `POST /images/predict`.

| Field | Type | Description / Validation |
|-------|------|--------------------------|
| `message` | string | User-facing Spanish message; includes the uncertainty statement when `uncertain` is true. Non-empty. |
| `prediction` | string | Spanish display label of the top class. MUST be one of the registry labels. |
| `confidence` | number | Percentage 0.0–100.0, one decimal. Equals `top_probability * 100`. |
| `uncertain` | boolean | `true` iff `confidence < confidence_threshold`. |
| `model` | string | Registry `name` of the model used. |

**Invariants**:
- `uncertain == (confidence < 50.0)`.
- `message` contains the uncertainty statement **iff** `uncertain` is `true`.
- `prediction` ∈ registry labels.
- `confidence` is rounded to one decimal place and lies in `[0.0, 100.0]`.

**Serialized example**:
```json
{
  "message": "Detecté: gato (32.4% de certeza). No estoy completamente seguro de esta predicción.",
  "prediction": "gato",
  "confidence": 32.4,
  "uncertain": true,
  "model": "cifar10"
}
```

---

## 3. Uploaded Image (transient, never persisted)

Represents the incoming file during one request.

| Field | Type | Description / Validation |
|-------|------|--------------------------|
| `filename` | string | Original filename; empty string → treated as "no image". |
| `content_type` | string | Declared MIME type (not trusted; validation is by decoding). |
| `raw_bytes` | bytes | File content; zero length → "no image". |
| `decoded` | array (H×W×3) | Result of decoding; `None`/failure → invalid image. |

**Lifecycle**: created from the request → validated → decoded → preprocessed → discarded at the end of the request. No storage, no logging of content (constitution VI: no PII).

---

## 4. Analysis Error (in memory, serialized to JSON)

| Field | Type | Description |
|-------|------|-------------|
| `error` | string | User-facing Spanish error message; MUST NOT contain paths, stack traces, or library names. |
| HTTP status | integer | One of `400`, `413`, `500` (see research R12). |

---

## 5. Request Processing State

```
received
  └─ validate presence/size ──(missing/empty)──▶ 400
  └─ decode image ───────────(undecodable)────▶ 400
  └─ preprocess (RGB, 32×32, /255)
  └─ ensure model loaded (lazy, locked)
  └─ infer ──────────────────(failure)────────▶ 500
  └─ compute confidence + uncertain
  └─ build message
  └─ respond 200 (PredictionResult)
```

Over-size payloads are rejected by the framework before the handler runs and are converted to a JSON `413` response.
