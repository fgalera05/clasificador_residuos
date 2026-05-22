import os
import pandas as pd
import streamlit as st

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
    """Intenta cargar el dataset de Puntos Verdes de CABA."""
    URL = "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/ministerio-de-espacio-publico-e-higiene-urbana/puntos-verdes/puntos-verdes.csv"
    try:
        df = pd.read_csv(URL, encoding="utf-8")
        return df
    except Exception:
        # Fallback con datos de ejemplo
        return pd.DataFrame({
            "nombre": ["Punto Verde Palermo", "Punto Verde Recoleta", "Punto Verde Caballito", "Punto Verde Almagro", "Punto Verde San Telmo"],
            "direccion": ["Av. Santa Fe 3200", "Av. Las Heras 1900", "Av. Rivadavia 5000", "Av. Corrientes 3800", "Defensa 400"],
            "lat": [-34.5876, -34.5795, -34.6188, -34.6078, -34.6218],
            "long": [-58.4193, -58.3942, -58.4380, -58.4120, -58.3712],
        })
