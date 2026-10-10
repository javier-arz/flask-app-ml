# Feature Specification: Spam ML Inference

**Feature Branch**: `003-spam-ml-inference`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "Basado en la implementación de la operación de predicción de imágenes '/images/predict' (con su front, sus handlers, controlers y modelo), quiero que me ayudes a implementar una operación de detección de spam siguiendo la misma filosofía (puedes elegir el nombre y path de la operación, así como nombre de controllers y demás; como ya habrás podido inferir, se espera que reciba un texto y detecte si corresponde o no a un mensaje de spam; el modelo preentrenado que debes usar es: F:\estudio\Especialización IA\Machine Learning Avanzado\mi_modelo_spam.keras"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Análisis de spam desde la interfaz web (Priority: P1)

Un usuario ingresa a la aplicación web, navega a la sección de detección de spam, escribe o pega un mensaje de texto en un formulario, y envía el texto para análisis. El sistema procesa el mensaje con el modelo de ML y muestra si el mensaje es spam o no, junto con el nivel de confianza de la predicción.

**Why this priority**: Es el flujo principal de la funcionalidad — sin él no existe valor para el usuario. Todo lo demás (manejo de errores, casos edge) depende de que este flujo funcione.

**Independent Test**: Se puede probar completamente enviando un texto conocido como spam (ej: "¡Gana dinero gratis! Click aquí") a la interfaz web y verificando que el resultado mostrado indica "spam" con una confianza razonable.

**Acceptance Scenarios**:

1. **Given** el usuario está en la página de detección de spam, **When** envía un texto claramente spam, **Then** el sistema muestra un resultado indicando que es spam con un porcentaje de confianza
2. **Given** el usuario está en la página de detección de spam, **When** envía un texto claramente legítimo, **Then** el sistema muestra un resultado indicando que no es spam con un porcentaje de confianza
3. **Given** el usuario está en la página de detección de spam, **When** envía el texto para análisis, **Then** el sistema muestra un indicador de carga durante el procesamiento

---

### User Story 2 - Consulta de modelos disponibles vía API (Priority: P2)

Un usuario o desarrollador consulta el endpoint de listado de modelos para ver qué modelos están disponibles en el sistema. El nuevo modelo de spam aparece en la lista junto con el modelo de imágenes existente.

**Why this priority**: Es importante para la transparencia del sistema y para que los usuarios conozcan las capacidades disponibles, pero no es crítico para el flujo principal de predicción.

**Independent Test**: Se puede probar haciendo una petición al endpoint de listado de modelos y verificando que el modelo de spam aparece con su metadata correcta (nombre, tipo, clases, etc.).

**Acceptance Scenarios**:

1. **Given** el usuario consulta el listado de modelos, **When** el sistema responde, **Then** el modelo de detección de spam aparece en la lista con su metadata (nombre, tipo: classification, classes: spam/ham, etc.)

---

### User Story 3 - Manejo de errores en el análisis (Priority: P2)

Un usuario envía un texto que no puede ser procesado correctamente (texto vacío, texto demasiado largo, caracteres especiales que rompen el preprocesamiento, etc.) y recibe un mensaje de error claro en lugar de una respuesta incorrecta o un fallo del sistema.

**Why this priority**: Es esencial para la experiencia de usuario y la robustez del sistema, pero no bloquea el flujo principal.

**Independent Test**: Se puede probar enviando un texto vacío o con caracteres inusuales y verificando que el sistema devuelve un mensaje de error comprensible sin romper la página.

**Acceptance Scenarios**:

1. **Given** el usuario envía un texto vacío, **When** el sistema procesa la petición, **Then** muestra un mensaje de error indicando que no se recibió texto válido
2. **Given** el usuario envía un texto excesivamente largo, **When** el sistema procesa la petición, **Then** muestra un mensaje de error indicando la limitación

---

### Edge Cases

- ¿Qué ocurre cuando el texto está vacío o solo contiene espacios?
- ¿Cómo maneja el sistema texto en idiomas diferentes al de entrenamiento del modelo?
- ¿Qué sucede cuando el texto contiene emojis, URLs o caracteres especiales?
- ¿Cómo maneja el sistema textos extremadamente largos (potencial problema de memoria o timeout)?
- ¿Qué ocurre cuando el modelo retorna una confianza muy baja (zona gris entre spam y no spam)?
- ¿Cómo maneja el sistema texto con inyección de código o patrones maliciosos?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST proporcionar una interfaz web donde el usuario pueda ingresar un mensaje de texto para análisis de spam
- **FR-002**: El sistema MUST enviar el texto ingresado al modelo de ML y retornar la clasificación (spam o no spam) junto con el nivel de confianza
- **FR-003**: El sistema MUST mostrar el resultado del análisis de forma clara en la interfaz web, indicando si el mensaje es spam o no
- **FR-004**: El sistema MUST mostrar un indicador de carga mientras se procesa la petición
- **FR-005**: El sistema MUST mostrar mensajes de error claros cuando el texto no puede ser procesado (vacío, inválido, etc.)
- **FR-006**: El sistema MUST registrar el modelo de detección de spam en el registro de modelos para que aparezca en el listado de modelos disponibles
- **FR-007**: El sistema MUST seguir la misma arquitectura blueprint que la funcionalidad de imágenes (routes → controllers → ML service)
- **FR-008**: El sistema MUST preprocesar el texto de forma consistente con el preprocesamiento usado durante el entrenamiento del modelo
- **FR-009**: El sistema MUST manejar la carga perezosa del modelo (lazy loading) para no consumir memoria hasta que se requiera

### Key Entities

- **Mensaje de texto**: El input del usuario — una cadena de texto que representa el mensaje a analizar. Puede ser de longitud variable, incluir caracteres especiales, URLs, etc.
- **Resultado de análisis**: La salida del sistema — incluye la clasificación (spam/no spam), el nivel de confianza (porcentaje), y el nombre del modelo utilizado
- **Modelo de ML**: El artefacto de ML preentrenado (`mi_modelo_spam.keras`) que realiza la clasificación. Se carga perezosamente y se cachea para su reutilización

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede enviar un texto para análisis de spam y obtener un resultado en menos de 5 segundos
- **SC-002**: El sistema clasifica correctamente al menos el 90% de los mensajes de spam conocidos
- **SC-003**: El sistema clasifica correctamente al menos el 90% de los mensajes legítimos conocidos
- **SC-004**: El modelo de spam aparece listado en el endpoint de modelos disponibles junto con su metadata correcta
- **SC-005**: Un usuario puede completar el análisis de un mensaje de spam (desde ingresar el texto hasta ver el resultado) en menos de 3 pasos

## Assumptions

- El modelo `mi_modelo_spam.keras` es un modelo de clasificación binaria (spam vs. no spam, típicamente ham) que espera texto como input
- El modelo fue entrenado con un preprocesamiento específico (tokenización, padding, etc.) que debe replicarse durante la inferencia — esto requiere investigación adicional o documentación del modelo
- El modelo está guardado en la ubicación especificada por el usuario y es accesible desde el entorno de ejecución
- La aplicación web tiene un estilo visual consistente con la funcionalidad de imágenes (Tailwind CSS, spinner, manejo de errores en español)
- No se requiere autenticación para usar la funcionalidad de detección de spam (consistente con la funcionalidad de imágenes)
- El modelo retorna probabilidades de clase de las que se puede extraer la clase predicha y la confianza

## Constitution Compliance

Esta especificación cumple con los principios de la constitución del proyecto (v1.1.0):

- **§3.1 Blueprint-Based Modularity**: Se creará un blueprint dedicado para la detección de spam, siguiendo el patrón de `app/routes/images/`
- **§3.2 Lazy Model Loading**: El modelo de spam se cargará perezosamente, usando el mismo patrón que el predictor de imágenes
- **§3.3 Preprocessing Parity**: El preprocesamiento del texto debe coincidir con el usado durante el entrenamiento (investigación pendiente sobre el pipeline exacto)
- **§3.4 RESTful Inference API**: Se expondrá un endpoint `POST /spam/predict` (o similar) para la predicción, manteniendo `GET /api/models` para el listado
- **§4.1 Storage Convention**: El modelo se almacenará en `app/models/weights/` y se registrará en `registry.json`
- **§4.2 Model Metadata**: El modelo de spam debe incluir nombre, tipo, input_modality (text), shapes, clases, y pipeline de preprocesamiento
