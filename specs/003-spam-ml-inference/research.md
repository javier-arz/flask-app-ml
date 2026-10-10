# Research: Spam ML Inference

**Date**: 2026-10-10
**Feature**: 003-spam-ml-inference

## R1: Model Architecture

**Decision**: El modelo `mi_modelo_spam.keras` es un clasificador binario secuencial con las siguientes capas:

| # | Layer | Type | Output Shape | Params |
|---|-------|------|--------------|--------|
| 0 | text_vectorization | TextVectorization | (None, 100) | 0 |
| 1 | embedding | Embedding | (None, 100, 16) | 80,000 |
| 2 | global_average_pooling1d | GlobalAveragePooling1D | (None, 16) | 0 |
| 3 | dense | Dense | (None, 16) | 272 |
| 4 | dropout | Dropout | (None, 16) | 0 |
| 5 | dense_1 | Dense | (None, 8) | 136 |
| 6 | dense_2 | Dense | (None, 1) | 9 |

**Total params**: 241,253 (942.40 KB)

**Rationale**: El modelo es un clasificador binario que retorna una probabilidad entre 0 y 1. La capa de salida (dense_2) tiene 1 neurona con activación sigmoid implícita.

## R2: TextVectorization Configuration

**Decision**: La capa `TextVectorization` está integrada en el modelo con la siguiente configuración:

| Parameter | Value |
|-----------|-------|
| max_tokens | 5000 |
| standardize | lower_and_strip_punctuation |
| split | whitespace |
| ngrams | None |
| output_mode | int |
| output_sequence_length | 100 |
| vocabulary_size | 3138 |

**Rationale**: El preprocesamiento está completamente integrado en el modelo. No se requiere preprocesamiento externo — el texto crudo se puede alimentar directamente al modelo. La capa maneja: conversión a minúsculas, eliminación de puntuación, tokenización por espacios, y padding/truncamiento a 100 tokens.

## R3: Backend Requirement

**Decision**: El modelo requiere `KERAS_BACKEND=tensorflow` debido a la capa `TextVectorization`.

**Rationale**: La capa `TextVectorization` de Keras 3 solo funciona con TensorFlow como backend. El proyecto usa `torch` por defecto para el modelo de imágenes, pero el modelo de spam necesita `tensorflow`. Se debe usar un selector de backend dinámico o un predictor separado.

**Alternatives considered**:
1. Usar `KERAS_BACKEND=tensorflow` globalmente — rompería el modelo de imágenes que usa torch
2. Crear un predictor separado para spam con su propio backend — **elegido**, mantiene aislamiento
3. Convertir el modelo para remover TextVectorization — demasiado arriesgado, podría afectar rendimiento

## R4: Input/Output Contract

**Decision**: 
- **Input**: Texto crudo (string) — el modelo maneja todo el preprocesamiento internamente
- **Output**: Probabilidad de spam (float entre 0 y 1)

**Rationale**: La capa `TextVectorization` convierte el texto a una secuencia de enteros de longitud 100, que luego pasa por el embedding y las capas densas. El output es un único valor que representa la probabilidad de que el texto sea spam.

## R5: Class Mapping

**Decision**: 
- Índice 0 → "no spam" (ham)
- Índice 1 → "spam"

**Rationale**: El modelo tiene una sola neurona de salida (clasificación binaria con sigmoid). Un valor cercano a 0 indica "no spam" y cercano a 1 indica "spam". El umbral de decisión es 0.5 por defecto.

## R6: Vocabulary Language

**Decision**: El vocabulario del modelo está en español (3138 palabras).

**Rationale**: Las palabras más frecuentes en el vocabulario son artículos y preposiciones en español: 'de', 'tu', 'el', 'en', 'la', 'para', 'que', 'a', 'te', 'por', 'un', 'está', 'las', 'no', 'me', 'aquí', 'y', 'del', 'con', 'ya', 'al', 'solo', 'hoy', 'es', 'este', 'se', 'si', 'su'.

## R7: Model Storage

**Decision**: Copiar el modelo a `app/models/weights/mi_modelo_spam.keras` y registrarlo en `registry.json`.

**Rationale**: Seguir la convención de almacenamiento del proyecto (constitución §4.1). El modelo se copia desde la ubicación original del usuario al directorio de weights del proyecto.

## R8: Confidence Threshold

**Decision**: Usar 50% como umbral de confianza (consistente con el modelo de imágenes).

**Rationale**: Para un clasificador binario con sigmoid, 0.5 es el umbral natural. Si la probabilidad de spam es >= 50%, se clasifica como spam; de lo contrario, como no spam. Si la confianza está cerca del 50% (zona gris), se puede marcar como "incierto".
