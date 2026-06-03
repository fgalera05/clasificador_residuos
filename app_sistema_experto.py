"""
♻️ Clasificador de Residuos para Reciclaje
Sistema Experto — Análisis de Datos II
"""

import streamlit as st
import pandas as pd

# Librería para obtener la geolocalización del navegador del usuario
from streamlit_js_eval import get_geolocation

# Importamos los módulos locales
# cargar_sistema: carga los CSVs con keywords, reglas y términos ambiguos.
# cargar_puntos_verdes: carga el dataset de puntos de reciclaje de CABA.
from src.data import cargar_sistema, cargar_puntos_verdes

# construir_motor: construye el motor de inferencia con experta (KnowledgeEngine).
# detectar_tipo: detecta el tipo de residuo a partir de un texto usando keywords.
# obtener_regla: aplica el motor para obtener la regla de clasificación final.
from src.motor import construir_motor, detectar_tipo, obtener_regla

# puntos_cercanos: calcula los puntos de reciclaje más cercanos a una coordenada dada.
from src.geo import puntos_cercanos

# inyectar_estilos: carga el CSS personalizado en la app.
# mostrar_resultado: renderiza la card de resultado de clasificación.
from src.ui import inyectar_estilos, mostrar_resultado

# analizar_imagen_con_gemini: llama a la API de Gemini para identificar el residuo en una imagen.
from src.vision import analizar_imagen_con_gemini

# ── Configuración de página ───────────────────────────────────────────────────
# Define el título, ícono, layout y estado inicial del sidebar de la app.
st.set_page_config(
    page_title=" Clasificador de Residuos",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyectamos estilos desde el archivo CSS modularizado
inyectar_estilos()

# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS & INICIALIZACIÓN
# ══════════════════════════════════════════════════════════════════════════════

# Carga los tres diccionarios que componen la base de conocimiento
KEYWORDS_DICT, REGLAS_DICT, AMBIGUOS_DICT = cargar_sistema()

# Construye dinámicamente el motor de inferencia (KnowledgeEngine de experta) a partir del diccionario de reglas cargado.
ClasificadorDinamico = construir_motor(REGLAS_DICT)

# Carga el DataFrame con los puntos verdes, contenedores y centros de reciclaje de CABA.
DF_PUNTOS_VERDES = cargar_puntos_verdes()

# Inicialización de variables de estado de streamlit
# Se usa st.session_state para persistir valores entre reruns de la app.
# Cada bloque 'if' evita sobrescribir el valor si ya fue inicializado.
if "query_text" not in st.session_state:
    st.session_state.query_text = ""
if "widget_texto_input" not in st.session_state:
    st.session_state.widget_texto_input = ""
if "resultado_texto" not in st.session_state:
    st.session_state.resultado_texto = None
if "last_image_key" not in st.session_state:
    st.session_state.last_image_key = None
if "image_description" not in st.session_state:
    st.session_state.image_description = None
if "estado_limpio" not in st.session_state:
    st.session_state.estado_limpio = True
if "estado_seco" not in st.session_state:
    st.session_state.estado_seco = True
if "estado_roto" not in st.session_state:
    st.session_state.estado_roto = False

# Inicialización de copias locales de variables de estado para evitar colisión de keys
if "estado_limpio_text" not in st.session_state:
    st.session_state.estado_limpio_text = True
if "estado_seco_text" not in st.session_state:
    st.session_state.estado_seco_text = True
if "estado_roto_text" not in st.session_state:
    st.session_state.estado_roto_text = False

if "estado_limpio_img" not in st.session_state:
    st.session_state.estado_limpio_img = True
if "estado_seco_img" not in st.session_state:
    st.session_state.estado_seco_img = True
if "estado_roto_img" not in st.session_state:
    st.session_state.estado_roto_img = False

# Callbacks de sincronización bidireccional entre las pestañas
def sync_limpio_text():
    st.session_state.estado_limpio = st.session_state.estado_limpio_text
    st.session_state.estado_limpio_img = st.session_state.estado_limpio_text

def sync_seco_text():
    st.session_state.estado_seco = st.session_state.estado_seco_text
    st.session_state.estado_seco_img = st.session_state.estado_seco_text

def sync_roto_text():
    st.session_state.estado_roto = st.session_state.estado_roto_text
    st.session_state.estado_roto_img = st.session_state.estado_roto_text

def sync_limpio_img():
    st.session_state.estado_limpio = st.session_state.estado_limpio_img
    st.session_state.estado_limpio_text = st.session_state.estado_limpio_img

def sync_seco_img():
    st.session_state.estado_seco = st.session_state.estado_seco_img
    st.session_state.estado_seco_text = st.session_state.estado_seco_img

def sync_roto_img():
    st.session_state.estado_roto = st.session_state.estado_roto_img
    st.session_state.estado_roto_text = st.session_state.estado_roto_img

# Función helper para renderizar los controles de estado físico justo antes de la card
def renderizar_controles_estado(suffix: str):
    """
    Muestra tres checkboxes para que el usuario indique el estado físico del residuo
    (limpio, seco, roto/dañado) justo antes de la card de resultado.

    El parámetro 'suffix' ("text" o "img") diferencia los keys de los widgets
    según la pestaña activa, evitando conflictos de estado entre tabs.

    Retorna la tupla (limpio, seco, roto) con los valores maestros actuales,
    que luego se pasan al motor para ajustar la clasificación.
    """
    st.markdown("##### 🔍 Estado físico del residuo (Variables de Estado)")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.checkbox(
            "Está limpio 🧼",
            value=st.session_state.get(f"estado_limpio_{suffix}", True),
            key=f"estado_limpio_{suffix}",
            on_change=sync_limpio_text if suffix == "text" else sync_limpio_img,
            help="El residuo no contiene restos de comida, grasa ni líquidos."
        )
    with col_e2:
        st.checkbox(
            "Está seco ☀️",
            value=st.session_state.get(f"estado_seco_{suffix}", True),
            key=f"estado_seco_{suffix}",
            on_change=sync_seco_text if suffix == "text" else sync_seco_img,
            help="El residuo no está mojado, húmedo o empapado con líquidos."
        )
    with col_e3:
        st.checkbox(
            "Está roto/dañado 💥",
            value=st.session_state.get(f"estado_roto_{suffix}", False),
            key=f"estado_roto_{suffix}",
            on_change=sync_roto_text if suffix == "text" else sync_roto_img,
            help="El residuo está quebrado, roto o deteriorado en su estructura física."
        )
    return st.session_state.estado_limpio, st.session_state.estado_seco, st.session_state.estado_roto

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Encabezado con nombre del sistema y listado de integrantes del grupo
    st.markdown("""
    <div style="padding: 0.5rem 0;">
        <div style="font-family:'Space Mono',monospace; font-size:1.6rem; color:#81c784; font-weight:700; text-align:center">
            Sistema Experto
        </div>
        <div style="font-size:1.2rem; color:#88bda3; margin-top:4px; text-align:center">
                <div>Análisis de Datos II  · GRUPO A </div></br>
                <div>Luciano Asís</div>
                <div>Gustavo Barrajón</div>
                <div>Fernando Galera</div>
                <div>Gabrial García</div>
                <div>Facundo Martínez</div>
                <div>Andrea Moreno</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center">
                <div style="font-size:1.2rem">🔧 Configuración</div>
                <div style="font-size:1.4rem">API Key de Gemini</div>
    </div>
    """, unsafe_allow_html=True)

    # Campo de texto enmascarado para ingresar la API Key de Gemini.
    # Es necesaria para usar la funcionalidad de clasificación por imagen (Tab 2).
    gemini_key = st.text_input(
        "",
        type="password",
        placeholder="Para clasificación por imagen",
        help="Obtené tu key gratis en aistudio.google.com"
    )

    st.markdown("---")
    # Métricas que muestran el tamaño actual de la base de conocimiento cargada
    st.markdown("""
    <div style="font-size:1.2rem; text-align:center">📊 Base de conocimiento</div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
        /* Centra todo el bloque contenedor de la métrica */
        [data-testid="stMetric"] {
            display: flex;
            justify-content: center;
            text-align: center;
        }
        
        /* Centra la etiqueta (label), el valor y el delta internamente */
        [data-testid="stMetric"] > div {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])  # Estructura de 3 columnas

    with col2:
        st.metric("Tipos de residuos", len(REGLAS_DICT))
        st.metric("Keywords activas", sum(len(v) for v in KEYWORDS_DICT.values()))
        st.metric("Términos ambiguos", len(AMBIGUOS_DICT))

    st.markdown("---")
    # Información estática sobre los motores y fuentes de datos utilizados
    st.markdown("""
    <div style="font-size:1.1rem; color:#88bda3; line-height:1.6; text-align:center">
        <b>Motores:</b><br>
        • experta (KnowledgeEngine)<br>
        • Forward Chaining <br>
        • Gemini (imágenes)<br><br>
        <b>Datos:</b><br>
        • keywords.csv<br>
        • reglas.csv<br>
        • ambiguos.csv<br>
        • Puntos Verdes CABA (GCBA)
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CONTENIDO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

# Título y subtítulo de la aplicación
st.markdown("""
<div style="padding: 1.5rem 0 1rem 0;">
    <div class="titulo-principal">Clasificador de Residuos ♻️</div>
    <div class="subtitulo">Sistema Experto basado en reglas · Análisis de Datos II</div>
</div>
""", unsafe_allow_html=True)

# Los controles de estado físico ahora se muestran dentro de cada pestaña, directamente antes de la card.

# Creación de las tres pestañas principales de la aplicación
tab1, tab2, tab3 = st.tabs(["📝  Por texto", "📷  Por imagen", "📍  Puntos Verdes"])

# Auto-navegar a pestaña 3 cuando la URL tiene ?tipos=... (una vez por valor de param)
# Si la URL contiene ?tipos=... (por ejemplo, al compartir un enlace con filtros preseleccionados),
# se ejecuta un script JS que hace clic en la pestaña "Puntos Verdes" automáticamente.
# El flag en session_state asegura que el salto ocurra solo una vez por valor de parámetro.
_url_tipos_param = st.query_params.get("tipos", "")
if _url_tipos_param and not st.session_state.get(f"_tab3_auto_{_url_tipos_param}"):
    st.session_state[f"_tab3_auto_{_url_tipos_param}"] = True
    import streamlit.components.v1 as _stc_v1
    # JS inyectado: busca el botón de la pestaña "Puntos" y le hace clic con un pequeño delay
    _stc_v1.html(
        """<script>(function(){function _go(){var t=window.parent.document.querySelectorAll('button[role="tab"]');
        for(var i=0;i<t.length;i++){if(t[i].textContent.indexOf('Puntos')>-1){t[i].click();return;}}}
        setTimeout(_go,500);setTimeout(_go,1100);})();</script>""",
        height=0,
    )

# ── TAB 1: Clasificación por texto ────────────────────────────────────────────
with tab1:
    st.markdown("#### Describí el residuo que tenés")

    # Callback para cuando el input de texto cambia por Enter/unfocus
    def on_query_change():
        val = st.session_state.widget_texto_input.strip()
        st.session_state.query_text = val
        st.session_state.resultado_texto = None

    # Layout: campo de texto (ancho) + botón Clasificar (estrecho)
    col1, col2 = st.columns([3, 1])
    with col1:
        texto_input = st.text_input(
            label="residuo",
            placeholder="ej: botella de plástico, pila gastada, cáscara de naranja...",
            label_visibility="collapsed",
            key="widget_texto_input",
            on_change=on_query_change   # Dispara on_query_change al cambiar el valor
        )
    with col2:
        clasificar_btn = st.button("Clasificar →", use_container_width=True)

    # Si se hace clic en el botón Clasificar
    if clasificar_btn:
        val = st.session_state.widget_texto_input.strip()
        if val:
            # Actualiza la consulta activa y limpia el resultado anterior
            st.session_state.query_text = val
            st.session_state.resultado_texto = None
        else:
            st.info("Escribí qué residuo tenés para clasificarlo.")

    # Procesar la consulta activa
    query = st.session_state.query_text
    if query:
        # detectar_tipo analiza el texto con el diccionario de keywords.
        # Puede devolver: un tipo de residuo directo, o "ambiguo:<termino>" si hay ambigüedad.
        tipo = detectar_tipo(query, KEYWORDS_DICT, AMBIGUOS_DICT)

        # Manejo de ambigüedad
        if tipo.startswith("ambiguo:"):
            termino = tipo.split(":")[1]    # Extrae el término ambiguo
            info = AMBIGUOS_DICT[termino]   # Obtiene las opciones

            st.warning(f"🤔 **\"{termino}\"** puede ser de distintos materiales.")
            st.markdown(f"**{info['pregunta']}**")   # Muestra la pregunta aclaradora con las opciones

            # Prepara las listas de etiquetas y tipos para el radio button
            opciones_labels = [desc for _, desc in info["opciones"].values()]
            opciones_tipos  = [t for t, _ in info["opciones"].values()]

            # Usamos un key único compuesto para evitar problemas de persistencia cruzada
            radio_key = f"radio_{termino}_{query}"
            eleccion = st.radio(
                "Seleccioná una opción:",
                options=range(len(opciones_labels)),
                format_func=lambda i: opciones_labels[i],
                label_visibility="collapsed",
                key=radio_key
            )

            # Usa el tipo elegido por el usuario para continuar con la clasificación
            tipo_final = opciones_tipos[eleccion]
            # Mostrar controles justo antes de la card
            limpio, seco, roto = renderizar_controles_estado("text")
            # Aplica el motor de inferencia con el tipo y los estados físicos
            regla = obtener_regla(tipo_final, ClasificadorDinamico, REGLAS_DICT, limpio=limpio, seco=seco, roto=roto)
            # Muestra la card de resultado con instrucciones de descarte
            mostrar_resultado(regla, tipo_final, limpio=limpio, seco=seco, roto=roto)

        else:
            # Tipo detectado sin ambigüedad: se clasifica directamente
            limpio, seco, roto = renderizar_controles_estado("text")
            regla = obtener_regla(tipo, ClasificadorDinamico, REGLAS_DICT, limpio=limpio, seco=seco, roto=roto)
            mostrar_resultado(regla, tipo, limpio=limpio, seco=seco, roto=roto)

    # Ejemplos rápidos
    st.markdown("---")
    st.markdown("**⚡ Ejemplos rápidos**")
    ejemplos = [
        "botella de gaseosa", "pila gastada", "aceite de cocina usado",
        "caja de pizza", "árbol de navidad de plástico", "cáscara de naranja",
        "celular roto", "espejo roto", "papel higiénico"
    ]

    def seleccionar_ejemplo(ej_val):
        """
        Callback ejecutado al hacer clic en un ejemplo rápido.
        Carga el ejemplo en el campo de texto y pre-configura los checkboxes
        de estado físico según palabras clave del ejemplo (ej: 'roto', 'pizza', 'usado').
        """
        st.session_state.widget_texto_input = ej_val
        st.session_state.query_text = ej_val
        st.session_state.resultado_texto = None
        
        # Sincronizar checkboxes con palabras clave del ejemplo
        val_lower = ej_val.lower()
        roto_val = "roto" in val_lower or "dañado" in val_lower
        limpio_val = not ("pizza" in val_lower or "sucio" in val_lower or "usado" in val_lower or "higienico" in val_lower)
        seco_val = not ("humedo" in val_lower or "mojado" in val_lower)

        st.session_state.estado_roto = roto_val
        st.session_state.estado_limpio = limpio_val
        st.session_state.estado_seco = seco_val

        # Sincronizar también las copias locales de las pestañas
        st.session_state.estado_roto_text = roto_val
        st.session_state.estado_limpio_text = limpio_val
        st.session_state.estado_seco_text = seco_val

        st.session_state.estado_roto_img = roto_val
        st.session_state.estado_limpio_img = limpio_val
        st.session_state.estado_seco_img = seco_val

    cols = st.columns(3)
    for i, ej in enumerate(ejemplos):
        cols[i % 3].button(
            ej,
            key=f"ej_{i}",
            use_container_width=True,
            on_click=seleccionar_ejemplo,
            args=(ej,)
        )


# ── TAB 2: Clasificación por imagen ──────────────────────────────────────────
with tab2:
    st.markdown("#### Subí una foto del residuo")
    st.markdown("La IA identifica el material y el sistema experto lo clasifica.")

    # Verificación de API Key: si no se ingresó, se muestra advertencia y no se habilita el uploader
    if not gemini_key:
        st.warning("⚠️ Ingresá tu API Key de Gemini en el panel izquierdo para usar esta función. Podés obtenerla gratis en [aistudio.google.com](https://aistudio.google.com).")
    else:
        # Widget de carga de imagen; acepta JPG, JPEG, PNG y WEBP
        imagen = st.file_uploader(
            "Subir imagen",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )

        if imagen:
            # Key única basada en nombre y tamaño del archivo para detectar si se subió una imagen nueva
            image_key = f"{imagen.name}_{imagen.size}"
            
            # Limpiar caché de imagen si se sube una nueva
            if st.session_state.last_image_key != image_key:
                st.session_state.last_image_key = image_key
                st.session_state.image_description = None

            # Layout: columna izquierda para la imagen, columna derecha para el resultado
            col_img, col_res = st.columns([1, 1])
            with col_img:
                # Muestra la imagen subida                
                st.image(imagen, caption="Imagen subida", use_container_width=True)

            with col_res:
                # Si aún no se analizó esta imagen, se llama a Gemini
                if st.session_state.image_description is None:
                    with st.spinner("🤖 Analizando con Gemini..."):
                        try:
                            # Lee los bytes de la imagen y determina el tipo MIME
                            image_bytes = imagen.read()
                            ext = imagen.name.split(".")[-1].lower()
                            mime = {"jpg":"image/jpeg","jpeg":"image/jpeg",
                                    "png":"image/png","webp":"image/webp"}.get(ext,"image/jpeg")

                            # Llamada al modelo de visión para obtener descripción textual del residuo
                            descripcion = analizar_imagen_con_gemini(image_bytes, mime, gemini_key)

                            # Guarda la descripción en session_state para no volver a llamar a la API
                            st.session_state.image_description = descripcion
                        except Exception as e:
                            st.error(f"Error al analizar la imagen: {e}")
                            descripcion = None

                # Si tenemos una descripción en caché o procesada recién
                if st.session_state.image_description:
                    descripcion = st.session_state.image_description
                    # Muestra qué identificó Gemini
                    st.success(f"🤖 Gemini identificó: **{descripcion}**")

                    # Usa la descripción de Gemini como entrada para el motor de inferencia
                    tipo = detectar_tipo(descripcion, KEYWORDS_DICT, AMBIGUOS_DICT)

                    
                    # El material identificado es ambiguo: se pide al usuario que aclare
                    if tipo.startswith("ambiguo:"):
                        st.info(f"Material ambiguo detectado: **{descripcion}**. Usá la pestaña de texto para aclarar.")
                        termino = tipo.split(":")[1]
                        info = AMBIGUOS_DICT[termino]

                        st.warning(f"🤔 **\"{termino}\"** puede ser de distintos materiales.")
                        st.markdown(f"**{info['pregunta']}**")

                        opciones_labels = [desc for _, desc in info["opciones"].values()]
                        opciones_tipos  = [t for t, _ in info["opciones"].values()]

                        # Usamos un key único compuesto para evitar problemas de persistencia cruzada
                        radio_key = f"radio_{termino}_{descripcion}"
                        eleccion = st.radio(
                            "Seleccioná una opción:",
                            options=range(len(opciones_labels)),
                            format_func=lambda i: opciones_labels[i],
                            label_visibility="collapsed",
                            key=radio_key
                        )

                        tipo_final = opciones_tipos[eleccion]
                        # Mostrar controles justo antes de la card
                        limpio, seco, roto = renderizar_controles_estado("img")
                        regla = obtener_regla(tipo_final, ClasificadorDinamico, REGLAS_DICT, limpio=limpio, seco=seco, roto=roto)
                        mostrar_resultado(regla, tipo_final, limpio=limpio, seco=seco, roto=roto)
                    else:
                        # Mostrar controles justo antes de la card
                        limpio, seco, roto = renderizar_controles_estado("img")
                        regla = obtener_regla(tipo, ClasificadorDinamico, REGLAS_DICT, limpio=limpio, seco=seco, roto=roto)
                        mostrar_resultado(regla, tipo, limpio=limpio, seco=seco, roto=roto)
        else:
            # Limpiar variables si no hay imagen cargada
            st.session_state.last_image_key = None
            st.session_state.image_description = None



# ── TAB 3: Mapa de Puntos y Contenedores ─────────────────────────────────────

# ── Diccionarios de colores por tipo de punto de reciclaje ───────────────────
# Usados para diferenciar visualmente los tipos en el mapa y en las cards
_COLOR_TIPO = {
    "Con Atención"               : "#f5c800",
    "Centro de Clasificación RSU": "#1464c8",
    "Contenedor Verde"            : "#22a83a",
    "Contenedor Negro"            : "#555555",
}
# Mismos colores en formato RGBA (lista de 4 enteros 0-255) para las capas de pydeck
_COLOR_TIPO_RGB = {
    "Con Atención"               : [245, 200,   0, 230],
    "Centro de Clasificación RSU": [ 30, 100, 200, 230],
    "Contenedor Verde"            : [ 34, 168,  58, 230],
    "Contenedor Negro"            : [ 85,  85,  85, 200],
}
# Color del marcador de posición del usuario (rojo)
_COLOR_USUARIO_RGB = [220, 50, 50, 255]
_RADIO_TIPO = {"Contenedor Verde": 8, "default": 5}

# Mapeos para filtros de pestaña 3
_FILTRO_A_TIPO = {
    "con_atencion":     "Con Atención",
    "contenedor_verde": "Contenedor Verde",
    "rsu":              "Centro de Clasificación RSU",
    "contenedor_negro": "Contenedor Negro",
}
# Etiquetas y colores para mostrar en los checkboxes y la leyenda del mapa
_FILTRO_LABELS_TAB3 = {
    "con_atencion":     ("Con Atención",                 "#f5c800"),
    "contenedor_verde": ("Contenedor Verde",              "#22a83a"),
    "rsu":              ("Centro de Clasificación RSU",   "#1464c8"),
    "contenedor_negro": ("Contenedor Negro",              "#555555"),
}
# Horarios y materiales por defecto cuando el CSV no tiene datos
_HORARIO_DEFAULT = {
    "Contenedor Verde":            "Sin restricción horaria · disponible 24 hs",
    "Contenedor Negro":            "Recomendado: depositar entre 19 y 21 hs (días de recolección)",
    "Centro de Clasificación RSU": "Consultar con el centro",
    "Con Atención":                "",
}
_MATERIALES_DEFAULT = {
    "Contenedor Verde":            "Papel · Cartón · Plástico · Metal · Vidrio · Tetrabrik",
    "Contenedor Negro":            "Residuos no reciclables",
    "Centro de Clasificación RSU": "Materiales reciclables separados por tipo",
    "Con Atención":                "",
}

with tab3:

    # ── Leer parámetro de URL y configurar filtros ────────────────────────────
    # Si la URL contiene ?tipos=contenedor_verde,rsu, se preseleccionan esos filtros
    _tipos_param_t3 = st.query_params.get("tipos", "")
    # Parsea el parámetro y valida que cada valor exista en el mapeo de filtros
    _tipos_url_t3   = [t.strip() for t in _tipos_param_t3.split(",")
                       if t.strip() in _FILTRO_LABELS_TAB3] if _tipos_param_t3 else []
    # Si hay filtros en la URL los usa; si no, selecciona todos por defecto
    _default_sel    = _tipos_url_t3 if _tipos_url_t3 else list(_FILTRO_LABELS_TAB3.keys())

    # ── Checkboxes de filtro ──────────────────────────────────────────────────
    st.markdown("**🔽 Filtrar por tipo de punto:**")
    _fcols = st.columns(4)
    _tipos_sel_t3 = []
    for _fi, (_fk, (_flbl, _fcol)) in enumerate(_FILTRO_LABELS_TAB3.items()):
        with _fcols[_fi]:
            if st.checkbox(
                _flbl,
                value=(_fk in _default_sel),
                key=f"filtro_t3_{_fk}",
            ):
                _tipos_sel_t3.append(_fk)

    # ── Título dinámico según filtros activos ─────────────────────────────────
    _all_filtro_keys = set(_FILTRO_LABELS_TAB3.keys())
    if not _tipos_sel_t3 or set(_tipos_sel_t3) == _all_filtro_keys:
        _titulo_t3 = "Puntos y Contenedores en CABA"
    elif len(_tipos_sel_t3) == 1:
        _titulo_t3 = f"Ubicación de {_FILTRO_LABELS_TAB3[_tipos_sel_t3[0]][0]} en CABA"
    else:
        _labs_t3 = [_FILTRO_LABELS_TAB3[t][0] for t in _tipos_sel_t3]
        _titulo_t3 = "Ubicación de " + ", ".join(_labs_t3[:-1]) + f" y {_labs_t3[-1]} en CABA"

    st.markdown(f"#### {_titulo_t3}")

    # ── Inicializar session state ─────────────────────────────────────────────
    # Coordenadas por defecto: centro geográfico aproximado de CABA
    for _k, _v in [("tab3_lat", -34.6083), ("tab3_lon", -58.3712),
                   ("tab3_modo", None), ("tab3_puntos", None),
                   ("tab3_busq_lat", -34.6083), ("tab3_busq_lon", -58.3712),
                   ("tab3_geo_lat_proc", None), ("tab3_geo_lon_proc", None)]:
        if _k not in st.session_state:
            st.session_state[_k] = _v

    def _buscar(lat, lon):
        """
        Realiza la búsqueda de puntos cercanos a las coordenadas (lat, lon) dadas.
        Aplica un radio inicial de 0.3 km con mínimo de 2 resultados.
        Filtra por los tipos de punto seleccionados actualmente en los checkboxes.
        Guarda los resultados y parámetros de búsqueda en session_state.
        """
        # Pasar los tipos activos para que el radio se expanda hacia esos tipos
        _tipos_busq = [_FILTRO_A_TIPO[k] for k in _tipos_sel_t3] if _tipos_sel_t3 else None
        st.session_state["tab3_puntos"]      = puntos_cercanos(lat, lon, DF_PUNTOS_VERDES,
                                                               radio_km=0.3, minimo=2,
                                                               tipos=_tipos_busq)
        st.session_state["tab3_busq_lat"]    = lat
        st.session_state["tab3_busq_lon"]    = lon
        st.session_state["tab3_tipos_busq"]  = frozenset(_tipos_busq) if _tipos_busq else None

    # ── Botones de modo ───────────────────────────────────────────────────────
    _col_b1, _col_b2 = st.columns(2)
    with _col_b1:
        if st.button("📍 Usar mi ubicación", use_container_width=True):
            st.session_state["tab3_modo"] = "geo"
    with _col_b2:
        if st.button("✏️ Ingresar dirección", use_container_width=True):
            st.session_state["tab3_modo"] = "dir"

    _modo = st.session_state["tab3_modo"]

    if _modo == "geo":
        # Obtiene las coordenadas del navegador usando la librería streamlit_js_eval
        _loc = get_geolocation()
        if _loc and _loc.get("coords"):
            _g_lat = _loc["coords"]["latitude"]
            _g_lon = _loc["coords"]["longitude"]
            if _g_lat != st.session_state["tab3_geo_lat_proc"] or \
               _g_lon != st.session_state["tab3_geo_lon_proc"]:
                st.session_state["tab3_lat"] = _g_lat
                st.session_state["tab3_lon"] = _g_lon
                st.session_state["tab3_geo_lat_proc"] = _g_lat
                st.session_state["tab3_geo_lon_proc"] = _g_lon
                _buscar(_g_lat, _g_lon)

    elif _modo == "dir":
        # Formulario de geocodificación manual: el usuario escribe una dirección
        with st.form("form_geocode", border=False):
            _addr = st.text_input("", placeholder="Ej: Av. Corrientes 1234, Buenos Aires",
                                  label_visibility="collapsed")
            if st.form_submit_button("🔍 Buscar", use_container_width=True) and _addr.strip():
                try:
                    import requests as _req
                    # Llama a la API de Nominatim (OpenStreetMap) para convertir la dirección en coordenadas
                    _res = _req.get(
                        "https://nominatim.openstreetmap.org/search",
                        params={"q": _addr, "format": "json", "limit": 1,
                                "countrycodes": "ar", "addressdetails": 0},
                        headers={"User-Agent": "clasificador-residuos-caba/1.0"},
                        timeout=5,
                    ).json()
                    if _res:
                        # Extrae lat/lon del primer resultado y lanza la búsqueda de puntos
                        _lat2, _lon2 = float(_res[0]["lat"]), float(_res[0]["lon"])
                        st.session_state["tab3_lat"] = _lat2
                        st.session_state["tab3_lon"] = _lon2
                        _buscar(_lat2, _lon2)
                    else:
                        st.warning("No se encontró la dirección.")
                except Exception:
                    import traceback
                    print(traceback.format_exc())
                    st.error("Error al geocodificar. Verificá tu conexión.")

    _puntos   = st.session_state.get("tab3_puntos")
    _busq_lat = st.session_state["tab3_busq_lat"]
    _busq_lon = st.session_state["tab3_busq_lon"]

    if _puntos:
        import pydeck as pdk

        # Filtrar por tipos seleccionados
        _tipos_csv_sel = {_FILTRO_A_TIPO[k] for k in _tipos_sel_t3} \
                         if _tipos_sel_t3 else set(_FILTRO_A_TIPO.values())
        _puntos_fil = [p for p in _puntos if p.get("tipo", "") in _tipos_csv_sel]

        # Fallback: si el filtro cambió después de la búsqueda y no hay resultados,
        # hacer una búsqueda ampliada para los tipos pedidos (cacheada en session_state)
        if not _puntos_fil and _tipos_csv_sel and _busq_lat != -34.6083:
            _ck = "_fb_" + "_".join(sorted(_tipos_csv_sel)) + f"_{_busq_lat:.5f}_{_busq_lon:.5f}"
            if _ck not in st.session_state:
                st.session_state[_ck] = puntos_cercanos(
                    _busq_lat, _busq_lon, DF_PUNTOS_VERDES,
                    radio_km=0.3, minimo=2, tipos=list(_tipos_csv_sel),
                )
            _puntos_fil = [p for p in st.session_state[_ck] if p.get("tipo", "") in _tipos_csv_sel]

        # Preparar datos completando horario/materiales con defaults por tipo
        _puntos_data = []
        for _p in _puntos_fil:
            _tp  = _p.get("tipo", "")
            _hor = _p.get("horario", "")    or _HORARIO_DEFAULT.get(_tp, "")
            _mat = _p.get("materiales", "") or _MATERIALES_DEFAULT.get(_tp, "")
            _puntos_data.append({
                "lon":        _p["lon"],
                "lat":        _p["lat"],
                "nombre":     _p["nombre"],
                "tipo":       _tp,
                "direccion":  _p["direccion"],
                "distancia":  f"{int(_p['dist_km']*1000)} metros",
                "horario":    _hor,
                "materiales": _mat,
                "color":      _COLOR_TIPO_RGB.get(_tp, [128, 128, 128, 200]),
                "radio_px":   _RADIO_TIPO.get(_tp, _RADIO_TIPO["default"]),
            })

        # Separa los puntos por tipo para renderizarlos en capas distintas
        # (los Contenedores Verdes tienen radio más grande en el mapa) 
        _datos_peq  = [p for p in _puntos_data if p["tipo"] != "Contenedor Verde"]
        _datos_verd = [p for p in _puntos_data if p["tipo"] == "Contenedor Verde"]


        # ── Construcción de capas de pydeck ───────────────────────────────────
        _capas = []
        if _datos_peq:
            # Capa para todos los tipos excepto Contenedor Verde (radio más pequeño)
            _capas.append(pdk.Layer(
                "ScatterplotLayer", _datos_peq,
                get_position=["lon", "lat"], get_fill_color="color",
                get_radius=10, radius_min_pixels=4, radius_max_pixels=4,
                pickable=True,   # Habilitado para el tooltip al hacer hover
            ))
        if _datos_verd:
            # Capa exclusiva para Contenedores Verdes con radio visualmente mayor
            _capas.append(pdk.Layer(
                "ScatterplotLayer", _datos_verd,
                get_position=["lon", "lat"], get_fill_color="color",
                get_radius=10, radius_min_pixels=8, radius_max_pixels=8,
                pickable=True,
            ))
        # Capa adicional para mostrar la posición del usuario
        _capas.append(pdk.Layer(
            "ScatterplotLayer",
            [{"lon": _busq_lon, "lat": _busq_lat, "nombre": "Tu ubicación",
              "tipo": "", "direccion": "", "distancia": "", "horario": "",
              "materiales": "", "color": _COLOR_USUARIO_RGB, "radio_px": 10}],
            get_position=["lon", "lat"], get_fill_color="color",
            get_radius=10, radius_min_pixels=10, radius_max_pixels=10,
            pickable=True,
        ))

        # ── Cálculo de vista del mapa (centro y zoom dinámico) ────────────────
        if _puntos_fil:
            # Centrar entre ubicación del usuario y centroide de puntos visibles
            _avg_lat = sum(p["lat"] for p in _puntos_fil) / len(_puntos_fil)
            _avg_lon = sum(p["lon"] for p in _puntos_fil) / len(_puntos_fil)
            _view_lat = (_busq_lat + _avg_lat) / 2
            _view_lon = (_busq_lon + _avg_lon) / 2
            # Zoom según el punto filtrado más lejano (con margen)
            _max_dist_km = max(p["dist_km"] for p in _puntos_fil)
            if   _max_dist_km < 0.15: _zoom = 16
            elif _max_dist_km < 0.35: _zoom = 15
            elif _max_dist_km < 0.70: _zoom = 14
            elif _max_dist_km < 1.50: _zoom = 13
            elif _max_dist_km < 3.00: _zoom = 12
            elif _max_dist_km < 6.00: _zoom = 11
            else:                      _zoom = 10
        else:
            # Sin resultados: centra en la ubicación buscada con zoom alto
            _view_lat, _view_lon, _zoom = _busq_lat, _busq_lon, 16


        # Configura la vista inicial del mapa (latitud, longitud, nivel de zoom)
        _vista = pdk.ViewState(latitude=_view_lat, longitude=_view_lon, zoom=_zoom)
        # Construye el mapa con las capas, la vista y el estilo Positron (fondo claro)
        _deck  = pdk.Deck(
            layers=_capas,
            initial_view_state=_vista,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            # Tooltip con información del punto al hacer hover
            tooltip={"html": (
                "<b>{nombre}</b><br/>"
                "<span style='color:#aaa;font-size:0.85em'>{tipo}</span><br/>"
                "📍 {direccion}<br/>"
                "🚶 {distancia}<br/>"
                "🕐 {horario}<br/>"
                "♻️ {materiales}"
            )},
        )
        st.pydeck_chart(_deck)          # Renderiza el mapa en la app

        # Leyenda dinámica según filtros activos
        _leyenda_html = '<div style="display:flex;gap:20px;font-size:0.82rem;margin-top:4px;flex-wrap:wrap;">'
        for _fk, (_flbl, _fcol) in _FILTRO_LABELS_TAB3.items():
            if not _tipos_sel_t3 or _fk in _tipos_sel_t3:
                _leyenda_html += (
                    f'<span><span style="display:inline-block;width:11px;height:11px;'
                    f'background:{_fcol};border-radius:50%;margin-right:4px;"></span>'
                    f'{_flbl}</span>'
                )
        _leyenda_html += (
            '<span><span style="display:inline-block;width:11px;height:11px;'
            'background:#e63215;border-radius:50%;margin-right:4px;"></span>Tu ubicación</span>'
            '</div>'
        )
        st.markdown(_leyenda_html, unsafe_allow_html=True)

        # ── Resumen y cards de resultados ─────────────────────────────────────
        _radio_real = int(max(p["dist_km"] for p in _puntos_fil) * 1000) if _puntos_fil else 0
        _radio_txt  = f"{_radio_real} m" if _radio_real <= 300 else f"~{_radio_real} m (radio ampliado)"
        st.markdown(f"**{len(_puntos_fil)} puntos** en {_radio_txt} ({_titulo_t3}):")
        
        # Renderiza una card HTML para cada punto encontrado
        for _p in _puntos_fil:
            _tl   = _p.get("tipo", "—")
            _cdot = _COLOR_TIPO.get(_tl, "#808080")
            _hor  = _p.get("horario", "")    or _HORARIO_DEFAULT.get(_tl, "")
            _mat  = _p.get("materiales", "") or _MATERIALES_DEFAULT.get(_tl, "")
            _hor_html = (f'<div style="font-size:0.75rem;color:#81c784;margin-top:2px;">🕐 {_hor}</div>'
                         if _hor else "")
            _mat_html = (f'<div style="font-size:0.75rem;color:#aed6bf;margin-top:1px;">♻️ {_mat}</div>'
                         if _mat else "")
            st.markdown(f"""
            <div class="punto-verde-card">
                <div class="punto-verde-nombre">
                    <span style="display:inline-block;width:10px;height:10px;background:{_cdot};border-radius:50%;margin-right:6px;"></span>
                    {_p['nombre']}
                </div>
                <div style="font-size:0.78rem;color:#555;margin-bottom:2px;">{_tl}</div>
                <div class="punto-verde-dir">📍 {_p['direccion']}</div>
                <div class="punto-verde-dist">🚶 {int(_p['dist_km']*1000)} metros de distancia</div>
                {_hor_html}
                {_mat_html}
            </div>
            """, unsafe_allow_html=True)

    elif _puntos is not None:
        st.info("No se encontraron puntos cercanos. Intentá con otra dirección.")

    st.caption("Datos: [Portal de Datos Abiertos de CABA](https://data.buenosaires.gob.ar/dataset/puntos-verdes)")
