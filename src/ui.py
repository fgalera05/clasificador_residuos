import os
import streamlit as st

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

    # Mostrar la transición si el motor de inferencia reclasificó el residuo
    tipo_mostrado = tipo
    final_tipo = regla.get("_final_tipo", tipo)
    if final_tipo != tipo:
        tipo_mostrado = f"{tipo} ➔ {final_tipo}"

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
