import os
import streamlit as st

# Mapping de tipo de residuo → clave de filtro del mapa (pestaña 3)
_TIPO_A_FILTRO_MAPA = {
    # Reciclables → contenedor verde
    "plastico_pet":        "contenedor_verde",
    "plastico_bolsa":      "contenedor_verde",
    "plastico_decoracion": "contenedor_verde",
    "vidrio":              "contenedor_verde",
    "papel":               "contenedor_verde",
    "carton":              "contenedor_verde",
    "tetrabrik":           "contenedor_verde",
    "metal_lata":          "contenedor_verde",
    "aerosol":             "contenedor_verde",
    "reciclable_sucio":    "contenedor_verde",
    # Especiales → punto verde con atención
    "pila_bateria":        "con_atencion",
    "bateria_auto":        "con_atencion",
    "medicamento":         "con_atencion",
    "aceite_cocina":       "con_atencion",
    "aceite_motor":        "con_atencion",
    "electronico":         "con_atencion",
    "bombilla":            "con_atencion",
    "bombilla_led":        "con_atencion",
    "pintura_solvente":    "con_atencion",
    "ropa_textil":         "con_atencion",
    "plastico_pvc":        "con_atencion",
    "organico":            "con_atencion",
    # Basura común → contenedor negro
    "telgopor":             "contenedor_negro",
    "papel_higienico":      "contenedor_negro",
    "papel_no_reciclable":  "contenedor_negro",
    "panal":                "contenedor_negro",
    "vidrio_no_reciclable": "contenedor_negro",
    "desconocido":          "contenedor_negro",
    # escombros, madera, neumatico → sin mapa específico (recolección municipal)
}
_FILTRO_LABEL_MAPA = {
    "contenedor_verde": "Contenedores Verdes (reciclables)",
    "con_atencion":     "Puntos Verdes con Atención",
    "rsu":              "Centros de Clasificación RSU",
    "contenedor_negro": "Contenedores Negros",
}

def inyectar_estilos():
    """Lee el archivo style.css de la misma carpeta e inyecta los estilos en Streamlit."""
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning("No se pudo cargar el archivo de estilos CSS.")


def color_urgencia(urgencia: str) -> str:
    """Devuelve la clase de urgencia correspondiente para los estilos CSS."""
    u = str(urgencia).lower()
    if "alta" in u or "🔴" in u:
        return "urgencia-alta"
    if "media" in u:
        return "urgencia-media"
    return "urgencia-baja"


def tipo_tarjeta(categoria: str) -> str:
    """Devuelve la clase de estilo de tarjeta correspondiente para la categoría."""
    cat = str(categoria).lower()
    if "reciclable" in cat:
        return "card-reciclable"
    if "orgánico" in cat or "organico" in cat:
        return "card-organico"
    if "especial" in cat or "peligroso" in cat or "raee" in cat:
        return "card-especial"
    if "común" in cat or "comun" in cat:
        return "card-basura"
    return "card-basura"


def mostrar_resultado(regla: dict, tipo: str, limpio: bool = True, seco: bool = True, roto: bool = False):
    """Renderiza la card de resultado de la clasificación."""
    pasos_html = "".join([
        f'<div class="paso"><div class="paso-num">{i+1}</div><div>{p}</div></div>'
        for i, p in enumerate(regla.get("instrucciones", []))
    ])
    errores_html = "".join([
        f'<div class="error-item">{e}</div>'
        for e in regla.get("errores_comunes", [])
    ])
    clase_urg = color_urgencia(regla.get("urgencia", ""))
    clase_card = tipo_tarjeta(regla.get("categoria", ""))

    # Obtener explicación de inferencia si existe
    explicacion = regla.get("_explicacion", "")
    explicacion_html = ""
    if explicacion:
        explicacion_html = f'<div class="explicacion-box">🧠 <b>Razonamiento:</b> {explicacion}</div>'

    tipo_mostrado = tipo
    final_tipo = regla.get("_final_tipo", tipo)
    transicion_html = ""
    if final_tipo != tipo:
        tipo_mostrado = f"{tipo} ➔ {final_tipo}"
        transicion_html = f'<div style="color: #ff8a80; font-weight: bold; margin-top: 5px; font-size: 0.9rem;">⚠️ Reclasificado de <b>{tipo}</b> a <b>{final_tipo}</b> por su estado físico</div>'

    # Generar badges para el estado físico evaluado
    status_limpio = "🧼 Limpio" if limpio else "⚠️ Sucio/Grasoso"
    status_seco = "☀️ Seco" if seco else "💧 Húmedo"
    status_roto = "💥 Roto" if roto else "📦 Entero"
    
    estado_html = f"""<div class="estado-evaluado-box">
<span class="badge-estado">{status_limpio}</span>
<span class="badge-estado">{status_seco}</span>
<span class="badge-estado">{status_roto}</span>
</div>"""

    st.markdown(f"""<div class="card-resultado {clase_card}">
<div class="card-categoria">{regla.get('categoria', '—')}</div>
<div class="card-sub">{regla.get('subcategoria', '—')} · tipo: <code>{tipo_mostrado}</code></div>
{transicion_html}
{estado_html}
{explicacion_html}
<div class="card-contenedor">🗑️ {regla.get('contenedor', '—')}</div>
<span class="{ clase_urg }">⚡ Urgencia: {regla.get('urgencia', '—')}</span>
<div class="seccion-titulo">📋 Instrucciones</div>
{pasos_html}
<div class="seccion-titulo">⚠️ Errores comunes</div>
{errores_html}
<div class="impacto-box">🌍 {regla.get('impacto', '—')}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="disclaimer">
⚠️ Este sistema es orientativo y educativo. Para dudas específicas consultá en tu municipio o Punto Verde más cercano.
</div>""", unsafe_allow_html=True)

    # Link a la pestaña del mapa con filtro pre-aplicado
    _tipo_final = regla.get("_final_tipo", tipo)
    _filtro = _TIPO_A_FILTRO_MAPA.get(_tipo_final)
    if _filtro:
        _flabel = _FILTRO_LABEL_MAPA.get(_filtro, "el mapa")
        st.markdown(
            f'<a target="_self" href="?tipos={_filtro}" style="display:inline-flex;align-items:center;gap:6px;'
            f'background:#1a3a2a;color:#81c784;border:1px solid #2d5a3d;padding:8px 16px;'
            f'border-radius:8px;text-decoration:none;font-size:0.88rem;margin-top:8px;">'
            f'📍 Ver {_flabel} en el mapa →</a>',
            unsafe_allow_html=True,
        )
