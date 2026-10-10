# Contract: POST /spam/predict

**Feature**: 003-spam-ml-inference
**Method**: POST
**Path**: /spam/predict
**Content-Type**: application/x-www-form-urlencoded

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | El mensaje de texto a analizar |

### Example

```http
POST /spam/predict HTTP/1.1
Content-Type: application/x-www-form-urlencoded

text=¡Gana dinero gratis! Click aquí para tu premio
```

## Response

### Success (200 OK)

```json
{
  "message": "Detecté: spam (95.3% de certeza).",
  "prediction": "spam",
  "confidence": 95.3,
  "uncertain": false,
  "model": "spam_classifier"
}
```

### Error (400 Bad Request)

```json
{
  "error": "No se recibió ningún texto."
}
```

### Error (500 Internal Server Error)

```json
{
  "error": "No fue posible analizar el texto en este momento."
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| message | string | Mensaje descriptivo del resultado |
| prediction | string | "spam" o "no spam" |
| confidence | float | Porcentaje de confianza (0-100) |
| uncertain | boolean | True si la confianza está cerca del umbral |
| model | string | Nombre del modelo utilizado |

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Texto vacío o inválido |
| 500 | Error de inferencia o carga del modelo |
