# Data Model: Spam ML Inference

**Date**: 2026-10-10
**Feature**: 003-spam-ml-inference

## Entities

### TextAnalysisRequest

Representa una solicitud de análisis de texto para detección de spam.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| text | str | El mensaje de texto a analizar | Required, non-empty, max 10000 chars |

### SpamPredictionResult

Representa el resultado de un análisis de spam.

| Field | Type | Description |
|-------|------|-------------|
| message | str | Mensaje descriptivo del resultado |
| prediction | str | "spam" o "no spam" |
| confidence | float | Porcentaje de confianza (0-100) |
| uncertain | bool | True si la confianza está cerca del umbral |
| model | str | Nombre del modelo utilizado |

### ModelMetadata (registry entry)

Entrada en `app/models/registry.json` para el modelo de spam.

| Field | Value |
|-------|-------|
| name | spam_classifier |
| type | classification |
| input_modality | text |
| input_shape | [1] |
| output_shape | [1] |
| classes | [{"key": "ham", "label": "no spam"}, {"key": "spam", "label": "spam"}] |
| preprocessing | {"standardize": "lower_and_strip_punctuation", "split": "whitespace", "max_tokens": 5000, "output_sequence_length": 100} |
| framework | keras |
| artifact_path | weights/mi_modelo_spam.keras |
| confidence_threshold | 50 |

## State Transitions

```text
[Text Input] → [Validation] → [TextVectorization] → [Embedding] → [GlobalAveragePooling] → [Dense Layers] → [Sigmoid Output] → [Classification]
```

## Validation Rules

1. **Empty text**: Reject with error "No se recibió ningún texto."
2. **Whitespace-only text**: Reject with error "No se recibió ningún texto."
3. **Text too long**: Reject with error "El texto excede la longitud máxima permitida."
4. **Model loading failure**: Return error "No fue posible cargar el modelo en este momento."
5. **Inference failure**: Return error "No fue posible analizar el texto en este momento."
