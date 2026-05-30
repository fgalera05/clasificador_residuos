"""
♻️ Clasificador de Residuos para Reciclaje (Versión 2 - Inferencia Real)
Sistema Experto — Análisis de Datos II
"""

import streamlit as st
import pandas as pd

# Importamos los módulos locales
from src.data import cargar_sistema, cargar_puntos_verdes
from src.motor import construir_motor, detectar_tipo, obtener_regla
from src.geo import puntos_cercanos
from src.ui import inyectar_estilos, mostrar_resultado
from src.vision import analizar_imagen_con_gemini, analizar_imagen_local

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="♻️ Clasificador de Residuos (v2)",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyectamos estilos desde el archivo CSS modularizado
inyectar_estilos()

# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS & INICIALIZACIÓN
# ══════════════════════════════════════════════════════════════════════════════

KEYWORDS_DICT, REGLAS_DICT, AMBIGUOS_DICT = cargar_sistema()
ClasificadorDinamico = construir_motor(REGLAS_DICT)
DF_PUNTOS_VERDES = cargar_puntos_verdes()

# Inicialización de variables de estado
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
    st.markdown("""
    <div style="padding: 1rem 0;">
        <div style="font-family:'Space Mono',monospace; font-size:1.1rem; color:#69f0ae; font-weight:700;">
            ♻️ Clasificador v2
        </div>
        <div style="font-size:0.8rem; color:#81c784; margin-top:4px;">
            Sistema Experto · Análisis de Datos II
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**📊 Base de conocimiento**")
    st.metric("Tipos de residuos", len(REGLAS_DICT))
    st.metric("Keywords activas", sum(len(v) for v in KEYWORDS_DICT.values()))
    st.metric("Términos ambiguos", len(AMBIGUOS_DICT))

    st.markdown("---")
    st.markdown("**🔧 Configuración**")

    vision_motor = st.selectbox(
        "Motor de Visión",
        options=["Hugging Face (Local - Tensores)", "Gemini (Nube)"],
        index=0,
        help="Elegí si procesar la imagen de forma local usando Hugging Face o en la nube usando Gemini."
    )

    gemini_key = None
    if vision_motor == "Gemini (Nube)":
        gemini_key = st.text_input(
            "API Key de Gemini",
            type="password",
            placeholder="Para clasificación por imagen",
            help="Obtené tu key gratis en aistudio.google.com"
        )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.75rem; color:#4caf50; line-height:1.6;">
        <b>Motores:</b><br>
        • experta (KnowledgeEngine)<br>
        • Forward Chaining + State Rules<br>
        • Gemini / HF Local (imágenes)<br><br>
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

st.markdown("""
<div style="padding: 1.5rem 0 1rem 0;">
    <div class="titulo-principal">Clasificador de<br>Residuos ♻️</div>
    <div class="subtitulo">Sistema Experto basado en reglas · Análisis de Datos II</div>
</div>
""", unsafe_allow_html=True)

# Los controles de estado físico ahora se muestran dentro de cada pestaña, directamente antes de la card.

tab1, tab2, tab3 = st.tabs(["📝 Por texto", "📷 Por imagen", "📍 Puntos Verdes"])


# ── TAB 1: Clasificación por texto ────────────────────────────────────────────
with tab1:
    st.markdown("#### Describí el residuo que tenés")

    # Callback para cuando el input de texto cambia por Enter/unfocus
    def on_query_change():
        val = st.session_state.widget_texto_input.strip()
        st.session_state.query_text = val
        st.session_state.resultado_texto = None

    col1, col2 = st.columns([3, 1])
    with col1:
        texto_input = st.text_input(
            label="residuo",
            placeholder="ej: botella de plástico, pila gastada, cáscara de naranja...",
            label_visibility="collapsed",
            key="widget_texto_input",
            on_change=on_query_change
        )
    with col2:
        clasificar_btn = st.button("Clasificar →", use_container_width=True)

    # Si se hace clic en el botón Clasificar
    if clasificar_btn:
        val = st.session_state.widget_texto_input.strip()
        if val:
            st.session_state.query_text = val
            st.session_state.resultado_texto = None
        else:
            st.info("Escribí qué residuo tenés para clasificarlo.")

    # Procesar la consulta activa
    query = st.session_state.query_text
    if query:
        tipo = detectar_tipo(query, KEYWORDS_DICT, AMBIGUOS_DICT)

        # Manejo de ambigüedad
        if tipo.startswith("ambiguo:"):
            termino = tipo.split(":")[1]
            info = AMBIGUOS_DICT[termino]

            st.warning(f"🤔 **\"{termino}\"** puede ser de distintos materiales.")
            st.markdown(f"**{info['pregunta']}**")

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

            tipo_final = opciones_tipos[eleccion]
            # Mostrar controles justo antes de la card
            limpio, seco, roto = renderizar_controles_estado("text")
            regla = obtener_regla(tipo_final, ClasificadorDinamico, REGLAS_DICT, limpio=limpio, seco=seco, roto=roto)
            mostrar_resultado(regla, tipo_final, limpio=limpio, seco=seco, roto=roto)

        else:
            # Mostrar controles justo antes de la card
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

    if vision_motor == "Gemini (Nube)" and not gemini_key:
        st.warning("⚠️ Ingresá tu API Key de Gemini en el panel izquierdo para usar esta función. Podés obtenerla gratis en [aistudio.google.com](https://aistudio.google.com).")
    else:
        imagen = st.file_uploader(
            "Subir imagen",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )

        if imagen:
            image_key = f"{imagen.name}_{imagen.size}"
            
            # Limpiar caché de imagen si se sube una nueva
            if st.session_state.last_image_key != image_key:
                st.session_state.last_image_key = image_key
                st.session_state.image_description = None

            col_img, col_res = st.columns([1, 1])
            with col_img:
                st.image(imagen, caption="Imagen subida", use_container_width=True)

            with col_res:
                if st.session_state.image_description is None:
                    spinner_msg = (
                        "🤖 Analizando localmente con Qwen2-VL... (La primera vez puede tardar unos minutos descargando el modelo)"
                        if vision_motor == "Hugging Face (Local - Tensores)"
                        else "🤖 Analizando con Gemini..."
                    )
                    with st.spinner(spinner_msg):
                        try:
                            image_bytes = imagen.read()
                            ext = imagen.name.split(".")[-1].lower()
                            mime = {"jpg":"image/jpeg","jpeg":"image/jpeg",
                                    "png":"image/png","webp":"image/webp"}.get(ext,"image/jpeg")

                            if vision_motor == "Hugging Face (Local - Tensores)":
                                # Llamada local con tensores
                                descripcion = analizar_imagen_local(image_bytes)
                            else:
                                # Llamada modularizada al modelo de visión
                                descripcion = analizar_imagen_con_gemini(image_bytes, mime, gemini_key)
                            
                            st.session_state.image_description = descripcion
                        except Exception as e:
                            st.error(f"Error al analizar la imagen: {e}")
                            descripcion = None

                # Si tenemos una descripción en caché o procesada recién
                if st.session_state.image_description:
                    descripcion = st.session_state.image_description
                    motor_label = "HF Local" if vision_motor == "Hugging Face (Local - Tensores)" else "Gemini"
                    st.success(f"🤖 {motor_label} identificó: **{descripcion}**")

                    tipo = detectar_tipo(descripcion, KEYWORDS_DICT, AMBIGUOS_DICT)
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



# ── TAB 3: Puntos Verdes ──────────────────────────────────────────────────────
with tab3:
    st.markdown("#### Puntos Verdes más cercanos")
    st.markdown("Ingresá tu ubicación para encontrar los centros de reciclaje más cercanos.")

    col_lat, col_lon, col_n = st.columns([2, 2, 1])

    # Valores por defecto: Plaza de Mayo, CABA
    with col_lat:
        lat = st.number_input("Latitud", value=-34.6083, format="%.4f", step=0.0001)
    with col_lon:
        lon = st.number_input("Longitud", value=-58.3712, format="%.4f", step=0.0001)
    with col_n:
        n_puntos = st.number_input("Cantidad", min_value=1, max_value=10, value=3)

    st.caption("💡 Podés obtener tus coordenadas haciendo clic derecho en Google Maps → \"¿Qué hay aquí?\"")

    if st.button("🔍 Buscar Puntos Verdes", use_container_width=True):
        with st.spinner("Buscando..."):
            puntos = puntos_cercanos(lat, lon, DF_PUNTOS_VERDES, n=n_puntos)

        if puntos:
            st.markdown(f"**{len(puntos)} Puntos Verdes más cercanos:**")

            for p in puntos:
                st.markdown(f"""
                <div class="punto-verde-card">
                    <div class="punto-verde-nombre">📌 {p['nombre']}</div>
                    <div class="punto-verde-dir">📍 {p['direccion']}</div>
                    <div class="punto-verde-dist">🚶 {p['dist_km']} km de distancia</div>
                </div>
                """, unsafe_allow_html=True)

            # Mapa con los puntos
            mapa_data = pd.DataFrame({
                "lat": [p["lat"] for p in puntos] + [lat],
                "lon": [p["lon"] for p in puntos] + [lon],
            })
            st.map(mapa_data, zoom=13)

        else:
            st.error("No se pudieron obtener los Puntos Verdes. Verificá tu conexión.")

    st.markdown("---")
    st.caption("Datos: [Portal de Datos Abiertos de CABA](https://data.buenosaires.gob.ar/dataset/puntos-verdes)")
