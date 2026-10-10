# Quickstart: Spam ML Inference

**Feature**: 003-spam-ml-inference
**Date**: 2026-10-10

## Prerequisites

- Python 3.11+
- Dependencias instaladas: `pip install -r requirements.txt`
- TensorFlow instalado: `pip install tensorflow`
- Modelo copiado a `app/models/weights/mi_modelo_spam.keras`
- Registro actualizado en `app/models/registry.json`

## Setup

1. Copiar el modelo de spam al directorio de weights:
   ```powershell
   Copy-Item "F:\estudio\Especialización IA\Machine Learning Avanzado\mi_modelo_spam.keras" "app\models\weights\mi_modelo_spam.keras"
   ```

2. Verificar que el registro de modelos incluye el modelo de spam:
   ```powershell
   venv\Scripts\python.exe -c "from app.ml.model_registry import load_registry; print([m.name for m in load_registry()])"
   ```
   Expected output: `['cifar10', 'spam_classifier']`

## Validation Scenarios

### Scenario 1: Análisis de spam desde la interfaz web

1. Iniciar la aplicación:
   ```powershell
   venv\Scripts\python.exe run.py
   ```

2. Abrir en el navegador: `http://localhost:5000/spam`

3. Ingresar un texto claramente spam: `¡Gana dinero gratis! Click aquí para tu premio`

4. Hacer clic en "Analizar"

5. **Expected**: El resultado muestra "spam" con un porcentaje de confianza alto (>80%)

### Scenario 2: Análisis de texto legítimo

1. En la misma página, ingresar un texto legítimo: `Hola, ¿cómo estás? Quisiera agradecerte por tu ayuda.`

2. Hacer clic en "Analizar"

3. **Expected**: El resultado muestra "no spam" con un porcentaje de confianza alto (>80%)

### Scenario 3: Texto vacío

1. Dejar el campo de texto vacío

2. Hacer clic en "Analizar"

3. **Expected**: Se muestra un mensaje de error indicando que no se recibió texto

### Scenario 4: Consulta de modelos disponibles

1. Ejecutar:
   ```powershell
   venv\Scripts\python.exe -c "from app.ml.inference_service import list_models; import json; print(json.dumps(list_models(), indent=2))"
   ```

2. **Expected**: El modelo `spam_classifier` aparece en la lista con su metadata

### Scenario 5: API directa (curl)

```powershell
curl -X POST http://localhost:5000/spam/predict -d "text=¡Gana dinero gratis!"
```

**Expected**: JSON response con `prediction: "spam"` y `confidence` > 80%

## Unit Tests

```powershell
venv\Scripts\python.exe -m pytest tests/unit/test_spam_predictor.py -v
```

## Integration Tests

```powershell
venv\Scripts\python.exe -m pytest tests/integration/test_spam_predict.py -v
```

## Expected Outcomes

- El modelo de spam se carga correctamente y aparece en el listado de modelos
- Los textos claramente spam se clasifican como "spam" con alta confianza
- Los textos claramente legítimos se clasifican como "no spam" con alta confianza
- Los textos vacíos o inválidos producen mensajes de error claros
- La interfaz web muestra el resultado del análisis de forma clara
