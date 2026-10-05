# Phase 0 Research: Image ML Inference & Confidence Messaging

**Feature**: `001-image-ml-inference` | **Date**: 2026-10-05

All NEEDS CLARIFICATION items from the plan's Technical Context are resolved below.

---

## R1. Inference runtime / backend

**Decision**: Run inference with **Keras 3.13.x** using the **PyTorch 2.14.x (CPU)** backend on the existing Python 3.14 environment.

**Rationale**:
- The environment's `venv` runs Python 3.14.7, and the constitution requires Python 3.11+.
- TensorFlow 2.21.0 (latest stable at plan time) publishes wheels only for cp310–cp313 — none for cp314 — so `pip install tensorflow` fails on this interpreter.
- JAX (`jax`/`jaxlib`) publishes no Windows wheels, so a JAX backend is not viable on this machine.
- PyTorch 2.14.1 publishes `cp314` `win_amd64` wheels.
- Keras 3 is backend-agnostic; the `.keras` artifact (`keras_version: 3.13.2`, `Sequential`) loads on any backend. Layers used (InputLayer, RandomFlip/Rotation/Zoom/Translation, Conv2D, BatchNormalization, MaxPooling2D, Flatten, Dense, Dropout) are all backend-agnostic, and the random-augmentation layers are inactive at inference time.

**Alternatives considered**:
- *TensorFlow 2.21 on a separate Python 3.10 venv* — rejected: Python 3.10 is below the constitution's 3.11+ requirement and forces the whole app into a second environment.
- *Install Python 3.12/3.13 and use TensorFlow* — rejected as extra setup burden for an academic deployment; revisit only if the PyTorch backend proves unstable.
- *Keras 3 + JAX* — rejected: no Windows wheels.

**Verification step**: After installing dependencies, load `app/models/weights/cifar10.keras` and run a prediction on a known CIFAR-10 sample to confirm the backend loads the artifact and produces sane probabilities.

---

## R2. Model artifact selection

**Decision**: Use the **`.keras`** artifact (`best_cifar10.keras`), copied to `app/models/weights/cifar10.keras`.

**Rationale**: The `.keras` format is Keras 3 native, self-contained (contains `config.json`, `metadata.json`, `model.weights.h5`), and loads on any Keras 3 backend. The artifact's `metadata.json` reports `keras_version: 3.13.2`.

**Alternatives considered**: The legacy `.h5` (`cifar10_model (1).h5`) — rejected because legacy HDF5 loading in Keras 3 is only supported on the TensorFlow backend, which this environment cannot use (R1). Keep it only as a reference artifact.

**Observed architecture** (from `config.json`): `Sequential`, input `(None, 32, 32, 3)`, output `Dense(10, activation="softmax")`, with `BatchNormalization` after each `Conv2D` and `Dropout` before the final dense layers. No `Rescaling`/`Normalization` layer is embedded — see R3.

---

## R3. Preprocessing / normalization scheme

**Decision**: Decode as color, convert **BGR → RGB**, resize to **32×32** (`INTER_AREA`), cast to `float32`, and **scale to `[0, 1]` by dividing by 255**, then add a batch dimension → shape `(1, 32, 32, 3)`.

**Rationale**: The model contains no built-in rescaling layer, so normalization must match training. The most common CIFAR-10 Keras pipeline scales pixels to `[0, 1]` (`x.astype("float32") / 255`). RGB channel order matches CIFAR-10 (OpenCV decodes as BGR, hence the conversion).

**Alternatives considered**: Channel-wise standardization with CIFAR-10 mean/std (`~[0.4914, 0.4822, 0.4465]` / `~[0.2470, 0.2435, 0.2616]`) — retained as a fallback.

**Verification step (required)**: Because the exact training normalization is not recorded in the artifact, validate empirically during implementation by predicting a few known samples. If top-1 accuracy is poor, switch the normalization strategy. Expose the normalization as a single, documented constant so the scheme can be changed in one place.

---

## R4. Image decoding & format support

**Decision**: Decode bytes with `cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)`.

**Rationale**: OpenCV is the constitution's designated image-processing library and ships an abi3 wheel compatible with Python 3.14. `imdecode` handles JPG/PNG/WEBP and returns `None` on undecodable input, which maps cleanly to the "invalid image" error path. Content is validated by decoding rather than trusting the filename or declared MIME type.

**Alternatives considered**: Pillow — rejected to honor the constitution's OpenCV choice and avoid an extra dependency.

---

## R5. Confidence threshold & uncertainty messaging

**Decision**: Compute `confidence = top_probability * 100` (one decimal place). Set `uncertain = confidence < 50.0` (strictly below). Append the uncertainty statement to the message only when `uncertain` is true. Messages in Spanish:

- Confident: `"Detecté: {label} ({confidence}% de certeza)."`
- Uncertain: `"Detecté: {label} ({confidence}% de certeza). No estoy completamente seguro de esta predicción."`

**Rationale**: Directly implements spec FR-004/FR-005 and the user's request; the strict `< 50%` boundary means exactly 50.0% is treated as confident (spec acceptance scenario US2-3).

**Alternatives considered**: Using the raw probability (0–1) — rejected because spec FR-003 requires a 0–100 percentage.

---

## R6. Response contract

**Decision**: Success returns HTTP 200 JSON:

```json
{
  "message": "Detecté: gato (87.0% de certeza).",
  "prediction": "gato",
  "confidence": 87.0,
  "uncertain": false,
  "model": "cifar10"
}
```

The `uncertain` field is **always present** on success (default `false` from US1 onward; computed in US2), so the response never violates the contract during incremental delivery.

Errors return JSON `{ "error": "<mensaje>" }` with an appropriate status code. The existing UI reads `data.message` (success) and `data.error` (error), so no frontend change is required (spec FR-006).

This exact success shape is returned by the single prediction endpoint `POST /images/predict`; see R13. `GET /api/models` returns model metadata, not predictions.

**Rationale**: Keeps backward compatibility while exposing the structured fields required by spec FR-014 and aligned with constitution 3.4 (`prediction`, `confidence`, `model`).

**Alternatives considered**: A new nested schema (e.g., `{"result": {...}}`) — rejected because it would require changing the existing page. Sharing one endpoint for prediction and model listing — rejected because they are different operations.

---

## R7. Category labels

**Decision**: Store canonical CIFAR-10 keys (English) and a Spanish display label per class in the registry. The message uses the Spanish label; the `prediction` field uses the Spanish label too, with the canonical key available in the registry.

CIFAR-10 classes (index order 0–9): `airplane→avión`, `automobile→automóvil`, `bird→ave`, `cat→gato`, `deer→ciervo`, `dog→perro`, `frog→rana`, `horse→caballo`, `ship→barco`, `truck→camión`.

**Rationale**: The interface is Spanish; the registry keeps a stable, testable canonical mapping.

**Alternatives considered**: Returning English labels — rejected as inconsistent with the Spanish UI.

---

## R8. Model storage & registry

**Decision**: Store the artifact at `app/models/weights/cifar10.keras` and metadata at `app/models/registry.json` (constitution 4.1). The manifest follows constitution 4.2 fields: `name`, `type`, `input_modality`, `input_shape`, `output_shape`, `classes`, `preprocessing`, `framework`, plus `artifact_path` and `confidence_threshold`. `app/ml/model_registry.py` loads and validates the manifest.

**Rationale**: Directly satisfies constitution 3.2 (registry manages availability/metadata) and 4.1/4.2.

**Alternatives considered**: Hardcoding metadata in Python — rejected because the constitution mandates a registry manifest. A full multi-model registry with dynamic discovery — out of scope for a single-model academic feature; the loader is written to support additional entries later.

---

## R9. Upload size limit

**Decision**: Set `MAX_CONTENT_LENGTH = 5 * 1024 * 1024` (5 MB) in `config/base_config.py`, and register a JSON 413 handler so oversized uploads return `{"error": ...}` instead of an HTML error page.

**Rationale**: Mitigates the large-file risk noted in the previous feature's spec and bounds memory; keeps the JSON error contract (spec FR-012).

**Alternatives considered**: No limit — rejected (memory risk). A larger limit — rejected as unnecessary for 32×32 inputs.

---

## R10. Lazy loading & thread safety

**Decision**: `app/ml/predictor.py` exposes a module-level singleton loaded on first use, guarded by a `threading.Lock`. The Flask development server is threaded, so concurrent first requests must not double-load the model.

**Rationale**: Constitution 3.2 (lazy loading, bounded memory) and spec FR-011 (no per-request reload).

**Alternatives considered**: Eager load at startup — rejected (violates 3.2, slows startup). No lock — rejected (race on first concurrent requests).

---

## R11. Testing approach

**Decision**: Use `pytest`.
- **Unit** (`tests/unit/`): preprocessing shape/dtype/range/color order; registry parsing; threshold/message logic using a stubbed model (no real artifact needed).
- **Integration** (`tests/integration/`): `POST /images/predict` with a committed fixture image → 200 with `prediction`, `confidence`, `uncertain`, `message`, `model`; no-file → 400; undecodable bytes → 400; `GET /api/models` → 200.
- **Fixtures** (`tests/fixtures/cifar10_samples/`): a small number of tiny committed images (e.g., 32×32 PNGs) so tests never download data.

**Rationale**: Constitution 5.2 requires unit tests for preprocessing and integration tests for the inference endpoint, with committed fixtures. Stubbing the model keeps unit tests fast and independent of the heavy dependency.

**Alternatives considered**: Testing only end-to-end with the real model — rejected as slow and brittle.

---

## R12. Error handling & status codes

**Decision**:
- No file / empty filename / zero bytes → **400** `{"error": "No se recibió ninguna imagen."}`
- Undecodable or unsupported content → **400** `{"error": "El archivo no es una imagen válida o el formato no está soportado."}`
- Payload over `MAX_CONTENT_LENGTH` → **413** `{"error": "La imagen excede el tamaño máximo permitido (5 MB)."}`
- Model load/inference failure → **500** `{"error": "No fue posible analizar la imagen en este momento."}` (details logged server-side, never returned)

**Rationale**: Satisfies spec FR-007/FR-008/FR-009/FR-012/FR-013; internal details are logged, not exposed.

**Alternatives considered**: 415 for unsupported media type — a valid alternative, but 400 keeps a simpler, uniform client contract for the existing page.

---

## R13. Prediction endpoint consolidation

**Decision**: Expose **exactly one** prediction endpoint, `POST /images/predict`, backed by `app/ml/inference_service.py`. The duplicate routes `POST /images/analyze` and `POST /api/predict` were removed. `GET /api/models` remains as a distinct operation (model listing).

**Rationale**: The user requires a single prediction endpoint with no duplicated endpoints or controllers. Consolidating removes the duplicate HTTP surface and controller method while keeping one inference implementation. `GET /api/models` is not a prediction endpoint and is retained.

**Alternatives considered**:
- *Two prediction entry points (`/images/analyze` + `/api/predict`)* — rejected: duplicated endpoint/controller surface.
- *Keep only `/api/predict` (constitution §3.4) and point the page at it* — rejected: the user chose `/images/predict` as the single route.
- *Keep only `/images/analyze`* — rejected: the user specified `/images/predict` as the route name.

**Constitution note**: Resolved by constitution amendment **v1.1.0** — §3.4 now sanctions `POST /images/predict` as the single prediction endpoint.
