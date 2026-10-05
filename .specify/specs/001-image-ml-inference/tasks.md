---
description: "Task list for Image ML Inference & Confidence Messaging"
---

# Tasks: Image ML Inference & Confidence Messaging

**Input**: Design documents from `.specify/specs/001-image-ml-inference/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/predict.openapi.yaml, contracts/api.openapi.yaml, quickstart.md

**Tests**: Included because the project constitution (`.specify/memory/constitution.md`, §5.2) mandates unit tests for preprocessing and integration tests for the inference endpoint, and `plan.md`/`research.md` (R11) specify pytest.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single Flask project at repository root: `app/`, `config/`, `tests/`.
- ML infrastructure: `app/ml/`; model assets: `app/models/weights/` + `app/models/registry.json`.
- Single prediction endpoint: `app/routes/images/routes.py` + `app/controllers/image_controller.py`.
- Model listing: `app/routes/api/routes.py` + `app/controllers/api_controller.py`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependencies

- [x] T001 Add ML dependencies to `requirements.txt` (`keras==3.13.2`, `torch==2.14.1`, `numpy==2.5.3`, `opencv-python-headless==5.0.0.93`) and install them into the existing `venv`
- [x] T002 [P] Create the `app/ml/` package (`app/ml/__init__.py`) and the test package skeleton (`tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`)
- [x] T003 [P] Copy the model artifact from `F:\estudio\Especialización IA\Machine Learning Avanzado\best_cifar10.keras` to `app/models/weights/cifar10.keras`
- [x] T004 [P] Set `KERAS_BACKEND=torch` in `.env.example` and in the local `.env`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core inference infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create `app/models/registry.json` with the constitution §4.2 fields for the CIFAR-10 model (name, type, input_modality, input_shape, output_shape, classes, preprocessing, framework, artifact_path, confidence_threshold). Constraint: `len(classes) == output_shape[0]`; `confidence_threshold` in [0,100]; `artifact_path` MUST resolve under `app/models/`
- [x] T006 [P] Implement `app/ml/model_registry.py`: load and validate `app/models/registry.json`, resolve `artifact_path` safely under `app/models/`, and expose a typed accessor plus a sanitized public view (omit `artifact_path`)
- [x] T007 [P] Implement `app/ml/preprocessing.py`: decode via OpenCV, BGR→RGB, resize to 32×32 (`INTER_AREA`), cast `float32`, scale by `1/255`, add batch dim → `(1, 32, 32, 3)` (research.md R3/R4)
- [x] T008 Implement `app/ml/predictor.py`: lazy, lock-guarded singleton that loads `app/models/weights/cifar10.keras` on first use and exposes `predict(image_array)` returning the top-1 index and confidence percentage 0.0–100.0. Depends on T006, T007
- [x] T009 [P] Add configuration constants to `config/base_config.py`: `MAX_CONTENT_LENGTH`, `CONFIDENCE_THRESHOLD`, and model/registry path settings
- [x] T010 [P] Register a JSON 413 handler in `app/__init__.py` (FR-012, FR-018)
- [x] T011 [P] Add small committed sample images (32×32 PNG) under `tests/fixtures/cifar10_samples/`
- [x] T012 [P] Add `tests/conftest.py` (Flask app/client fixtures) and `tests/helpers.py` (image builders)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Receive a real prediction (Priority: P1) 🎯 MVP

**Goal**: A valid image yields a prediction through the single endpoint `POST /images/predict`; `GET /api/models` lists available models.

**Independent Test**: Post a valid fixture image to `/images/predict` → 200 with `prediction` (in the registry set), numeric `confidence`, `uncertain`, non-empty `message`, `model="cifar10"`. `GET /api/models` returns the model metadata.

### Tests for User Story 1

- [x] T013 [P] [US1] Unit test preprocessing in `tests/unit/test_preprocessing.py`: shape `(1,32,32,3)`, dtype `float32`, range `[0,1]`, RGB order, `None` for undecodable bytes
- [x] T014 [P] [US1] Unit test predictor raw output in `tests/unit/test_predictor.py` (stubbed model): returns a category within the registry and confidence in [0.0, 100.0]
- [x] T015 [P] [US1] Unit test the orchestration in `tests/unit/test_inference_service.py` (stubbed predictor): builds a `PredictionResult` with `uncertain` present; raises the correct typed error for invalid input
- [x] T016 [P] [US1] Integration test the prediction endpoint in `tests/integration/test_images_predict.py`: POST a fixture image to `/images/predict` → 200 with `message`, `prediction`, `confidence`, `uncertain`, `model`
- [x] T017 [P] [US1] Integration test model listing in `tests/integration/test_api_models.py`: `GET /api/models` → 200 listing `cifar10`; and determinism (the same image posted twice to `/images/predict` returns identical `prediction`/`confidence`, SC-006)

### Implementation for User Story 1

- [x] T018 [US1] Implement `app/ml/inference_service.py`: single source of truth that validates the uploaded file, calls `preprocessing`, calls `predictor`, and builds the `PredictionResult` (including `uncertain` defaulting to `false`)
- [x] T019 [US1] Implement `ImageController.predict()` in `app/controllers/image_controller.py` to delegate to `app/ml/inference_service.py` and return HTTP 200 JSON `{message, prediction, confidence, uncertain, model}`
- [x] T020 [P] [US1] Add the prediction route `POST /images/predict` in `app/routes/images/routes.py` (single endpoint; no duplicates, FR-015/FR-017)
- [x] T021 [US1] Implement model listing: `GET /api/models` route in `app/routes/api/routes.py` and `ApiController.models()` in `app/controllers/api_controller.py` (FR-016)
- [x] T022 [US1] Empirically validate the normalization scheme (research.md R3) against known samples; adjust the single scaling constant in `app/ml/preprocessing.py` if needed

**Checkpoint**: User Story 1 fully functional and testable independently (MVP)

---

## Phase 4: User Story 2 - Be warned when the model is not confident (Priority: P2)

**Goal**: When confidence is strictly below 50%, the message appends an explicit uncertainty statement and the response sets `uncertain=true`.

**Independent Test**: A prediction with confidence < 50.0 yields `uncertain=true` and a message ending with "No estoy completamente seguro de esta predicción."; a prediction ≥ 50.0 yields `uncertain=false` and no such statement.

### Tests for User Story 2

- [x] T023 [P] [US2] Unit test threshold boundary in `tests/unit/test_inference_service.py` (stubbed predictor): 49.9 → uncertain; 50.0 → confident; 50.1 → confident; `uncertain == (confidence < 50.0)`
- [x] T024 [P] [US2] Integration test uncertain case in `tests/integration/test_images_predict.py` (stubbed model): `uncertain=true` and the uncertainty statement present in `message`

### Implementation for User Story 2

- [x] T025 [US2] Implement uncertainty computation in `app/ml/predictor.py`: `uncertain = confidence < 50.0` (strictly below) and append the statement `"No estoy completamente seguro de esta predicción."` only when uncertain (FR-004, FR-005)
- [x] T026 [US2] Propagate the computed `uncertain` value and message through `app/ml/inference_service.py` and the endpoint (FR-014)

**Checkpoint**: User Stories 1 AND 2 both work independently

---

## Phase 5: User Story 3 - Get clear errors instead of failures (Priority: P3)

**Goal**: Missing, non-image, oversized, or model-failure cases return clear JSON errors without crashing or leaking internals.

**Independent Test**: Submit no file → 400; undecodable bytes → 400; oversized payload → 413; simulated model failure → 500; the service stays up and no message contains paths, stack traces, or library names.

### Tests for User Story 3

- [x] T027 [P] [US3] Unit test registry validation in `tests/unit/test_model_registry.py`: missing artifact, `len(classes) != output_shape[0]`, invalid `type`/`input_modality`, and path traversal in `artifact_path` all raise clear errors
- [x] T028 [P] [US3] Integration tests for error paths in `tests/integration/test_images_predict.py` and `tests/integration/test_error_safety.py`: no file → 400 `"No se recibió ninguna imagen."`; undecodable bytes → 400; oversized payload → 413; simulated inference failure → 500 `"No fue posible analizar la imagen en este momento."`

### Implementation for User Story 3

- [x] T029 [US3] Implement input validation and error mapping in `app/ml/inference_service.py`: missing/empty filename or zero bytes → 400; decode failure → 400 (FR-007, FR-008)
- [x] T030 [US3] Implement model load/inference failure handling in `app/ml/predictor.py`: catch exceptions, log details server-side, and raise a typed error mapping to 500 without exposing internals (FR-009, FR-013)

**Checkpoint**: All user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T031 [P] Add a model card at `app/models/weights/cifar10.md` (constitution §5.1/§VI)
- [x] T032 [P] Update `README.md` with ML setup and the endpoints (`POST /images/predict`, `GET /api/models`)
- [x] T033 [P] Security/quality review: assert no user-facing error contains paths, stack traces, or library names in `tests/integration/test_error_safety.py` (FR-013, SC-008)
- [x] T034 [P] Add a latency check for SC-001 in `tests/integration/test_performance.py` and record results
- [x] T035 [P] Apply constitution §5.3: docstrings, type hints, and absolute imports across `app/ml/` and the routes/controllers
- [x] T036 Update `quickstart.md` and run the validation scenarios (confident, uncertain, boundary, no file, non-image, oversized, determinism, single endpoint, model reuse)
- [x] T037 Finalize pinned versions in `requirements.txt` and document `KERAS_BACKEND=torch` in `.env.example`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational completion
  - US1 is the MVP and should be delivered first
  - US2 and US3 build on the US1 pipeline but remain independently testable
- **Polish (Phase 6)**: Depends on all targeted stories being complete

### User Story Dependencies

- **US1 (P1)**: After Foundational - no dependency on other stories
- **US2 (P2)**: After Foundational - extends the US1 result with the computed uncertainty
- **US3 (P3)**: After Foundational - hardens validation/error paths around the US1 pipeline

### Within Each User Story

- Tests written first and failing before implementation
- Foundational infrastructure (registry, preprocessing, predictor) before the shared service
- Shared service before routes/controllers
- Core implementation before integration/error handling

### Parallel Opportunities

- T002–T004 (Setup) run in parallel
- T006, T007, T009, T010, T011, T012 (Foundational) run in parallel once T005 exists; T008 depends on T006+T007
- T013–T017 (US1 tests) run in parallel
- T023/T024 (US2) and T027/T028 (US3) run in parallel within their stories
- T031–T035 (Polish) run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests together:
Task: "Unit test preprocessing in tests/unit/test_preprocessing.py"
Task: "Unit test predictor raw output in tests/unit/test_predictor.py"
Task: "Unit test orchestration in tests/unit/test_inference_service.py"
Task: "Integration test prediction endpoint in tests/integration/test_images_predict.py"
Task: "Integration test model listing in tests/integration/test_api_models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run US1 tests and quickstart scenarios
5. Demo the working prediction

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → real prediction via `POST /images/predict` (MVP)
3. US2 → uncertainty messaging
4. US3 → robust error handling
5. Polish → model card, README, performance/security checks, full validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] labels map tasks to user stories for traceability
- Tests are included per constitution §5.2
- The normalization scheme (T022) is the main technical risk; it is isolated to one constant
- There is exactly one prediction endpoint (`POST /images/predict`); never add duplicate prediction routes (FR-015/FR-017)
- `GET /api/models` is model listing, not a prediction endpoint
- Commit after each task or logical group
