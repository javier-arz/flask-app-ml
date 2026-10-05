# Feature Specification: Image ML Inference & Confidence Messaging

**Feature Branch**: `001-image-ml-inference`

**Created**: 2026-10-05

**Status**: Draft

**Input**: User description: "Implement the pending TODO in `app/controllers/image_controller.py` (load model, preprocess, infer). Return the detected category and confidence; if confidence is below 50%, append a 'not fully sure' note. The model is a pre-trained CIFAR-10 Keras classifier. Expose the prediction through a single endpoint `POST /images/predict` (no duplicate prediction endpoints), and list available models through `GET /api/models`."

## Clarifications

### Session 2026-10-05

- **Q**: How many prediction endpoints should exist?
  **A**: **Exactly one**: `POST /images/predict`. The earlier duplicate routes (`POST /images/analyze` and `POST /api/predict`) were removed to avoid duplicated endpoints/controllers. `GET /api/models` is retained as a distinct operation (listing models), not a prediction endpoint.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive a real prediction (Priority: P1)

A user opens the image analysis page, selects a picture, and submits it; the system analyzes the image with the project's pre-trained classification model and shows the detected category and confidence. The prediction is served by a single endpoint, and API consumers can discover the available model through the model-listing endpoint.

**Why this priority**: This is the core value of the feature and the MVP.

**Independent Test**: Submit a valid image to `POST /images/predict` and confirm it returns the predicted category, confidence, model identifier, and uncertainty flag; `GET /api/models` lists the available model.

**Acceptance Scenarios**:

1. **Given** the analysis page with a valid image selected, **When** the user submits, **Then** the page displays the detected category and its confidence without reloading.
2. **Given** a valid image sent to `POST /images/predict`, **When** it is analyzed, **Then** the response contains the predicted category, the confidence, the model identifier, and the uncertainty flag.
3. **Given** a valid image, **When** it is analyzed, **Then** the detected category is one of the model's known categories.
4. **Given** a request to `GET /api/models`, **When** it is handled, **Then** the response lists the available model(s) with their metadata.
5. **Given** the application, **When** its routes are inspected, **Then** there is exactly one prediction endpoint.

---

### User Story 2 - Be warned when the model is not confident (Priority: P2)

When the model's confidence for its top prediction is below 50%, the response explicitly states that the system is not fully certain about the prediction, so the user does not over-trust an unreliable result.

**Why this priority**: Communicating uncertainty is an industry-standard expectation for ML features and prevents misleading users. It is valuable but secondary to producing a prediction at all.

**Independent Test**: Analyze an image that yields confidence below 50% and confirm the uncertainty message is present and the uncertainty flag is true; analyze one at or above 50% and confirm both are absent/false.

**Acceptance Scenarios**:

1. **Given** a prediction whose confidence is below 50%, **When** the result is returned, **Then** the uncertainty flag is `true` and the message includes an explicit statement that the system is not fully certain.
2. **Given** a prediction whose confidence is 50% or higher, **When** the result is returned, **Then** the uncertainty flag is `false` and the message does not include the uncertainty statement.
3. **Given** a prediction whose confidence is exactly 50%, **When** the result is returned, **Then** it is treated as confident (only values strictly below 50% are uncertain).

---

### User Story 3 - Get clear errors instead of failures (Priority: P3)

When the submitted content is missing, not a real image, corrupt, too large, or the model cannot produce a prediction, the caller receives a clear, human-readable error and the service keeps running.

**Why this priority**: Reliability and safe failure are required for a trustworthy feature, but they do not block the primary happy path.

**Independent Test**: Submit an empty form, a non-image file, a corrupt image, and an oversized image; confirm each returns a clear error and the service remains available.

**Acceptance Scenarios**:

1. **Given** a submission with no file, **When** it is sent, **Then** the system responds with HTTP 400 and a clear error message.
2. **Given** content that is not a decodable image or uses an unsupported format, **When** it is sent, **Then** the system responds with HTTP 400 and a clear error message.
3. **Given** a payload larger than the configured limit, **When** it is sent, **Then** the system responds with HTTP 413 and a clear error message.
4. **Given** the model is unavailable or inference fails, **When** a valid image is sent, **Then** the system responds with HTTP 500 and a clear error message without terminating the service.

---

### Edge Cases

- The file field is present but the filename is empty or the file is zero bytes.
- A non-image file is renamed with an image extension (content does not match the declared type).
- The image is corrupt or truncated and cannot be decoded.
- The image is extremely large (dimensions and/or file size).
- The image format or dimensions do not match what the model expects; the system must still return a result or a clear error, never crash.
- The image does not correspond to any category the model was trained on; a low-confidence result with the uncertainty message is expected.
- The same image is analyzed twice; the predicted category and confidence must be identical (deterministic).
- Two requests arrive at the same time; neither must corrupt the other's result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST analyze an uploaded image using the project's pre-trained image classification model and return a predicted category.
- **FR-002**: System MUST include the predicted category in the response.
- **FR-003**: System MUST include a confidence value for the prediction, expressed as a percentage from 0.0 to 100.0, rounded to one decimal place.
- **FR-004**: WHEN the confidence is strictly below 50%, the user-facing message MUST include an explicit statement that the system is not fully certain about the prediction, and the uncertainty flag MUST be `true`.
- **FR-005**: WHEN the confidence is 50% or higher, the user-facing message MUST NOT include the uncertainty statement, and the uncertainty flag MUST be `false`.
- **FR-006**: The prediction endpoint `POST /images/predict` MUST preserve the request contract (a single image file field) and response contract (a user-facing message field already consumed by the current page) so the existing interface keeps working without changes.
- **FR-007**: System MUST reject a request with no file with HTTP 400 and a clear error message.
- **FR-008**: System MUST reject content that is not a decodable image, or that uses an unsupported format, with HTTP 400 and a clear error message.
- **FR-009**: System MUST handle model load or inference failures without terminating the service, returning HTTP 500 and a clear error message.
- **FR-010**: Predictions MUST be restricted to the model's known category set.
- **FR-011**: System MUST serve predictions without re-reading the model artifact on every request (the loaded model is reused across requests).
- **FR-012**: The response MUST remain machine-readable JSON for both success and error outcomes.
- **FR-013**: System MUST NOT expose internal implementation details (file paths, stack traces, library names) in any user-facing error message.
- **FR-014**: The success response MUST expose the uncertainty flag and the user-facing message, in addition to the predicted category (FR-002) and confidence (FR-003).
- **FR-015**: System MUST expose **exactly one** prediction endpoint, `POST /images/predict`.
- **FR-016**: System MUST expose `GET /api/models`, listing the available model(s) with their metadata.
- **FR-017**: System MUST NOT expose duplicate prediction endpoints; every prediction request MUST be served by the same single implementation.
- **FR-018**: System MUST reject a payload larger than the configured upload limit with HTTP 413 and a clear error message.

*Example user-facing messages (illustrative, not exhaustive):*

- Confident: `"Detecté: gato (87.0% de certeza)."`
- Uncertain: `"Detecté: gato (32.4% de certeza). No estoy completamente seguro de esta predicción."`

### Key Entities *(include if feature involves data)*

- **Uploaded Image**: The single image file provided by the user. Accepted formats are JPG, PNG, and WEBP. The system does not persist the image.
- **Prediction Result**: The outcome of one analysis. Attributes: predicted category (one of the model's known categories), confidence percentage (0.0–100.0, one decimal), uncertainty flag (true when confidence < 50%), and a user-facing message.
- **Model Metadata**: Descriptive information about an available model (identifier, type, input modality, input/output shape, category set, framework). Exposed by `GET /api/models`.
- **Pre-trained Model**: An externally trained image classifier with a fixed set of categories and fixed input expectations. It is provided as a model artifact and is not retrained by this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users receive a prediction for a valid image within 2 seconds in at least 95% of requests on the local server.
- **SC-002**: 100% of results with confidence below 50% include the uncertainty message and have the uncertainty flag set to `true`.
- **SC-003**: 0% of results with confidence at or above 50% include the uncertainty message.
- **SC-004**: 100% of valid image submissions return a category and a confidence value without a server error.
- **SC-005**: 100% of invalid submissions (missing, non-image, corrupt, or oversized) return a clear error message without crashing the service.
- **SC-006**: Re-analyzing the same image yields the same predicted category and confidence in 100% of cases.
- **SC-007**: The primary flow (select an image → submit → see the result) completes successfully in a single attempt in 100% of scripted smoke tests.
- **SC-008**: 0% of user-facing error messages expose internal details (file paths, stack traces, library names) across all tested error cases.

## Assumptions

- The pre-trained model is an image classifier with 10 known categories (CIFAR-10: airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck).
- The model artifact is supplied by the user and stored within the project; the existing upload page is reused.
- "Confidence" means the model's probability for its top predicted category, expressed as a percentage rounded to one decimal place.
- The 50% threshold is inclusive on the confident side: values strictly below 50% are uncertain; 50% and above are confident.
- Category names and messages are presented in Spanish to match the existing interface language.
- Only single-image analysis is in scope; batch upload and analysis history are out of scope.
- This is an academic deployment; production-grade scalability, authentication, and persistence of results are out of scope.
- Accepted formats remain JPG, PNG, and WEBP, consistent with the current interface.
- Model listing (`GET /api/models`) is in scope; it is not a prediction endpoint.
