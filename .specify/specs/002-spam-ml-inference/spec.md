# Feature Specification: Spam Detection & Text ML Inference

**Feature Branch**: `002-spam-ml-inference`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "Necesito crear una nueva operación en la aplicación. De la misma forma que ya existe la operación '/images/predict' con su propia vista web, handler y controlador quiero que me ayudes a crear la operación 'spam/predict' con las mismas características, solo que esta vez, el modelo a usar para predecir si el input recibido puede interpretarse como spam o no es: 'F:\estudio\Especialización IA\Machine Learning Avanzado\mi_modelo_spam.keras'. De igual forma, este nuevo modelo debería verse reflejado en los resultados de la operación de consulta de modelos. Mantente alineado con buenas prácticas y estándares de la industria y básate por la operación que te pasé como referencia, que me parece muy muy bien estructurada."

## Clarifications

### Session 2026-10-10

- **Q**: How many prediction endpoints should exist now that a second modality is added?
  **A**: The single-endpoint rule (constitution §3.4) is **per feature/modality**, not global. `POST /images/predict` and `POST /spam/predict` are each the single prediction endpoint of their own feature. Two *distinct* modalities (image, text) justify two endpoints; two endpoints serving the *same* operation would still be a violation. The model-listing endpoint `GET /api/models` remains a listing operation, not a prediction endpoint.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Classify a message as spam or ham (Priority: P1)

A user opens the spam analysis page, pastes or types a message (an email, SMS, or short text), and submits it. The system classifies the text with the project's pre-trained spam classifier and shows the verdict (spam / not spam) together with the confidence, without reloading the page.

**Why this priority**: This is the core value of the feature and the MVP. Without it the feature delivers nothing.

**Independent Test**: Submit a known-spam message and a known-legitimate message to `POST /spam/predict` and confirm each returns the correct verdict, a confidence value, the model identifier, and the uncertainty flag.

**Acceptance Scenarios**:

1. **Given** the spam analysis page with a non-empty message, **When** the user submits, **Then** the page displays the verdict and its confidence without reloading.
2. **Given** a text submitted to `POST /spam/predict`, **When** it is analyzed, **Then** the response contains the verdict, the confidence, the model identifier, and the uncertainty flag.
3. **Given** any valid text, **When** it is analyzed, **Then** the verdict is one of the model's known verdicts.
4. **Given** the application, **When** its routes are inspected, **Then** there is exactly one prediction endpoint per modality — one for images and one for text — and no duplicated text-prediction route.
5. **Given** the image analysis page, **When** a request is made to `POST /spam/predict`, **Then** it returns 404; and vice versa.

---

### User Story 2 - Discover the new model through model listing (Priority: P2)

An API consumer asks which models the application can use and receives both the image classifier and the spam classifier, each with enough metadata to tell them apart and to know what kind of input each expects.

**Why this priority**: The user explicitly asked for the new model to appear in model-listing results. Without it the operation works but the capability is undocumented to consumers, and the project constitution (§4.2) requires registered metadata for every model. Secondary to producing a verdict at all.

**Independent Test**: Request `GET /api/models` and confirm it lists two entries — one image classifier and one text classifier — each with its modality, input/output expectations, and labels.

**Acceptance Scenarios**:

1. **Given** a request to `GET /api/models`, **When** it is handled, **Then** the response lists every registered model, including the spam classifier.
2. **Given** the spam classifier entry, **When** its metadata is inspected, **Then** it declares a text input modality, its input and output shape, and its verdict labels.
3. **Given** any model entry, **When** the listing response is inspected, **Then** no internal file-system path or artifact location is exposed.
4. **Given** the image classifier entry, **When** the listing response is inspected, **Then** it is unchanged from its current output apart from the addition of the new entry.

---

### User Story 3 - Be warned when the classifier is not confident (Priority: P3)

When the confidence for the top verdict is below the configured threshold, the response explicitly states that the system is not fully certain, so the user does not over-trust an unreliable verdict.

**Why this priority**: Communicating uncertainty is an industry-standard expectation for ML features and prevents misleading users. It mirrors the behaviour already established for the image feature, so it is valuable but secondary.

**Independent Test**: Analyze messages that yield confidence below and at/above the threshold and confirm the uncertainty flag and message are present and absent respectively.

**Acceptance Scenarios**:

1. **Given** a verdict whose confidence is strictly below the threshold, **When** the result is returned, **Then** the uncertainty flag is `true` and the message includes an explicit statement that the system is not fully certain.
2. **Given** a verdict whose confidence is at or above the threshold, **When** the result is returned, **Then** the uncertainty flag is `false` and the message does not include the uncertainty statement.
3. **Given** a confidence value exactly at the threshold, **When** the result is returned, **Then** it is treated as confident (only values strictly below the threshold are uncertain).
4. **Given** each registered model, **When** it is analyzed, **Then** the threshold applied is the one registered for that model, not a single hard-coded value.

---

### User Story 4 - Get clear errors instead of failures (Priority: P4)

When the message is missing, empty, blank, or the model cannot produce a verdict, the caller receives a clear, human-readable error and the service keeps running.

**Why this priority**: Reliability and safe failure are required for a trustworthy feature, but they do not block the primary happy path.

**Independent Test**: Submit an empty form, whitespace-only text, and a request while the model is unavailable; confirm each returns a clear error and the service remains available.

**Acceptance Scenarios**:

1. **Given** a submission with no text, **When** it is sent, **Then** the system responds with HTTP 400 and a clear error message.
2. **Given** a submission with whitespace-only text, **When** it is sent, **Then** the system responds with HTTP 400 and a clear error message.
3. **Given** the model is unavailable or inference fails, **When** a valid message is sent, **Then** the system responds with HTTP 500 and a clear error message without terminating the service.
4. **Given** the spam model fails to load, **When** the image prediction operation is used, **Then** the image feature continues to work unaffected.
5. **Given** any error, **When** the response is inspected, **Then** it is machine-readable and exposes no internal implementation details.

---

### Edge Cases

- The message consists only of whitespace, punctuation, or emoji with no recognizable words.
- The message is extremely long, far beyond what the model was trained on.
- The message is empty when stripped of HTML markup but was submitted from a rich-text editor.
- The message contains characters outside the model's known vocabulary, including accented or non-Latin characters.
- The same message is analyzed twice; the verdict and confidence must be identical (deterministic).
- A message that is neither clearly spam nor clearly legitimate sits near the decision boundary (roughly 50/50).
- Two requests arrive at the same time; neither must corrupt the other's result.
- Both models are used in the same process; loading one must not evict, corrupt, or degrade the other.
- The user submits while the model is still being loaded for the first time.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST classify a submitted text message as spam or not spam using the project's pre-trained spam classifier.
- **FR-002**: The response MUST include the verdict, the confidence percentage (0.0–100.0, rounded to one decimal place), the model identifier, and the uncertainty flag.
- **FR-003**: WHEN the confidence is strictly below the registered threshold for the model used, the user-facing message MUST include an explicit statement that the system is not fully certain, and the uncertainty flag MUST be `true`.
- **FR-004**: WHEN the confidence is at or above the registered threshold, the user-facing message MUST NOT include the uncertainty statement, and the uncertainty flag MUST be `false`.
- **FR-005**: System MUST serve the text prediction through exactly one text prediction endpoint, `POST /spam/predict`, mirroring the structure of the existing image prediction operation (web view, request handler, controller).
- **FR-006**: System MUST expose `GET /spam/` serving the spam analysis view with a text input, a submit action, and a result area.
- **FR-007**: The text prediction endpoint MUST preserve the same response contract already produced for the image operation (message, prediction, confidence, uncertain, model) so both operations behave consistently for clients.
- **FR-008**: System MUST reject a submission with no text, or with text that is empty or whitespace-only, with HTTP 400 and a clear error message.
- **FR-009**: System MUST handle model load or inference failures without terminating the service, returning HTTP 500 and a clear error message.
- **FR-010**: Verdicts MUST be restricted to the model's known verdict set.
- **FR-011**: The verdict MUST be restricted to the model's known category set; the system MUST NOT invent verdicts outside it.
- **FR-012**: System MUST reuse a loaded model across requests rather than re-reading the artifact on every request, per constitution §3.2.
- **FR-013**: System MUST keep loaded models isolated from one another: loading or failing to load the spam model MUST NOT affect the availability, performance, or correctness of the image model.
- **FR-014**: The response MUST remain machine-readable JSON for both success and error outcomes.
- **FR-015**: System MUST NOT expose internal implementation details (file paths, stack traces, library names) in any user-facing error message.
- **FR-016**: System MUST expose `GET /api/models`, listing every registered model with its metadata, including the spam classifier.
- **FR-017**: Each registered model MUST declare the metadata required by constitution §4.2, and the spam classifier MUST declare a text input modality, its input and output shape, its verdict labels, and the preprocessing required to match training-time transformation.
- **FR-018**: System MUST expose **exactly one** text prediction endpoint; it MUST NOT create duplicate text prediction routes or duplicated controller logic.
- **FR-019**: System MUST register the spam model artifact within the project's model storage convention (constitution §4.1) rather than loading it from an arbitrary external location.
- **FR-020**: The spam analysis view MUST be reachable from the main page navigation, mirroring how the image analysis view is reached.
- **FR-021**: The confidence threshold MUST be a property of the model being used, read from registered metadata, not a hard-coded constant in the prediction path.
- **FR-022**: The prediction operation MUST determine which model to use from the operation being invoked, not from an implicit "first available model" rule.
- **FR-023**: The system MUST remain operable when a text message contains words absent from the model's vocabulary, returning a result or a clear error and never crashing.
- **FR-024**: Documentation MUST be updated to describe the new operation: the available models, the API endpoints, and usage examples, per constitution §5.1.
- **FR-025**: System MUST include tests covering the text preprocessing path, the text prediction endpoint, and the model-listing response, per constitution §5.2.
- **FR-026**: System MUST keep the spam model usable by the runtime environment actually deployed. [NEEDS CLARIFICATION: the provided artifact contains a text-preprocessing layer that requires a machine-learning runtime not currently installed in this project; see Resolution Q1]

*Example user-facing messages (illustrative, not exhaustive):*

- Confident spam: `"Detecté: spam (92.3% de certeza)."`
- Confident not spam: `"Detecté: no spam (88.1% de certeza)."`
- Uncertain: `"Detecté: spam (47.0% de certeza). No estoy completamente seguro de esta predicción."`

### Key Entities *(include if feature involves data)*

- **Message**: The text provided by the user. A single free-text field. The system does not persist it. May originate from typing, pasting, or a form field.
- **Spam Verdict**: The outcome of one classification. Attributes: verdict (one of the model's known verdicts), confidence percentage (0.0–100.0, one decimal), uncertainty flag (true when confidence is below the registered threshold), model identifier, and a user-facing message.
- **Model Metadata**: Descriptive information about an available model (identifier, type, input modality, input/output shape, verdict label set, required preprocessing, framework, confidence threshold). Exposed by `GET /api/models` without internal artifact locations.
- **Pre-trained Spam Classifier**: An externally trained text classifier with a fixed verdict set and fixed input expectations, supplied by the user. Not trained, retrained, or modified by this feature. Its text-preprocessing expectations travel with the artifact.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users receive a spam/ham verdict for a valid message within 2 seconds in at least 95% of requests on the local server.
- **SC-002**: 100% of results with confidence below the registered threshold include the uncertainty statement and have the uncertainty flag set to `true`.
- **SC-003**: 0% of results with confidence at or above the registered threshold include the uncertainty statement.
- **SC-004**: 100% of valid message submissions return a verdict and a confidence value without a server error.
- **SC-005**: 100% of invalid submissions (missing, empty, or whitespace-only) return a clear error message without crashing the service.
- **SC-006**: Re-analyzing the same message yields the same verdict and confidence in 100% of cases.
- **SC-007**: The primary text flow (enter a message → submit → see the verdict) completes successfully in a single attempt in 100% of scripted smoke tests.
- **SC-008**: 0% of user-facing error messages expose internal details (file paths, stack traces, library names) across all tested error cases.
- **SC-009**: 100% of registered models appear in the model-listing response, and 0% of listing entries expose internal artifact locations.
- **SC-010**: 0% of regressions in the existing image analysis operation — all currently passing image feature tests continue to pass unchanged after this feature is delivered.
- **SC-011**: A user who has never used the application can find the spam analysis view from the main page and complete a classification without external instructions.
- **SC-012**: Each of the two modalities can be exercised independently, in either order, in the same running process without interfering with the other.

## Assumptions

- The pre-trained spam classifier is a binary text classifier with two verdicts; the verdict-to-label mapping is supplied by the user or documented with the model, and the two verdicts map to "spam" and "not spam" (commonly called *ham*).
- "Confidence" means the classifier's probability for its top verdict, expressed as a percentage rounded to one decimal place.
- The threshold is inclusive on the confident side: values strictly below it are uncertain; it and above are confident.
- The existing image operation defines the quality bar: this feature mirrors its structure (blueprint, view, handler, controller, response shape, uncertainty behaviour, lazy loading, tests).
- Both operations coexist in one process. Model selection is explicit per operation; the existing "first registered model" default is not relied upon.
- The user's message language is Spanish, matching the existing interface; the classifier itself was trained on a fixed corpus whose language is a property of the model, not of the interface.
- Accepted input is plain text of arbitrary length within the configured request-size limit; the application defines no content-length restriction beyond that limit.
- The model artifact is supplied by the user and is copied into the project's model storage; the application does not read models from arbitrary external paths at runtime.
- This is an academic deployment: production-grade scalability, authentication, persistence of analyses, and bulk/batch submission are out of scope.
- No personally identifiable information is required for this feature; users submit arbitrary text of their choosing and the system does not persist it.

## Out of Scope

- Training, fine-tuning, or re-exporting the spam model
- Storing or listing past analyses
- User authentication on the spam operation
- Bulk or batch submission of multiple messages
- Cross-modal inputs (e.g. an image containing text)
- Changing the behaviour, contracts, or response shape of the existing image operation
- Model selection by the end user at runtime (the operation determines its model)

## Dependencies

- The existing blueprint, controller, view, and inference-orchestration structure established by the image feature
- The existing model registry manifest and its validation rules
- The model-listing operation `GET /api/models`
- The project's test suite and fixtures convention (committed samples, no downloads at test time)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| The supplied model artifact cannot be loaded by the project's runtime environment | **High** | Blocking — must be resolved before implementation; see Resolution Q1 |
| Adding a second registered model changes which model the existing image operation resolves | High | Make model resolution explicit per operation; existing image tests must pass unchanged (SC-010) |
| Tokenisation/preprocessing drifts from training time | High | The classifier's preprocessing travels with the artifact; document it in model metadata per §4.2 |
| Two large models increase memory footprint | Medium | Load lazily and only the model the invoked operation needs; never preload both |
| Binary verdicts are mislabelled (spam vs. ham ordering) | Medium | Confirm the verdict-to-label mapping with the model owner before wiring the registry entry |
| Users over-trust a borderline verdict | Medium | Uncertainty statement below the registered threshold (FR-003), consistent with the image feature |
| Users submit text containing personal or sensitive data | Low | Text is not persisted; no analytics on submitted content |