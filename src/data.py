import os
import re
import pandas as pd
import streamlit as st

_POINT_RE = re.compile(r"POINT\s*\(\s*([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s*\)")

# Ruta a la carpeta data, ubicada en la raíz del proyecto (un nivel arriba de src/)
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

@st.cache_data
def cargar_sistema():
    """Carga los tres CSV y construye los diccionarios del sistema."""
    # Keywords
    df_kw = pd.read_csv(os.path.join(DATA_PATH, "keywords.csv"), encoding="utf-8")
    keywords_dict = {}
    for _, row in df_kw.iterrows():
        keywords_dict.setdefault(row["tipo"], []).append(str(row["keyword"]).strip())

    # Reglas
    df_reg = pd.read_csv(os.path.join(DATA_PATH, "reglas.csv"), encoding="utf-8")
    reglas_dict = {}
    for _, row in df_reg.iterrows():
        reglas_dict[row["tipo"]] = {
            "categoria"      : row["categoria"],
            "subcategoria"   : row["subcategoria"],
            "contenedor"     : row["contenedor"],
            "instrucciones"  : [i.strip() for i in str(row["instrucciones"]).split(";") if i.strip()],
            "errores_comunes": [e.strip() for e in str(row["errores_comunes"]).split(";") if e.strip()],
            "impacto"        : row["impacto"],
            "urgencia"       : row["urgencia"],
        }

    # Ambiguos
    df_amb = pd.read_csv(os.path.join(DATA_PATH, "ambiguos.csv"), encoding="utf-8")
    ambiguos_dict = {}
    for _, row in df_amb.iterrows():
        t = row["termino"]
        if t not in ambiguos_dict:
            ambiguos_dict[t] = {"pregunta": row["pregunta"], "opciones": {}}
        ambiguos_dict[t]["opciones"][str(row["opcion_num"])] = (
            row["tipo"], row["descripcion"]
        )

    return keywords_dict, reglas_dict, ambiguos_dict


@st.cache_data
def cargar_puntos_verdes():
    """Carga el dataset de Puntos Verdes desde el archivo local."""
    local = os.path.join(DATA_PATH, "puntos_verdes.csv")
    try:
        df = pd.read_csv(local, encoding="utf-8")
    except Exception:
        return None

    # Parsear columna geometry (WKT "POINT (lon lat)") → lat / lon
    has_lat = any("lat" in c.lower() for c in df.columns)
    has_lon = any(x in c.lower() for c in df.columns for x in ("lon", "lng", "long"))
    if (not has_lat or not has_lon) and "geometry" in df.columns:
        def _parse(s):
            m = _POINT_RE.search(str(s))
            return (float(m.group(2)), float(m.group(1))) if m else (None, None)
        parsed = df["geometry"].apply(_parse)
        df["lat"] = [p[0] for p in parsed]
        df["lon"] = [p[1] for p in parsed]

    return df
