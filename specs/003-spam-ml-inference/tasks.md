# Tasks: Spam ML Inference

**Input**: Design documents from `/specs/003-spam-ml-inference/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `app/` for source code, `tests/` for tests
- Paths shown below follow the existing project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Copy spam model artifact to `app/models/weights/mi_modelo_spam.keras`
- [x] T002 [P] Update `app/models/registry.json` with spam_classifier entry (name: spam_classifier, type: classification, input_modality: text, input_shape: [1], output_shape: [1], classes: [{"key": "ham", "label": "no spam"}, {"key": "spam", "label": "spam"}], preprocessing: {"standardize": "lower_and_strip_punctuation", "split": "whitespace", "max_tokens": 5000, "output_sequence_length": 100}, framework: keras, artifact_path: weights/mi_modelo_spam.keras, confidence_threshold: 50)
- [x] T003 [P] Install TensorFlow dependency in `requirements.txt` (required for TextVectorization layer)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create spam blueprint structure: `app/routes/spam/__init__.py` (Blueprint('spam', __name__)) and `app/routes/spam/routes.py` with index and predict route stubs
- [x] T005 Create spam controller in `app/controllers/spam_controller.py` with index() and predict() methods (stubs returning empty responses)
- [x] T006 Register spam controller export in `app/controllers/__init__.py` (add SpamController import)
- [x] T007 Register spam blueprint in `app/__init__.py` (from app.routes.spam import bp as spam_blueprint, app.register_blueprint(spam_blueprint, url_prefix='/spam'))
- [x] T008 Create spam template in `app/templates/spam/index.html` extending base.html with text input form and result display area
- [x] T009 [P] Create spam predictor in `app/ml/spam_predictor.py` with lazy model loading pattern (KERAS_BACKEND=tensorflow, thread-safe, keras.saving.load_model)
- [x] T010 [P] Update `app/ml/inference_service.py` with analyze_text() function for spam prediction (text validation, model inference, result formatting)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Análisis de spam desde la interfaz web (Priority: P1) MVP

**Goal**: Un usuario puede ingresar texto en la interfaz web y obtener una clasificación de spam/no-spam con nivel de confianza

**Independent Test**: Navegar a /spam, ingresar texto spam, verificar que el resultado muestra "spam" con confianza > 80%

### Tests for User Story 1 (OPTIONAL - only if tests requested)

- [x] T011 [P] [US1] Contract test for POST /spam/predict in `tests/integration/test_spam_predict.py`
- [x] T012 [P] [US1] Integration test for web interface in `tests/integration/test_spam_web.py`

### Implementation for User Story 1

- [x] T013 [US1] Implement spam predictor load_model() in `app/ml/spam_predictor.py` with tensorflow backend and error handling
- [x] T014 [US1] Implement spam predictor predict() in `app/ml/spam_predictor.py` returning (class_index, confidence_percent)
- [x] T015 [US1] Implement analyze_text() in `app/ml/inference_service.py` with text validation (non-empty, max 10000 chars), inference, and result formatting
- [x] T016 [US1] Implement SpamController.predict() in `app/controllers/spam_controller.py` handling form data and InferenceError
- [x] T017 [US1] Implement spam web interface in `app/templates/spam/index.html` with text input, submit button, loading indicator, and result display
- [x] T018 [US1] Add navigation link to spam page in `app/templates/base.html`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Consulta de modelos disponibles vía API (Priority: P2)

**Goal**: El modelo de spam aparece en el listado de modelos disponibles junto con el modelo de imágenes

**Independent Test**: Consultar GET /api/models y verificar que spam_classifier aparece con su metadata correcta

### Tests for User Story 2 (OPTIONAL - only if tests requested)

- [x] T019 [P] [US2] Integration test for model listing in `tests/integration/test_api_models.py`

### Implementation for User Story 2

- [x] T020 [US2] Verify spam model appears in `app/ml/inference_service.py` list_models() output (should already work after T002)
- [x] T021 [US2] Add spam model metadata test in `tests/unit/test_model_registry.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Manejo de errores en el análisis (Priority: P2)

**Goal**: El sistema maneja correctamente textos vacíos, demasiado largos, y errores de inferencia con mensajes claros

**Independent Test**: Enviar texto vacío a /spam/predict y verificar mensaje de error apropiado

### Tests for User Story 3 (OPTIONAL - only if tests requested)

- [x] T022 [P] [US3] Integration test for error handling in `tests/integration/test_spam_errors.py`

### Implementation for User Story 3

- [x] T023 [US3] Add text validation in `app/ml/inference_service.py` analyze_text() for empty/whitespace-only text (error: "No se recibió ningún texto.")
- [x] T024 [US3] Add text length validation in `app/ml/inference_service.py` analyze_text() for text > 10000 chars (error: "El texto excede la longitud máxima permitida.")
- [x] T025 [US3] Add model loading error handling in `app/ml/spam_predictor.py` (error: "No fue posible cargar el modelo en este momento.")
- [x] T026 [US3] Add inference error handling in `app/ml/inference_service.py` analyze_text() (error: "No fue posible analizar el texto en este momento.")
- [x] T027 [US3] Add error display in `app/templates/spam/index.html` for error responses from the API

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T028 [P] Update README.md with spam detection endpoint documentation
- [x] T029 [P] Add model card for spam classifier in `app/models/weights/spam_classifier.md`
- [x] T030 Run quickstart.md validation scenarios
- [x] T031 [P] Add Spanish error messages consistency check across all spam-related code
- [x] T032 Code style compliance check (PEP 8, type hints, absolute imports)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on T002 (registry entry)
- **User Story 3 (P2)**: Can start after User Story 1 - Depends on analyze_text() implementation

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational tasks marked [P] can run in parallel (T006, T009, T010)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for POST /spam/predict in tests/integration/test_spam_predict.py"
Task: "Integration test for web interface in tests/integration/test_spam_web.py"

# Launch all models for User Story 1 together:
Task: "Implement spam predictor load_model() in app/ml/spam_predictor.py"
Task: "Implement spam predictor predict() in app/ml/spam_predictor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
