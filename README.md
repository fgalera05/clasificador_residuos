#  Clasificador de Residuos para Reciclaje
### Sistema Experto basado en reglas

---

##  Información del trabajo

| Campo | Detalle |
|---|---|
| **Materia** | Análisis de Datos II |
| **Trabajo** | Trabajo Práctico — Sistema Experto |
| **Universidad** | Universidad de la Ciudad de Buenos Aires |
| **Profesor** | Agustín Asuaje |
| **Cuatrimestre** | 1º Cuatrimestre 2026 |
| **Fecha de presentación** | 4 de junio de 2026 |

---

##  Grupo A

| Integrantes |
|---|
| Luciano Asís |
| Gustavo Barrajón |
| Fernando Galera |
| Gabriel García |
| Facundo Martinez |
| Andrea Moreno |

---

##  Objetivo

Construir un **Sistema Experto basado en reglas** capaz de clasificar residuos domésticos e indicar cómo descartarlos correctamente, contribuyendo a una gestión más responsable de los residuos en Argentina.

---

##  Descripción del sistema

El sistema recibe una descripción de un residuo (por texto o imagen) y devuelve:

- **Categoría** del residuo (reciclable, orgánico, especial, peligroso, basura común)
- **Instrucciones** paso a paso para descartarlo correctamente
- **Errores comunes** a evitar con ese material
- **Impacto ambiental** si se recicla o descarta correctamente
- **Enlace directo al mapa** de Puntos Verdes filtrado por el tipo de destino del residuo clasificado
- **Mapa interactivo** con Puntos Verdes, Contenedores y Centros RSU cercanos (CABA), filtrables por tipo y accesibles desde la URL

Las reglas y categorías están alineadas con la normativa vigente: **Ley CABA 1854/2005**, **Decreto GCBA 639/07**, **Ley CABA 5991/2018**, **Ley Nacional 25.916**, **Código IRAM 13700** (plásticos) y los Convenios de **Basilea** y **Estocolmo** (residuos peligrosos y COPs).

---
##  Cómo Ejecutar el Proyecto

Crear un entorno virtual e instalar dependencias:
```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

###  Ejecutar la app
```bash
streamlit run app_sistema_experto.py
```
La app abre en `http://localhost:8501`. Para las siguientes ejecuciones solo es necesario activar el entorno virtual y correr el comando anterior.

### App Streamlit (online)

<img src="data/qr-code.png" alt="Qr de la web" width="300">

[Ver la app desplegada](https://clasificador--residuos.streamlit.app/) 

---

##  API Key de Gemini (clasificación por imagen)

La clasificación por imagen usa **Google Gemini 2.5 Flash**, cuya API es gratuita:

1. Ir a [aistudio.google.com](https://aistudio.google.com)
2. Iniciar sesión con cuenta de Google
3. Click en **Get API Key** → **Create API Key**
4. Ingresarla en el panel lateral de la app Streamlit

---
##  Tecnologías Utilizadas

* **Motor de Inferencia (`experta`):**
  * El core lógico del sistema experto está basado en la biblioteca **`experta`** (una implementación de sistemas expertos en Python inspirada en el clásico lenguaje CLIPS).
  * Utiliza el **Algoritmo Rete** para emparejamiento rápido de patrones de reglas.
  * Implementa **Encadenamiento hacia adelante (Forward Chaining)** declarativo por medio de Hechos (`Fact`, `Residuo`, `Clasificado`, `Clasificacion`) y Reglas (`Rule`), permitiendo que el motor infiera dinámicamente nuevas categorías de residuos de acuerdo a sus propiedades físicas (si está limpio, seco, roto).

* **Módulo de Visión Computacional (Clasificación por Imagen):**
  * La aplicación permite al usuario cargar imágenes del residuo para su análisis en dos etapas: primero el modelo de visión describe el residuo (material/objeto) y luego el sistema experto determina su reciclabilidad. El módulo [src/vision.py](./src/vision.py) soporta la tecnología de:
    * **Gemini (Nube):** Modelo `gemini-2.5-flash` mediante la API oficial de Google AI Studio, ofreciendo respuestas rápidas y precisas sin consumir hardware local.

---

##  Archivos Principales

* [app_sistema_experto.py](./app_sistema_experto.py): Interfaz en Streamlit. Realiza clasificación e incorpora la selección de variables de estado físico (limpio, seco, roto) en tiempo real con sincronización entre pestañas y muestra la justificación del motor.
* [src/motor.py](./src/motor.py): Contiene la lógica del motor de inferencia (`experta`). Define los hechos (`Residuo`, `Clasificado`, `Clasificacion`), la base de reglas lógicas para reclasificación por estado, y las funciones de detección.
* [src/data.py](./src/data.py): Módulo encargado de la carga de base de conocimientos desde CSVs.
* [src/ui.py](./src/ui.py): Funciones auxiliares para renderizar las tarjetas y el diseño visual.
* [src/style.css](./src/style.css): Hoja de estilos personalizada para dar una estética premium.
* [data/](./data): Carpeta con los archivos de conocimiento (`reglas.csv`, `keywords.csv`, `ambiguos.csv`, `puntos_verdes.csv`).
* [Reciclaje/](./Reciclaje): Carpeta que contiene imágenes de prueba organizadas por tipo de residuo y contenedor para validar el funcionamiento del módulo de visión computacional.


---

##  Estructura de Archivos del Proyecto

El repositorio está estructurado en módulos para separar la interfaz de usuario (Frontend), la carga de datos (Data), la lógica de negocio/reglas (Motor) y el procesamiento de IA y Geoposicionamiento:

```
📁 clasificador-residuos/
│
├── app_sistema_experto.py     # Aplicación base (Sistema Experto con Inferencia)
├── requirements.txt           # Dependencias para Streamlit Cloud
├── README.md
│
├── data/                      # Base de conocimientos en CSV
│   │
│   ├── puntos_verdes.csv                       
│   ├── reglas.csv
│   ├── keywords.csv
│   └── ambiguos.csv
│
└── src/                       # Módulos auxiliares del sistema
    │
    ├── __init__.py
    ├── compat.py              # Parche de compatibilidad Python 3.10+
    ├── data.py                # Carga y caché de datos CSV/API
    ├── motor.py               # Motor de inferencia y lógica NLP de plurales
    ├── vision.py              # Reconocimiento visual (Gemini y Qwen VLM local)
    ├── geo.py                 # Distancias Haversine para Puntos Verdes
    ├── ui.py                  # Inyección de estilos y renderizado de tarjetas
    └── style.css              # Hoja de estilos premium
```

---

## 1. Módulos de Soporte (`src/`)

### A. Parche de Compatibilidad: src/compat.py
**Propósito:** Solucionar la incompatibilidad de la librería `experta` con versiones modernas de Python (3.10 o superiores).
* **Problema:** `experta` fue desarrollada hace años y utiliza referencias obsoletas a estructuras del módulo `collections` (como `collections.Mapping`). En Python 3.10+, estas estructuras fueron removidas y movidas permanentemente a `collections.abc`.
* **Solución:** Modifica dinámicamente las referencias en tiempo de ejecución antes de importar `experta`:
```python
import collections
import collections.abc

if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Callable'):
    collections.Callable = collections.abc.Callable
```

---

### B. Carga de Datos: src/data.py
**Propósito:** Cargar y procesar la base de conocimientos desde los archivos CSV y consumir los datos geográficos de los Puntos Verdes.
* **Optimización con `@st.cache_data`:** Utiliza la caché integrada de Streamlit para evitar abrir y leer archivos CSV del disco en cada interacción o actualización del navegador (rerun).
* **`cargar_sistema()`:** Lee tres archivos fundamentales:
  1. `keywords.csv`: Mapea keywords del lenguaje natural a tipos de residuos.
  2. `reglas.csv`: Define las propiedades de destino (contenedor, instrucciones, impacto, urgencia) por tipo de residuo.
  3. `ambiguos.csv`: Almacena términos conflictivos y las preguntas guiadas para resolverlos. Cubre materiales genéricos según IRAM 13700: **plástico** (PET / film / rígido / PVC / EPS), **vidrio** (reciclable / no reciclable), **metal** (lata / cable-RAEE), **lámpara** (fluorescente / LED / halógena), además de botella, frasco, envase, papel, bolsa y aceite.
* **`cargar_puntos_verdes()`:** Lee el dataset local de Puntos Verdes del Gobierno de la Ciudad de Buenos Aires (GCBA), incluyendo campos de `horario` y `materiales` aceptados por punto.

---

### C. Lógica del Motor e Inferencia: src/motor.py
Este archivo es el **cerebro del sistema experto** y gestiona el razonamiento y la normalización de lenguaje natural.

#### 1. Inferencia Lógica mediante Encadenamiento hacia Adelante (Forward Chaining)
Utiliza la biblioteca `experta` basada en hechos y reglas lógicas declarativas:
* **`Residuo` (Fact de entrada):** Representa el material y su estado físico real (`limpio`, `seco`, `roto`).
* **`Clasificado` (Fact intermedio):** Almacena el resultado lógico del estado del residuo y su respectiva justificación explicativa.
* **`Clasificacion` (Fact final):** Contiene la información técnica que se mostrará en pantalla.

Las reglas evalúan el estado del residuo y deducen clasificaciones intermedias más seguras:
```python
# Ejemplo de Regla de Estado Físico
@Rule(
    AS.r << Residuo(tipo='papel', limpio=False) |
    AS.r << Residuo(tipo='papel', seco=False) |
    AS.r << Residuo(tipo='carton', limpio=False) |
    AS.r << Residuo(tipo='carton', seco=False),
    salience=10
)
def regla_papel_sucio(self, r):
    # Deducimos un hecho intermedio alternativo si está mojado o engrasado
    self.declare(Clasificado(
        tipo='papel_no_reciclable',
        explicacion="Se reclasificó... porque está húmedo/sucio..."
    ))
```
La prioridad se define mediante `salience=10`, asegurando que las reglas de evaluación de estado físico se disparen **antes** de la regla por defecto (`salience=-10`).

#### 2. Metaprogramación y Construcción Dinámica
Para que la base de conocimientos sea dinámica, el motor lee el archivo CSV y genera en tiempo de ejecución las reglas de clasificación final mediante la función `construir_motor(reglas_dict)` utilizando `type()` para crear dinámicamente la clase `KnowledgeEngine`:
```python
def crear_metodo_regla(tipo: str, datos: dict):
    def metodo(self, _datos=datos):
        self.declare(Clasificacion(**_datos))
    metodo.__name__ = f'regla_{tipo}'
    return Rule(Clasificado(tipo=tipo))(metodo)
```

#### 3. Soporte Avanzado de Plurales en Español
Para resolver variaciones morfológicas en la descripción escrita por el usuario, `pattern_para_palabra(word)` genera expresiones regulares en tiempo real:
* **Plurales en `-ces` / Singulares en `-z`:** `lápices` o `lápiz` $\rightarrow$ regex: `lapi(z|ces)`.
* **Plurales en `-es`:** `papeles` o `papel` $\rightarrow$ regex: `papel(es)?`.
* **Plurales en `-s`:** `botellas` o `botella` $\rightarrow$ regex: `botellas?`.

La función `coincide_keyword` compila estas regex respetando límites de palabras completas (`\b` en regex) para evitar falsos positivos (por ejemplo, evitar que la keyword "pila" coincida con "depilar").

---

### D. Procesamiento Visual por IA: src/vision.py
**Propósito:** Clasificar residuos de forma multimodal (a partir de imágenes cargadas por el usuario). 

   **Gemini (Nube):**
   * Emplea el SDK oficial (`google-generativeai`).
   * Envía los bytes crudos de la imagen junto a un prompt restrictivo que solicita la descripción específica del residuo en una sola oración.

---

### E. Geoposicionamiento: src/geo.py
**Propósito:** Calcular qué Puntos Verdes físicos se encuentran más cercanos a la ubicación introducida por el usuario.
* **Fórmula de Haversine:** Calcula la distancia ortodrómica sobre la superficie de una esfera ($R = 6371$ km) a partir de diferencias de latitud y longitud.
* **Flexibilidad de Columnas:** Inspecciona dinámicamente las columnas del CSV mediante búsquedas difusas, permitiendo que el formato del dataset cambie sin romper la aplicación.
* **Radio dinámico con filtro de tipos:** `puntos_cercanos(lat, lon, df, radio_km=0.3, minimo=2, tipos=None)` — si el radio fijo devuelve menos de `minimo` puntos **del tipo solicitado**, expande automáticamente el radio hasta incluirlos. Esto garantiza que el mapa siempre muestre resultados relevantes aunque el tipo de punto esté lejos (ej. un Punto Verde Con Atención a 2.4 km).
* **Horario y materiales:** Retorna los campos `horario` y `materiales` de cada punto para su visualización en tooltips y tarjetas.

---

### F. Interfaz de Usuario: src/ui.py
**Propósito:** Darle una estética premium y renderizar de forma uniforme los resultados del motor.
* **`inyectar_estilos()`:** Lee directamente el archivo [src/style.css] y lo inserta en Streamlit en una etiqueta `<style>` con la opción `unsafe_allow_html=True`.
* **`mostrar_resultado(...)`:** Renderiza el contenedor final combinando código HTML y clases dinámicas. Si hay una discrepancia entre el tipo inicial y el tipo inferido final (por ejemplo, de `vidrio` a `vidrio_no_reciclable`), dibuja una transición visual explícita indicando al usuario la razón física del cambio. Al final de cada resultado muestra un **enlace al mapa** (`?tipos=<filtro>`) que lleva directamente a la Pestaña 3 con el tipo de punto correspondiente pre-seleccionado.

---

## 2. Interfaces de Streamlit (Frontend)

El proyecto expone dos interfaces para visualizar la evolución del prototipo base a la versión final:

### Sistema Experto: app_sistema_experto.py
* **Comportamiento:** Incorpora razonamiento interactivo y variables de estado sincronizadas (evalúa si los materiales cargados están húmedos, sucios o rotos).


#### 1. Sincronización Bidireccional entre Pestañas (Session State)
Streamlit reconstruye la vista completa en cada interacción. Si cambiamos del panel "Por texto" al de "Por imagen", los checkboxes físicos del estado del residuo podrían perderse. Para evitarlo, se programan callbacks y copias locales vinculadas al estado global (`st.session_state`):
```python
def sync_limpio_text():
    st.session_state.estado_limpio = st.session_state.estado_limpio_text
    st.session_state.estado_limpio_img = st.session_state.estado_limpio_text

# Checkbox en el tab de texto
st.checkbox(
    "Está limpio 🧼",
    key="estado_limpio_text",
    on_change=sync_limpio_text
)
```
Esto asegura que las variables de estado físico sean persistentes y consistentes sin importar la vía de entrada del residuo.

#### 2. Ejemplos Rápidos Inteligentes
El frontend expone botones para pruebas rápidas. Cuando el usuario hace clic en *"caja de pizza"*, un callback autodetecta el material e infiere lógicamente que contiene restos de grasa/aceite, desmarcando automáticamente el checkbox de **Está Limpio** en el frontend para forzar al motor a reclasificarlo como papel no reciclable.

#### 3. Mapa Interactivo con Filtros (Pestaña 3)
La pestaña de mapa permite explorar los puntos de descarte en CABA con las siguientes capacidades:

* **Filtros por tipo** (checkboxes): Con Atención · Contenedor Verde · Centro de Clasificación RSU · Contenedor Negro. Todos activos por defecto.
* **Filtro por URL**: el parámetro `?tipos=con_atencion` (o combinaciones separadas por coma como `?tipos=con_atencion,contenedor_verde`) pre-selecciona los filtros al abrir la pestaña. Esto permite que el enlace del resultado de clasificación lleve directamente al mapa con el filtro correcto.
* **Título dinámico**: se actualiza según los filtros activos, p. ej. *"Ubicación de Con Atención en CABA"*.
* **Dos modos de búsqueda**: geolocalización del navegador · ingreso de dirección (con Enter para buscar) ·
* **Radio adaptativo**: el radio (300 m por defecto) se expande automáticamente hasta incluir al menos 2 puntos del tipo filtrado. Cuando el radio se amplía, se informa al usuario.
* **Zoom automático**: el mapa se centra entre la ubicación del usuario y el centroide de los puntos visibles, y ajusta el zoom para que ambos queden en pantalla.
* **Tooltips enriquecidos**: cada punto muestra nombre, tipo, dirección, distancia, horario de atención y materiales aceptados.
* **Auto-navegación**: si la URL tiene el parámetro `?tipos=...`, el sistema navega automáticamente a la Pestaña 3 al cargar la página.

---

##  Arquitectura

```
Entrada del usuario (texto o imagen)
            │
            ▼
    detectar_tipo()
    keywords.csv → ordenadas por longitud (más específicas primero)
            │
            ├── término ambiguo → pregunta al usuario
            ├── inferencia según propiedades físicas (si está limpio, seco, roto)
            │
            ▼
    Motor de inferencia (experta — KnowledgeEngine)
    Reglas generadas dinámicamente desde reglas.csv
    Forward Chaining
            │
            ▼
    Clasificacion(categoria, instrucciones, impacto...)
            │
            ▼
        Resultado
```
A continuación se detalla cómo razona el motor con un ejemplo: **caja de pizza sucia**:

```
[Usuario escribe: "caja de pizza"]
       │
       ▼
[Normalización: "caja de pizza"]
       │
       ▼
[Mapeo por Keywords: coincide con "pizza" -> tipo "carton"]
       │
       ▼
[Evaluación del Estado Físico: limpio=False, seco=True, roto=False]
       │
       ▼
[Motor experta evalúa hechos: Residuo(tipo='carton', limpio=False, seco=True)]
       │
       ▼
[Se dispara regla_papel_sucio (Salience 10)]
       │
       ├─► Declara Hecho: Clasificado(tipo='papel_no_reciclable')
       └─► Genera Explicación: "Se reclasificó 'carton' a 'papel no reciclable' porque está sucio/con grasa..."
       │
       ▼
[Se dispara regla_papel_no_reciclable (Generada dinámicamente desde reglas.csv)]
       │
       └─► Declara Hecho: Clasificacion(categoria="Basura Común", contenedor="Gris (Basura Común)", ...)
       │
       ▼
[Frontend renderiza con clase 'card-basura' y muestra la explicación del razonamiento]
```

---

##  Base de conocimiento

| Categoría | Tipos de residuos cubiertos |
|---|---|
| ♻️ Reciclables | Plástico PET, Bolsas/Film, Plástico rígido (HDPE/PP), Vidrio, Papel, Cartón, Tetrabrik, Latas, Aerosoles vacíos |
| 🌱 Orgánicos | Restos de comida, frutas, verduras, yerba, café, poda |
| ⚠️ Especiales | Pilas AA/AAA/botón, Batería de auto (plomo-ácido), Medicamentos, Aceite de cocina, Aceite de motor, Electrónicos/RAEE, Lámparas fluorescentes/CFL, Lámparas LED, Ropa y textiles, Neumáticos, Madera/muebles |
| ⚠️ Peligrosos | Pinturas/barnices/solventes, PVC (código 03) |
| 🚫 Basura común | Papel higiénico, Pañales, Telgopor/EPS, Papel metalizado/encerado, Vidrio no reciclable |
| 🏗️ Voluminosos/Especiales | Escombros y residuos de construcción (Decreto GCBA 639/07) |
| ❓ Desconocido | Orientación general con derivación al municipio |

> **31 tipos de residuos** clasificados, alineados con Ley CABA 1854, Decreto 639/07, IRAM 13700, Ley 5991/2018 y Convenios de Basilea y Estocolmo.

La base de conocimiento es **extensible sin modificar el código**: agregar un material nuevo implica sólo agregar filas en los CSV.

---


##  Dependencias principales

| Librería | Uso |
|---|---|
| `experta==1.9.4` | Motor de inferencia (KnowledgeEngine) |
| `pandas` | Carga y procesamiento de CSV |
| `google-generativeai` | Clasificación por imagen con Gemini |
| `streamlit` | Interfaz web opcional |
| `matplotlib` | Visualización del árbol de decisión |
| `collections` | Acceso a clases contenedoras que mejoran los tipos estándar |
| `collections.abc` | Jerarquía de clases abstractas o para crear estructuras de datos personalizadas |
| `os` | Módulo del Sistema Operativo |
| `re` | Buscar, validar y manipular texto utilizando patrones complejos |
| `math` | Funciones matemáticas avanzadas y constantes numéricas |
| `get_geolocation de streamlit_js_eval` | Ubicación del usuario desde el navegador |
| `pydeck` | Visualizaciones interactivas de datos geoespaciales y mapas en 2D y 3D |

---

##  Datos abiertos utilizados

- **Puntos Verdes CABA**: [Portal de Datos Abiertos del Gobierno de la Ciudad de Buenos Aires](https://data.buenosaires.gob.ar/dataset/puntos-verdes)

---

> ⚠️ *Este sistema es orientativo y educativo. Para dudas específicas sobre el descarte de residuos, consultá en tu municipio o Punto Verde más cercano.*
