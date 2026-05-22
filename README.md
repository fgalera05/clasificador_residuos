# ♻️ Clasificador de Residuos - Sistema Experto

Este proyecto es un Clasificador de Residuos basado en un motor de reglas desarrollado para la materia **Análisis de Datos II**.

El repositorio cuenta con dos versiones de la aplicación para demostrar la evolución desde un prototipo inicial con limitaciones lógicas hasta un sistema experto robusto que realiza inferencia real sobre estados físicos.

---

## 🔬 ¿Por qué la Versión Base (app_simple_lookup.py) NO es un Sistema Experto real y la Versión 2 (app_sistema_experto.py) SÍ lo es?

Para que un software sea considerado un **Sistema Experto (SE)** genuino, no basta con utilizar una librería de reglas (como `experta`); debe cumplir con la arquitectura y comportamiento de un sistema basado en conocimiento.

| Característica | Prototipo Base (`app_simple_lookup.py`) | Sistema Experto Real (`app_sistema_experto.py`) | ¿Por qué es crítico para un SE? |
| :--- | :--- | :--- | :--- |
| **Inferencia Lógica (Forward Chaining)** | ❌ **No realiza inferencia.** Funciona como una simple base de datos (Lookup Table). Si el residuo es "papel", devuelve "papel" directamente de un mapeo estático. |  **Inferencia real.** Encadena hechos iniciales (`Residuo`), evalúa condiciones lógicas intermedias (`Clasificado`) y concluye una `Clasificacion` final. | Un SE debe deducir nuevos conocimientos a partir de reglas encadenadas, no solo actuar como un diccionario. |
| **Cerebro en el Motor vs. Código Tradicional** | ❌ **Decisión fuera del motor.** El control de ambigüedades y compatibilidad de materiales se resuelve en Python procedimental (`if/else` externos). |  **Razonamiento nativo.** Toda la lógica declarativa y resolución de condiciones críticas se delega a las reglas del motor. | En un SE, el control de la inferencia debe ser declarativo y residir dentro del motor, no en el código de control del frontend. |
| **Variables de Estado del Entorno** | ❌ **Ignora el contexto.** Asume condiciones ideales para todo residuo. |  **Hechos estructurados.** Evalúa variables físicas reales (`limpio`, `seco`, `roto`) para alterar la clasificación. | Los problemas del mundo real dependen de variables de estado. Un papel mojado o un vidrio roto cambian su lógica de reciclabilidad. |
| **Módulo de Explicación (Explanation Facility)** | ❌ **Ausente.** Muestra instrucciones fijas sin justificar la conclusión. |  **Nativo y dinámico.** Explica detalladamente al usuario la justificación lógica (el *"¿Cómo?"* y *"¿Por qué?"*) de la clasificación final. | Es un requisito clásico que un SE sea transparente y justifique sus deducciones lógicas ante el usuario humano. |

---

## 🚀 Cómo Ejecutar el Proyecto

Asegurate de tener instaladas las dependencias indicadas en [requirements.txt](./requirements.txt):
```bash
pip install -r requirements.txt
```

### 1. Ejecutar Versión Base (Prototipo Inicial)
Para correr la aplicación original que sirve como línea base y punto de partida de la auditoría:
```bash
streamlit run app_simple_lookup.py
```

### 2. Ejecutar Versión 2 (Inferencia Real y Variables de Estado)
Para correr la aplicación mejorada que resuelve las limitaciones lógicas y de negocio del sistema experto:
```bash
streamlit run app_sistema_experto.py
```

---

## 🛠️ Tecnologías Utilizadas

* **Motor de Inferencia (`experta`):**
  * El core lógico del sistema experto está basado en la biblioteca **`experta`** (una implementación de sistemas expertos en Python inspirada en el clásico lenguaje CLIPS).
  * Utiliza el **Algoritmo Rete** para emparejamiento rápido de patrones de reglas.
  * Implementa **Encadenamiento hacia adelante (Forward Chaining)** declarativo por medio de Hechos (`Fact`, `Residuo`, `Clasificado`, `Clasificacion`) y Reglas (`Rule`), permitiendo que el motor infiera dinámicamente nuevas categorías de residuos de acuerdo a sus propiedades físicas (si está limpio, seco, roto).

* **Módulo de Visión Computacional (Clasificación por Imagen):**
  * La aplicación permite al usuario cargar imágenes del residuo para su análisis en dos etapas: primero el modelo de visión describe el residuo (material/objeto) y luego el sistema experto determina su reciclabilidad. El módulo [src/vision.py](./src/vision.py) soporta dos tecnologías:
    * **Gemini (Nube):** Modelo `gemini-2.5-flash` mediante la API oficial de Google AI Studio, ofreciendo respuestas rápidas y precisas sin consumir hardware local.
    * **Hugging Face (Local con PyTorch):** Modelo VLM local `Qwen2-VL-2B-Instruct` cargado con la librería `transformers` y procesado con tensores de PyTorch (`torch`). Está optimizado para ejecutarse en CPU, GPU (NVIDIA CUDA), o aceleradores MPS (Metal Performance Shaders en chips Apple Silicon de macOS).

---

## 📂 Arquitectura y Archivos Principales

* [app_simple_lookup.py](./app_simple_lookup.py): Interfaz inicial en Streamlit. Realiza clasificación directa sin evaluar estados físicos variables del residuo.
* [app_sistema_experto.py](./app_sistema_experto.py): Interfaz mejorada en Streamlit. Incorpora la selección de variables de estado físico (limpio, seco, roto) en tiempo real con sincronización entre pestañas y muestra la justificación del motor.
* [src/motor.py](./src/motor.py): Contiene la lógica del motor de inferencia (`experta`). Define los hechos (`Residuo`, `Clasificado`, `Clasificacion`), la base de reglas lógicas para reclasificación por estado, y las funciones de detección.
* [src/data.py](./src/data.py): Módulo encargado de la carga de base de conocimientos desde CSVs.
* [src/ui.py](./src/ui.py): Funciones auxiliares para renderizar las tarjetas y el diseño visual.
* [src/style.css](./src/style.css): Hoja de estilos personalizada para dar una estética premium.
* [data/](./data): Carpeta con los archivos de conocimiento (`reglas.csv`, `keywords.csv`, `ambiguos.csv`).

---

## 🧠 Auditoría y Comparativa de Versiones

A continuación se detalla cómo la **Versión 2** (`app_sistema_experto.py`) soluciona los problemas detectados en la auditoría del diseño inicial (`app_simple_lookup.py` / [src/motor.py](./src/motor.py) / [data/reglas.csv](./data/reglas.csv)).

### 1. El motor de reglas es redundante vs. Inferencia Real
* **En `app_simple_lookup.py`:**
  La función `crear_metodo_regla` toma los datos estáticos de [data/reglas.csv](./data/reglas.csv) y genera reglas dinámicas que solo copian esa información al hecho final `Clasificacion` sin deducir información nueva. Funciona únicamente como una tabla de búsqueda (lookup table).
* **En `app_sistema_experto.py` (Resuelto):**
  Se rediseñó el flujo en [src/motor.py](./src/motor.py). El motor ahora realiza un **encadenamiento hacia adelante (Forward Chaining)** real introduciendo el hecho intermedio `Clasificado`. Las reglas lógicas de estado evalúan el hecho inicial `Residuo` y pueden derivar en un hecho `Clasificado` diferente (ej. reclasificar papel a papel no reciclable). La regla de clasificación final reacciona al hecho `Clasificado` resultante.

### 2. El "cerebro" de decisión está fuera vs. Razonamiento Nativo
* **En `app_simple_lookup.py`:**
  El control de ambigüedades e identificación inicial se realiza mediante código Python estructurado convencional, restándole protagonismo al motor de inferencia declarativo.
* **En `app_sistema_experto.py` (Resuelto):**
  Aunque la detección por keywords asiste al inicio, toda la lógica de validación de compatibilidad de materiales, el cruce con variables físicas del residuo, y la reevaluación de categorías críticas se ejecutan de manera declarativa dentro del motor de inferencia usando las reglas de `experta`.

### 3. Falta de Hechos Estructurados vs. Variables de Estado Físico
* **En `app_simple_lookup.py`:**
  El motor solo recibe un hecho plano `Residuo(tipo=tipo)`, asumiendo que el residuo siempre está en condiciones ideales.
* **En `app_sistema_experto.py` (Resuelto):**
  Se incorporaron variables booleanas de estado físico: `limpio`, `seco` y `roto`. El sistema experto ahora razona sobre estas propiedades:
  * Papel o cartón que esté sucio o húmedo $\rightarrow$ se reclasifica a **Basura Común (Papel No Reciclable)**.
  * Vidrio que esté roto $\rightarrow$ se reclasifica a **Basura Común (Vidrio No Reciclable)** por razones de seguridad para los operarios.
  * Plásticos, tetrabrik o metales sucios/húmedos $\rightarrow$ se reclasifican como **No Apto para reciclaje** hasta ser saneados.

### 4. Ausencia de Explicaciones vs. Módulo de Explicación (Explanation Facility)
* **En `app_simple_lookup.py`:**
  La interfaz solo muestra instrucciones estáticas sin explicar la secuencia de razonamiento.
* **En `app_sistema_experto.py` (Resuelto):**
  Se implementó un módulo de explicación nativo en las reglas de [src/motor.py](./src/motor.py). Cada regla disparada añade una justificación textual detallada explicativa (`_explicacion`) que describe el *¿Cómo?* y *¿Por qué?* de la decisión, la cual es presentada de forma clara en la tarjeta de resultado en el frontend de Streamlit.